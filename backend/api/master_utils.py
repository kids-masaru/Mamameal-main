import os
import glob
import pandas as pd

def load_master_csv(base_path, file_pattern):
    """Load master CSV from assets directory."""
    search_path = os.path.join(base_path, f'*{file_pattern}*.csv')
    list_of_files = glob.glob(search_path)
    if not list_of_files:
        return pd.DataFrame(), None
    latest_file = max(list_of_files, key=os.path.getmtime)
    encodings = ['utf-8-sig', 'utf-8', 'cp932', 'shift_jis']
    for encoding in encodings:
        try:
            df = pd.read_csv(latest_file, encoding=encoding, dtype=str).fillna('')
            if not df.empty:
                df.columns = df.columns.str.strip()
                return df, os.path.basename(latest_file)
        except Exception:
            continue
    return pd.DataFrame(), None

def save_master_file(base_path, file_content, filename, file_pattern):
    """Save uploaded master file to assets directory, removing old ones."""
    # 1. Delete existing files matching the pattern
    search_path = os.path.join(base_path, f'*{file_pattern}*.csv')
    old_files = glob.glob(search_path)
    for f in old_files:
        try:
            os.remove(f)
        except Exception as e:
            print(f"Error removing old file: {e}")
            return False

    # 2. Save new file
    save_path = os.path.join(base_path, filename)
    try:
        with open(save_path, "wb") as f:
            f.write(file_content)
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False
