import argparse
from pathlib import Path

import pandas as pd


def build_atlasti(input_path: Path, output_path: Path) -> None:
    """Build Atlas.ti-style codebook and quotation sheets.

    Expects an Excel workbook with at least the following sheets:

    - article_level_sections
    - code_occurrences
    - GT_codebook_open
    - GT_axial_themes_summary
    - GT_categories_summary
    - GT_core_themes_summary
    - GT_top_codes_by_theme
    - GT_selective_core_codebook
    - GT_selective_core_occurrences
    - GT_selective_core_summary
    - GT_axial_theme_cooccurrence
    - GT_selective_core_cooccurrence
    - GT_theme_code_evolution_summary
    - GT_theme_code_evolution
    """
    xls = pd.read_excel(input_path, sheet_name=None)

    # Unpack core sheets
    article_df = xls["article_level_sections"].copy()
    codes_long = xls["code_occurrences"].copy()
    codebook_df = xls["GT_codebook_open"].copy()
    axial_summary = xls["GT_axial_themes_summary"].copy()
    cat_summary = xls["GT_categories_summary"].copy()
    core_themes_summary = xls["GT_core_themes_summary"].copy()
    top_codes_by_theme = xls["GT_top_codes_by_theme"].copy()
    selective_core_codebook = xls["GT_selective_core_codebook"].copy()
    selective_core_occurrences = xls["GT_selective_core_occurrences"].copy()
    selective_core_summary = xls["GT_selective_core_summary"].copy()
    axial_cooc = xls["GT_axial_theme_cooccurrence"].copy()
    core_cooc = xls["GT_selective_core_cooccurrence"].copy()
    theme_code_evolution_summary = xls["GT_theme_code_evolution_summary"].copy()
    theme_code_evolution = xls["GT_theme_code_evolution"].copy()

    # Build Atlas.ti-style codebook
    atlas_codebook = codebook_df.rename(columns={
        "open_code": "CodeName",
        "gt_category": "GT_Category",
        "axial_theme": "Axial_Theme",
    }).copy()

    # Merge evolution info: per code, whether it appears in each version and origin pattern
    evo_info = theme_code_evolution[[
        "open_code",
        "proposal_2021",
        "ep_position_2024",
        "final_oj_2024",
        "code_origin_pattern",
    ]].drop_duplicates("open_code")
    evo_info = evo_info.rename(columns={"open_code": "CodeName"})
    atlas_codebook = atlas_codebook.merge(evo_info, on="CodeName", how="left");

    # Add empty comment column for human notes in Atlas.ti
    atlas_codebook["Code_Comment"] = ""

    # Select main columns (adjust if your GT_codebook_open has different column names)
    atlas_codebook_subset = atlas_codebook[[
        "CodeName",
        "GT_Category",
        "Axial_Theme",
        "Code_Comment",
        "n_occurrences",
        "n_articles",
        "n_sources",
        "proposal_2021",
        "ep_position_2024",
        "final_oj_2024",
        "code_origin_pattern",
        "is_selective_core",
        "selective_core_bucket",
    ]]

    # Build Atlas.ti-style quotations directly from code_occurrences
    # Assumes code_occurrences already has paragraph_text and GT fields
    atlas_quotations = codes_long.rename(columns={
        "open_code": "CodeName",
        "gt_category": "GT_Category",
        "axial_theme": "Axial_Theme",
    })[[
        "source",
        "article_number",
        "section_label",
        "paragraph_id",
        "CodeName",
        "GT_Category",
        "Axial_Theme",
        "paragraph_text",
    ]].rename(columns={"paragraph_text": "Quotation_Text"})

    # Write out: keep all original sheets, add two new ones
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        # Original sheets (keep any extras as well)
        for name, df in xls.items():
            df.to_excel(writer, sheet_name=name, index=False)

        # New derived sheets
        atlas_codebook_subset.to_excel(writer, sheet_name="AtlasTI_codebook", index=False)
        atlas_quotations.to_excel(writer, sheet_name="AtlasTI_quotations", index=False)


def build_profiles(input_path: Path, output_path: Path) -> None:
    """Build axial-theme and core-bucket profile sheets.

    Expects an Excel workbook with at least:

    - GT_codebook_open
    - GT_selective_core_codebook

    and any other sheets you want to preserve.
    """
    xls = pd.read_excel(input_path, sheet_name=None)

    codebook_df = xls["GT_codebook_open"].copy()
    selective_core_codebook = xls["GT_selective_core_codebook"].copy()

    # Axial theme profile: one row per axial_theme
    rows = []
    for theme, sub in codebook_df.groupby("axial_theme"):
        cats = sorted(sub["gt_category"].dropna().unique().tolist())
        top_codes = (
            sub.sort_values("n_occurrences", ascending=False)
               .head(5)["open_code"].tolist()
        )
        rows.append({
            "axial_theme": theme,
            "n_codes_in_theme": sub["open_code"].nunique(),
            "n_code_occurrences_in_theme": sub["n_occurrences"].sum(),
            "n_sources_with_theme": sub["n_sources"].astype(int).gt(0).sum(),
            "gt_categories_in_theme": "; ".join(cats),
            "top5_codes_in_theme": "; ".join(top_codes),
        })

    axial_theme_profile = (
        pd.DataFrame(rows)
        .sort_values("axial_theme")
        .reset_index(drop=True)
    )

    # Core-bucket profile: one row per selective_core_bucket
    rows_b = []
    for bucket, sub in selective_core_codebook.groupby("selective_core_bucket"):
        cats = sorted(sub["gt_category"].dropna().unique().tolist())
        themes = sorted(sub["axial_theme"].dropna().unique().tolist())
        top_codes_b = (
            sub.sort_values("n_occurrences", ascending=False)
               .head(10)["open_code"].tolist()
        )
        rows_b.append({
            "selective_core_bucket": bucket,
            "n_core_codes_in_bucket": sub["open_code"].nunique(),
            "n_core_code_occurrences_in_bucket": sub["n_occurrences"].sum(),
            "axial_themes_in_bucket": "; ".join(themes),
            "gt_categories_in_bucket": "; ".join(cats),
            "top10_core_codes_in_bucket": "; ".join(top_codes_b),
        })

    core_bucket_profile = (
        pd.DataFrame(rows_b)
        .sort_values("selective_core_bucket")
        .reset_index(drop=True)
    )

    # Write all original sheets + profiles
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        for name, df in xls.items():
            df.to_excel(writer, sheet_name=name, index=False)

        axial_theme_profile.to_excel(writer, sheet_name="GT_axial_theme_profile", index=False)
        core_bucket_profile.to_excel(writer, sheet_name="GT_core_bucket_profile", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Act GT post-coding pipeline (Atlas.ti exports and profiles)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # build-atlasti
    p_atlasti = subparsers.add_parser(
        "build-atlasti",
        help="Build Atlas.ti codebook and quotations sheets from GT workbook"
    )
    p_atlasti.add_argument("--input", type=Path, required=True, help="Input Excel file (GT v3-style)")
    p_atlasti.add_argument("--output", type=Path, required=True, help="Output Excel file with Atlas.ti sheets (v4-style)")

    # build-profiles
    p_profiles = subparsers.add_parser(
        "build-profiles",
        help="Build axial theme and core bucket profile sheets"
    )
    p_profiles.add_argument("--input", type=Path, required=True, help="Input Excel file (GT v4-style)")
    p_profiles.add_argument("--output", type=Path, required=True, help="Output Excel file with profile sheets (v5-style)")

    args = parser.parse_args()

    if args.command == "build-atlasti":
        build_atlasti(args.input, args.output)
    elif args.command == "build-profiles":
        build_profiles(args.input, args.output)
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
