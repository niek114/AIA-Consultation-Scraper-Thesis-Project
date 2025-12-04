import pandas as pd

consult = pd.read_csv(
    r"data/raw/consultation_2020.csv",
    encoding="cp1252",
    sep=";",
    engine="python",
    on_bad_lines="skip"
)
letters = pd.read_csv(r"data/processed/letters_cleaned.csv")

upload_col = 'You can upload a document here:\n\n'
consult["upload"] = consult[upload_col].astype(str).str.strip()
consult = consult[consult["upload"].str.len() > 4][["Reference", "upload"]]
consult["filename_csv"] = consult["upload"].str.extract(r"([^/\\]+\.pdf)", expand=False)

letters["filename_disk"] = letters["filename"]
letters["filename_stripped"] = letters["filename_disk"].str.split("-", n=1).str[-1]

consult["filename_csv_clean"] = consult["filename_csv"].str.lower()
letters["filename_stripped_clean"] = letters["filename_stripped"].str.lower()

merged = pd.merge(
    consult,
    letters,
    left_on="filename_csv_clean",
    right_on="filename_stripped_clean",
    how="left"
)

match_rate = merged["text_clean"].notna().mean() * 100
print(f"Match rate: {match_rate:.1f}% ({merged['text_clean'].notna().sum()}/{len(merged)})")

out_path = r"data/processed/consultation_letters_merged_prefixfix.csv"
merged.to_csv(out_path, index=False)
print(f"Saved to {out_path}")
