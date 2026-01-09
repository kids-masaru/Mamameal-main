import pandas as pd
import os

assets_dir = r"backend/api/assets"
csv_file = "商品マスタ一覧2025.12.3.csv"
path = os.path.join(assets_dir, csv_file)

try:
    df = pd.read_csv(path, encoding='cp932')
    print("Columns:", df.columns.tolist())
    print("\n--- Search Results for 'キャラ' ---")
    # Assuming Name is Col D (Index 3, but let's check names)
    # The header printed previously: 商品ＣＤ,商品区分,商品名,商品予定名,...
    # So '商品予定名' matches user description.
    target_col = '商品予定名'
    
    if target_col in df.columns:
        res = df[df[target_col].astype(str).str.contains("キャラ", na=False)]
        print(res[target_col].tolist())
        
        print("\n--- Search Results for '赤' ---")
        res2 = df[df[target_col].astype(str).str.contains("赤", na=False)]
        print(res2[target_col].tolist())
    else:
        print(f"Column {target_col} not found. Available: {df.columns}")

except Exception as e:
    print(e)
