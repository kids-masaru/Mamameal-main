from google import genai
from google.genai import types
import json
import pdfplumber
import io
import logging
import re

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

    **Goal:** 
    1. Extract the LIST of Bento Types (Columns) from the header table.
    2. Extract client orders for these bentos.

    **Structure of the Header:**
    - The table header defines the specific bentos.
    - Some headers are merged. e.g. Top: "キャラ弁(学食)", Sub: "飯あり 100", "飯あり 150".
    - You must flattened these into unique names: "キャラ弁(学食) 飯あり 100", "キャラ弁(学食) 飯あり 150".
    - Expected "Fixed" Order at start (Left->Right):
      1. キャラ弁(学食) 飯あり 100
      2. キャラ弁(学食) 飯あり 150
      3. キャラ弁 飯あり 120
      4. キャラ弁 おにぎり(三角)
      5. キャラ弁 飯なし
      6. 赤 飯あり 120
      7. 赤 飯あり 100
      8. 赤 おにぎり(三角)
      9. 赤 飯なし
    - **Variable Section**: After "Red" (赤) group, there are variable bentos (e.g., "キャラパン", "クリスマスカレー"). Extract them exactly as written.

    **Required JSON Structure:**
    {
      "bento_headers": [
        "String representation of column 1 (e.g. キャラ弁(学食) 飯あり 100)",
        "String representation of column 2",
        ...
      ],
      "clients": [
        {
          "client_name": "Name of the kindergarten/school",
          "client_id": "Client ID (10001, etc) or null",
          "orders": [
             // List of counts corresponding to the bento_headers order, OR explicit mapping
             { "bento_name": "Matches one of bento_headers", "count": 12, "type": "student" },
             { "bento_name": "Matches one of bento_headers", "count": 2, "type": "teacher" }
          ]
        }
      ]
    }

    **Rules:**
    - "Client Name" ends in 園 or 学校.
    - "Orders": Extract the numerical counts for each bento column.
    - If a cell is empty or "-", count is 0.
    - Use half-width numbers.
    - If "35+1", sum it to 36.
    
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
