from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
consult_path = BASE / "data" / "raw" / "consultation_2020.csv"
letters_path = BASE / "data" / "processed" / "letters_from_pdfs.csv"
out_path = BASE / "data" / "processed" / "consultation_with_letters.csv"

consult = pd.read_csv(
    consult_path,
    encoding="cp1252",
    sep=";",
    engine="python",
    dtype=str,
)

# flatten headers from EC export (they have \n)
consult.columns = [c.replace("\r", " ").replace("\n", " ").strip() for c in consult.columns]

letters = pd.read_csv(
    letters_path,
    encoding="utf-8-sig",
    sep=";",
    dtype=str,
)

letters = letters.drop_duplicates(subset=["reference"], keep="first")

merged = consult.merge(
    letters[["reference", "filename", "text", "quality", "lang_guess"]],
    left_on="Reference",
    right_on="reference",
    how="left",
)

merged = merged.drop(columns=["reference"])

merged = merged.rename(columns={
    "filename": "letter_filename",
    "text": "letter_text",
    "quality": "letter_quality",
    "lang_guess": "letter_lang_guess",
})

merged["letter_text_len"] = merged["letter_text"].fillna("").str.len()

merged.to_csv(out_path, sep=";", index=False, encoding="utf-8-sig")
print(merged.shape)
print(out_path)
