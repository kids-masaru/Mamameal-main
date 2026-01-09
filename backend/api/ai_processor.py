from google import genai
from google.genai import types
import json
import pdfplumber
import io
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extracts all text from a PDF file using pdfplumber.
    """
    all_text = ""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n"
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        return ""
    return all_text

def process_order_pdf_with_ai(pdf_bytes: bytes, api_key: str, model_name: str = "gemini-2.0-flash") -> dict:
    """
    Processes an Order PDF (Nouhinsyo source) using Gemini to extract structured data.
    Returns a dict with 'clients' and 'bentos' keys.
    """
    if not api_key:
        raise ValueError("API Key is missing.")

    client = genai.Client(api_key=api_key)

    prompt = """
    You are an expert data extraction assistant.
    Analyze this PDF (Delivery Slip / Order Sheet) and extract the following information into a structured JSON format.

    **Goal:** Extract client orders and bento (meal) details.

    **Required JSON Structure:**
    {
      "clients": [
        {
          "client_name": "Name of the kindergarten/school (e.g., XX幼稚園, XX小学校)",
          "client_id": "Client ID if visible (e.g., 10001), else null",
          "orders": [
            {
              "type": "student", // "student" (園児) or "teacher" (先生/職員)
              "count": 12 // integer
            }
          ]
        }
      ],
      "bentos": [
        {
            "name": "Name of the bento/item (e.g., 普通食, 調整食, etc.)",
            "count": 5
        }
      ]
    }

    **Rules:**
    - "Client Name" is usually a facility name ending in 園 or 学校.
    - "Orders" are counts of meals. Sometimes separated by Student (園児) and Teacher (先生/職員).
    - If there is a table listing Bento types (e.g., ご飯あり, おかずのみ), extract them into "bentos".
    - Ignore page numbers or footer text.
    - Normalize numbers (convert full-width to half-width).
    - If a count is written like "35+1", calculate the sum (36).
    
    Return ONLY valid JSON.
    """

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                        types.Part.from_text(text=prompt)
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                max_output_tokens=65536
            )
        )
        
        text = response.text.strip()
        # Robust JSON extraction
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            # Fallback regex
            import re
            match = re.search(r'(\{.*\})', text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(1))
            else:
                 raise ValueError("No JSON found in AI response")
                 
        return parsed

    except Exception as e:
        logger.error(f"AI Processing failed: {e}")
        raise e
