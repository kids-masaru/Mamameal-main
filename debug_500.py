import sys
import os
import io
import pandas as pd
from dotenv import load_dotenv

# Path setup
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
from api.pdf_utils import extract_detailed_client_info_from_pdf, safe_write_df

# Mock data to simulate main.py flow
def debug_client_processing():
    try:
        print("1. Loading PDF...")
        # Load a real PDF to ensure extract_detailed works
        pdf_path = "api/assets/pdf/25.11.11【ママミール】.pdf"
        if not os.path.exists(pdf_path):
             # Try absolute
             pdf_path = r"c:\Users\HP\OneDrive\ドキュメント\mamameal\Mamameal\api\assets\pdf\25.11.11【ママミール】.pdf"
        
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            
        print("2. extracting legacy info...")
        client_data_legacy = extract_detailed_client_info_from_pdf(io.BytesIO(pdf_bytes))
        print(f"   Extracted {len(client_data_legacy)} clients")

        print("3. Building Rows...")
        client_rows = []
        for info in client_data_legacy:
            s_list = info.get('student_meals', [])
            t_list = info.get('teacher_meals', [])
            
            def get_val(lst, idx):
                return lst[idx] if idx < len(lst) else ''
            
            s1, s2, s3 = get_val(s_list, 0), get_val(s_list, 1), get_val(s_list, 2)
            t1, t2, t3 = get_val(t_list, 0), get_val(t_list, 1), get_val(t_list, 2)
            
            client_rows.append({
                'クライアント名': info['client_name'],
                '園児の給食の数1': s1,
                '園児の給食の数2': s2,
                '園児の給食の数3': s3,
                '先生の給食の数1': t1,
                '先生の給食の数2': t2,
                '先生の給食の数3': t3
            })
            
        print("4. Creating DataFrame...")
        df_client_sheet = pd.DataFrame(client_rows)
        print(df_client_sheet.head())

        print("5. Rename Logic (AI Simulation)...")
        bento_header_names = ["Charaben", "Red", "Plain"] # Simulating AI
        
        if bento_header_names:
            rename_map = {}
            for i in range(3):
                if i < len(bento_header_names):
                    b_name = bento_header_names[i]
                    old_s = f'園児の給食の数{i+1}'
                    new_s = f'{b_name}\n(園児)'
                    rename_map[old_s] = new_s
                    
                    old_t = f'先生の給食の数{i+1}'
                    new_t = f'{b_name}\n(先生)'
                    rename_map[old_t] = new_t
            
            print(f"   Map: {rename_map}")
            df_client_sheet.rename(columns=rename_map, inplace=True)
            print("   Rename Success.")
            print(df_client_sheet.columns)
            
        print("6. Safe Write DF Simulation...")
        # Mock worksheet
        class MockCell:
            def __init__(self): self.value = None
        class MockWS:
            def __init__(self): 
                self.max_row = 10
                self.cells = {}
            def cell(self, row, column, value=None):
                k = (row, column)
                if k not in self.cells: self.cells[k] = MockCell()
                if value is not None: self.cells[k].value = value
                return self.cells[k]
        
        ws = MockWS()
        safe_write_df(ws, df_client_sheet)
        print("   Write Success.")

    except Exception as e:
        print(f"\nCRASHED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_client_processing()
