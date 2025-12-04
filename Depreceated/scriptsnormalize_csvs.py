import pandas as pd
from pathlib import Path

base = Path("data/processed")
files = [
    "letters_extracted.csv",
    "letters_extracted_scored.csv",
    "letters_cleaned.csv",
    "consultation_letters_merged.csv",
    "consultation_letters_merged_prefixfix.csv",
    "consultation_letters_matched.csv",
    "consultation_letters_unmatched.csv",
    "master_consultation_ai_act.csv"
]

for name in files:
    path = base / name
    df = pd.read_csv(path, encoding="utf-8", sep=",", engine="python", on_bad_lines="skip")
    df.columns = [c.strip().replace("\n", " ").replace("\r", " ") for c in df.columns]
    df = df.applymap(lambda x: str(x).replace("\r", " ").replace("\n", " ").strip() if isinstance(x, str) else x)
    out = base / f"{path.stem}_normalized.csv"
    df.to_csv(out, sep=";", index=False, encoding="utf-8-sig")
    print(f"✅ Normalized {name} → {out}")
