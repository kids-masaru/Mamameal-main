import pdfplumber
import os

pdf_path = None
# Find the sample PDF
pdf_dir = r"api/assets/pdf"
if os.path.exists(pdf_dir):
    files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
    if files:
        pdf_path = os.path.join(pdf_dir, files[0])

if not pdf_path:
    print("No PDF found.")
    exit()

print(f"Inspecting {pdf_path}")

try:
    with pdfplumber.open(pdf_path) as pdf:
        p0 = pdf.pages[0]
        # Try default lines extraction
        table = p0.extract_table({
            "vertical_strategy": "lines", 
            "horizontal_strategy": "lines",
            "intersection_y_tolerance": 5
        })
        
        if not table:
            print("No table found with strategy 'lines'.")
            exit()
            
        print(f"Extracted {len(table)} rows.")
        
        # Print first few rows to see structure
        for i, row in enumerate(table[:10]):
            clean_row = [str(c).replace('\n', '|') if c else "" for c in row]
            print(f"Row {i}: {clean_row}")

        print("\n--- Scanning for 'Thinking Kids' ---")
        for i, row in enumerate(table):
            row_str = "".join(str(c) for c in row if c)
            if "シンキング" in row_str or "Thinking" in row_str or "18600" in row_str:
                 clean_row = [str(c).replace('\n', '|') if c else "[]" for c in row]
                 print(f"Found at Row {i}: {clean_row}")

except Exception as e:
    print(e)
