import os
import sys
from dotenv import load_dotenv

# Add backend to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from api.ai_processor import process_order_pdf_with_ai
from api.table_extractor import extract_client_table

# Load env from backend/.env
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', '.env')
load_dotenv(env_path)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in backend/.env")
    # Try loading from parent .env if exists
    parent_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(parent_env):
        print(f"Loading from parent .env: {parent_env}")
        load_dotenv(parent_env)
        api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("CRITICAL: No API Key found.")
    sys.exit(1)

# Path to PDF (in root api/assets/pdf)
pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api', 'assets', 'pdf', '25.11.11【ママミール】.pdf')

print(f"Testing with file: {pdf_path}")
if not os.path.exists(pdf_path):
    print("File not found!")
    # Look for any pdf
    pdf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api', 'assets', 'pdf')
    if os.path.exists(pdf_dir):
        files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        if files:
            pdf_path = os.path.join(pdf_dir, files[0])
            print(f"Found alternative: {pdf_path}")
        else:
            sys.exit(1)
    else:
        sys.exit(1)

with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

print("Sending to AI...")
try:
    result = process_order_pdf_with_ai(pdf_bytes, api_key)
    print("\n--- AI Result ---")
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n--- Rule-Based Client Extraction ---")
    grid = extract_client_table(pdf_bytes)
    print(f"Extracted {len(grid)} clients.")
    # Print first few
    print(json.dumps(grid[:5], indent=2, ensure_ascii=False))

    print("\nSuccess!")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
