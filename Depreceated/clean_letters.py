import pandas as pd
import re
from pathlib import Path

src = r"data/processed/letters_extracted.csv"
df = pd.read_csv(src)
print(f"Loaded {len(df)} letters")

df["text_len"] = df["text"].fillna("").str.len()
df["quality_flag"] = pd.cut(
    df["text_len"],
    bins=[-1, 200, 2000, 1_000_000],
    labels=["bad_or_scan", "ok_short", "good_long"]
)

def basic_clean(txt):
    if not isinstance(txt, str):
        return ""
    txt = re.sub(r"\n\s*\n+", "\n\n", txt)
    txt = re.sub(r"^Ref\.? ?Ares.*\n", "", txt, flags=re.MULTILINE)
    txt = re.sub(r" +", " ", txt)
    return txt.strip()

df["text_clean"] = df["text"].apply(basic_clean)

out_dir = Path("data/processed")
out_dir.mkdir(parents=True, exist_ok=True)

df.to_csv(out_dir / "letters_extracted_scored.csv", index=False)
df.to_csv(out_dir / "letters_cleaned.csv", index=False)

print("✅ Cleaning complete")
print(df["quality_flag"].value_counts())
