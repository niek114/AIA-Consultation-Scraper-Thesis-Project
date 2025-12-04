import pandas as pd

consult = pd.read_csv(
    r"data/raw/consultation_2020.csv",
    encoding="cp1252",
    sep=";",
    engine="python",
    on_bad_lines="skip"
)
matched_letters = pd.read_csv(
    r"data/processed/consultation_letters_merged_prefixfix.csv"
)

matched_letters = matched_letters.drop_duplicates(subset=["Reference"], keep="first")

upload_col = 'You can upload a document here:\n\n'
consult["upload"] = consult[upload_col].astype(str).str.strip()
consult["upload_filename"] = consult["upload"].str.extract(r"([^/\\]+\.pdf)", expand=False)

matched_letters = matched_letters.rename(columns={
    "text_clean": "letter_text",
    "quality_flag": "letter_quality",
    "filename_csv": "letter_filename_csv",
    "filename_stripped": "letter_filename_disk"
})

master = pd.merge(
    consult,
    matched_letters[["Reference", "letter_text", "letter_quality", "letter_filename_csv", "letter_filename_disk"]],
    on="Reference",
    how="left"
)

out_path = r"data/processed/master_consultation_ai_act.csv"
master.to_csv(out_path, index=False)
print(f"✅ Master dataset built: {master.shape}")
