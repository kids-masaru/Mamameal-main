import pdfplumber
import io
import re

def extract_client_table(pdf_bytes):
    """
    Extracts client order counts from the distinct table grid.
    Returns a list of clients:
    [
      {
        "client_name": "...",
        "counts": [
           {"student": 10, "teacher": 5}, # Column 1
           {"student": 0, "teacher": 0},  # Column 2
           ...
        ]
      },
      ...
    ]
    """
    clients = []
    
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        if not pdf.pages:
            return []
            
        page = pdf.pages[0]
        # Use simple line strategy for the grid
        table = page.extract_table({
            "vertical_strategy": "lines", 
            "horizontal_strategy": "lines",
            "intersection_y_tolerance": 5,
        })
        
        if not table:
            return []

        # Find Header Row to know where data starts
        start_row_idx = -1
        for i, row in enumerate(table):
            # Check for "園名" or "Client" indicator
            # Row usually contains: [ '園名', 'キャラ弁...', ... ]
            row_text = "".join(str(c) for c in row if c)
            if "園名" in row_text:
                start_row_idx = i
                break
        
        if start_row_idx == -1:
            # Fallback: look for first row with ID/Name pattern? 
            # Or just skip 2 rows? Safer to search.
            # If fail, try extracting from row 3 (guess).
            start_row_idx = 2 

        # Scan Data
        current_client = None
        
        for i in range(start_row_idx + 1, len(table)):
            row = table[i]
            if not row: continue
            
            # Col 0: ID and Name
            # Format: "1001\nMyClient" or "MyClient"
            raw_name_cell = str(row[0]) if row[0] else ""
            
            # Clean up Name
            # Remove digits at start? "5100\nName"
            # Or just keep it as is, cleaning closer to Excel if needed.
            # User wants "Name".
            # Split by newline
            parts = raw_name_cell.split('\n')
            
            # Logic to find Name vs ID
            # Usually ID is digits, Name is text.
            client_name = ""
            for p in parts:
                if not p.strip().isdigit():
                    client_name = p.strip()
            
            if not client_name:
                # If no name found (maybe just ID?), ignore or merge?
                # If row is totally empty, skip
                if not any(row): continue
                # Could be a continuation row? For now assume 1 row per client.
                continue

            # Process Counts (Col 1 onwards)
            count_data = [] # List of {student: x, teacher: y}
            
            # Careful: Grid might have fixed columns. 
            # We assume Col 1 corresponds to Bento Header 1.
            for cell_val in row[1:]:
                s_count, t_count = parse_cell_counts(cell_val)
                count_data.append({"student": s_count, "teacher": t_count})
            
            clients.append({
                "client_name": client_name,
                "counts": count_data
            })
            
    return clients

def parse_cell_counts(cell_text):
    """
    "111" -> s=111, t=0
    "111\n54" -> s=111, t=54
    "" -> s=0, t=0
    """
    if not cell_text:
        return 0, 0
    
    # Normalize
    text = str(cell_text).strip()
    if not text:
        return 0, 0
        
    lines = text.split('\n')
    lines = [l.strip() for l in lines if l.strip()]
    
    if not lines:
        return 0, 0
    
    def to_int(v):
        try:
            # Handle "35+1" -> 36
            if '+' in v:
                subparts = v.split('+')
                return sum(int(sp) for sp in subparts if sp.strip().isdigit())
            return int(v)
        except:
            return 0

    if len(lines) == 1:
        # Single value -> Student
        return to_int(lines[0]), 0
    elif len(lines) >= 2:
        # Top -> Student, Bottom -> Teacher
        return to_int(lines[0]), to_int(lines[1])
    
    return 0, 0
