from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Warning: GOOGLE_API_KEY not found in environment variables.")


@app.get("/")
def read_root():
    return {"message": "Mamameal API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

from api.seal_utils import generate_seal_data, create_seal_excel
import base64

@app.post("/api/seal")
async def create_seal(file: UploadFile = File(...)):
    try:
        content = await file.read()
        blocks = generate_seal_data(content, api_key=api_key)
        excel_io = create_seal_excel(blocks)
        
        # Return as base64 for now (or streaming response)
        b64_str = base64.b64encode(excel_io.getvalue()).decode()
        return {
            "filename": f"{file.filename.replace('.pdf', '')}_seal.xlsx",
            "file_data": b64_str,
            "blocks": blocks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Order/Invoice Processing ---
from api.pdf_utils import (
    safe_write_df, pdf_to_excel_data_for_paste_sheet, extract_table_from_pdf_for_bento,
    find_correct_anchor_for_bento, extract_bento_range_for_bento, match_bento_data, 
    extract_detailed_client_info_from_pdf, export_detailed_client_data_to_dataframe,
    paste_dataframe_to_sheet
)
from api.master_utils import load_master_csv, save_master_file
from openpyxl import load_workbook
import io
import pandas as pd

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'api', 'assets')

@app.post("/api/order-invoice")
async def process_order(file: UploadFile = File(...)):
    try:
        pdf_bytes = await file.read()
        pdf_file = io.BytesIO(pdf_bytes)
        
        # Load Masters
        df_product_master, _ = load_master_csv(ASSETS_DIR, "商品マスタ")
        df_customer_master, _ = load_master_csv(ASSETS_DIR, "得意先マスタ")
        
        # Extract Data
        # 1. Paste Sheet
        df_paste_sheet = pdf_to_excel_data_for_paste_sheet(io.BytesIO(pdf_bytes))
        if df_paste_sheet is None:
            raise HTTPException(status_code=400, detail="Failed to extract data from PDF for paste sheet")
            
        # 2. Bento Data
        df_bento_sheet = None
        tables = extract_table_from_pdf_for_bento(io.BytesIO(pdf_bytes))
        if tables:
            main_table = max(tables, key=len)
            anchor_col = find_correct_anchor_for_bento(main_table)
            if anchor_col != -1:
                bento_list = extract_bento_range_for_bento(main_table, anchor_col)
                if bento_list:
                    matched_data = match_bento_data(bento_list, df_product_master)
                    df_bento_sheet = pd.DataFrame(matched_data, columns=['商品予定名', 'パン箱入数', '売価単価', '弁当区分'])

        # 3. Client Data
        df_client_sheet = None
        client_data = extract_detailed_client_info_from_pdf(io.BytesIO(pdf_bytes))
        if client_data:
            df_client_sheet = export_detailed_client_data_to_dataframe(client_data)

        # 4. Generate Files
        template_path = os.path.join(ASSETS_DIR, "template.xlsm")
        nouhinsyo_path = os.path.join(ASSETS_DIR, "nouhinsyo.xlsx")
        
        if not os.path.exists(template_path) or not os.path.exists(nouhinsyo_path):
             raise HTTPException(status_code=500, detail="Template files not found")

        # --- Generate Template (Shuushussho) ---
        template_wb = load_workbook(template_path, keep_vba=True)
        
        # Paste Masters
        if not df_product_master.empty and "商品マスタ" in template_wb.sheetnames:
            ws = template_wb["商品マスタ"]
            if ws.max_row > 0: ws.delete_rows(1, ws.max_row)
            paste_dataframe_to_sheet(ws, df_product_master)
            
        if not df_customer_master.empty and "得意先マスタ" in template_wb.sheetnames:
             ws = template_wb["得意先マスタ"]
             if ws.max_row > 0: ws.delete_rows(1, ws.max_row)
             paste_dataframe_to_sheet(ws, df_customer_master)

        # Write Data
        ws_paste = template_wb["貼り付け用"]
        for r_idx, row in df_paste_sheet.iterrows():
            for c_idx, value in enumerate(row):
                ws_paste.cell(row=r_idx + 1, column=c_idx + 1, value=value)
        
        if df_bento_sheet is not None and "注文弁当の抽出" in template_wb.sheetnames:
            safe_write_df(template_wb["注文弁当の抽出"], df_bento_sheet)
            
        if df_client_sheet is not None and "クライアント抽出" in template_wb.sheetnames:
            safe_write_df(template_wb["クライアント抽出"], df_client_sheet)
            
        out_template = io.BytesIO()
        template_wb.save(out_template)
        b64_template = base64.b64encode(out_template.getvalue()).decode()

        # --- Generate Nouhinsyo ---
        nouhinsyo_wb = load_workbook(nouhinsyo_path)
        
        if not df_customer_master.empty and "得意先マスタ" in nouhinsyo_wb.sheetnames:
             ws = nouhinsyo_wb["得意先マスタ"]
             if ws.max_row > 0: ws.delete_rows(1, ws.max_row)
             paste_dataframe_to_sheet(ws, df_customer_master)
             
        ws_paste_n = nouhinsyo_wb["貼り付け用"]
        for r_idx, row in df_paste_sheet.iterrows():
            for c_idx, value in enumerate(row):
                ws_paste_n.cell(row=r_idx + 1, column=c_idx + 1, value=value)
                
        # Bento for Nouhinsyo
        df_bento_for_nouhin = None
        if df_bento_sheet is not None:
             master_df = df_product_master.copy()
             if not master_df.empty and '商品名' in master_df.columns:
                 master_map = master_df.drop_duplicates(subset=['商品予定名']).set_index('商品予定名')['商品名'].to_dict()
                 df_bento_for_nouhin = df_bento_sheet.copy()
                 df_bento_for_nouhin['商品名'] = df_bento_for_nouhin['商品予定名'].map(master_map)
                 df_bento_for_nouhin = df_bento_for_nouhin[['商品予定名', 'パン箱入数', '商品名']]
        
        if df_bento_for_nouhin is not None and "注文弁当の抽出" in nouhinsyo_wb.sheetnames:
             safe_write_df(nouhinsyo_wb["注文弁当の抽出"], df_bento_for_nouhin)
        
        if df_client_sheet is not None and "クライアント抽出" in nouhinsyo_wb.sheetnames:
             safe_write_df(nouhinsyo_wb["クライアント抽出"], df_client_sheet)

        out_nouhin = io.BytesIO()
        nouhinsyo_wb.save(out_nouhin)
        b64_nouhin = base64.b64encode(out_nouhin.getvalue()).decode()
        
        return {
            "template_file": {
                "filename": f"{file.filename.replace('.pdf', '')}_数出表.xlsm",
                "data": b64_template
            },
            "nouhinsyo_file": {
                "filename": f"{file.filename.replace('.pdf', '')}_納品書.xlsx",
                "data": b64_nouhin
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/masters/upload")
async def upload_master(file: UploadFile = File(...), type: str = "product"):
    try:
        content = await file.read()
        file_pattern = "商品マスタ" if type == "product" else "得意先マスタ"
        if type not in ["product", "customer"]:
             raise HTTPException(status_code=400, detail="Invalid type. Use 'product' or 'customer'.")
        
        # Check filename requirement (from original code)
        if type == "product" and "商品マスタ一覧" not in file.filename:
             raise HTTPException(status_code=400, detail="Filename must contain '商品マスタ一覧'")
        if type == "customer" and "得意先マスタ一覧" not in file.filename:
             raise HTTPException(status_code=400, detail="Filename must contain '得意先マスタ一覧'")

        success = save_master_file(ASSETS_DIR, content, file.filename, file_pattern)
        if success:
            return {"message": "File saved successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
