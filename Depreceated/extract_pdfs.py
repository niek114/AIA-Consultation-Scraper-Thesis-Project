import os
import pandas as pd
from pdfminer.high_level import extract_text
from langdetect import detect

RAW_DIR = "data/raw/letters_2020"
rows = []

for fname in os.listdir(RAW_DIR):
    if not fname.lower().endswith(".pdf"):
        continue
    fpath = os.path.join(RAW_DIR, fname)
    try:
        text = extract_text(fpath)
        lang = detect(text[:500]) if len(text) > 500 else "unknown"
        rows.append({
            "filename": fname,
            "text": text,
            "language": lang
        })
    except Exception as e:
        rows.append({
            "filename": fname,
            "text": "",
            "language": "error"
        })

os.makedirs("data/processed", exist_ok=True)
pd.DataFrame(rows).to_csv("data/processed/letters_extracted.csv", index=False)
print("Done. Extracted", len(rows), "PDFs.")
