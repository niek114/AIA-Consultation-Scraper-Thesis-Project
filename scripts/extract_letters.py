import os
from pathlib import Path
import re

import pandas as pd
from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
import pytesseract

# make sure poppler + tesseract are found on Windows
os.environ["PATH"] += os.pathsep + r"C:\poppler\Library\bin"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

BASE = Path(__file__).resolve().parent.parent
consult_path = BASE / "data" / "raw" / "consultation_2020.csv"
pdf_dir = BASE / "data" / "raw" / "letters_2020"
out_path = BASE / "data" / "processed" / "letters_from_pdfs.csv"

consult = pd.read_csv(
    consult_path,
    encoding="cp1252",
    sep=";",
    engine="python",
    dtype=str,
)

lang_map = {
    "English": "eng",
    "German": "deu",
    "French": "fra",
    "Spanish": "spa",
    "Italian": "ita",
    "Dutch": "nld",
    "Polish": "pol",
    "Portuguese": "por",
}

rows = []

for pdf_file in sorted(pdf_dir.glob("*.pdf")):
    fname = pdf_file.name
    ref = fname.split("-", 1)[0]

    row = consult.loc[consult["Reference"] == ref]
    cons_lang = (row.iloc[0]["Language"] or "").strip() if not row.empty else ""
    lang = lang_map.get(cons_lang, "eng")

    text = ""
    try:
        text = extract_text(str(pdf_file)) or ""
    except Exception as e:
        print(f"[WARN] pdfminer failed for {fname}: {e}")

    text = text.strip()

    if len(text) < 800:
        try:
            images = convert_from_path(str(pdf_file))
            ocr_parts = []
            for img in images:
                ocr_parts.append(pytesseract.image_to_string(img, lang=lang))
            text = "\n".join(ocr_parts).strip()
        except Exception as e:
            print(f"[WARN] OCR failed for {fname}: {e}")

    # sanitize for ; CSV and for Excel
    text_clean = (
        text.replace(";", " ")
            .replace("\r", " ")
            .replace("\n", " ")
            .replace('"', "'")
    )
    text_clean = re.sub(r"\s+", " ", text_clean).strip()

    quality = "good" if len(text_clean) >= 800 else "low"

    rows.append({
        "reference": ref,
        "filename": fname,
        "text": text_clean,
        "quality": quality,
        "lang_guess": lang,
    })

out_df = pd.DataFrame(rows)
out_df = out_df.drop_duplicates(subset=["reference"], keep="first")
out_df.to_csv(out_path, sep=";", index=False, encoding="utf-8-sig")
print(f"wrote {len(out_df)} rows to {out_path}")
