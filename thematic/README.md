# AI Act GT Coding Pipeline

This repository contains Python scripts to reproduce the main post-coding
processing steps used in the thesis for the EU AI Act Grounded-Theory (GT)
and thematic analysis pipeline.

The code assumes you already have an Excel workbook produced from earlier
(open) coding rounds, with the following sheets (as used in the project):

- `article_level_sections`
- `code_occurrences`
- `GT_codebook_open`
- `GT_axial_themes_summary`
- `GT_categories_summary`
- `GT_core_themes_summary`
- `GT_top_codes_by_theme`
- `GT_selective_core_codebook`
- `GT_selective_core_occurrences`
- `GT_selective_core_summary`
- `GT_axial_theme_cooccurrence`
- `GT_selective_core_cooccurrence`
- `GT_theme_code_evolution_summary`
- `GT_theme_code_evolution`

Two main steps are implemented:

1. **Atlas.ti export builder**: creates an Excel file with two additional
   sheets:
   - `AtlasTI_codebook`: one row per open code with GT category, axial theme,
     evolution flags and core-bucket status.
   - `AtlasTI_quotations`: one row per code occurrence with paragraph text and
     metadata (source, article, section, paragraph ID).

2. **Theme/core profile builder**: adds high-level profiles of axial themes
   and selective core buckets:
   - `GT_axial_theme_profile`
   - `GT_core_bucket_profile`

## Usage

Make sure you have Python 3.9+ and install dependencies:

```bash
pip install -r requirements.txt
```

Then run the pipeline on your GT workbook:

```bash
# Build Atlas.ti exports from a v3-style workbook
python ai_act_gt_pipeline.py build-atlasti \
    --input ai_act_GT_open_coding_GT_v3.xlsx \
    --output ai_act_GT_open_coding_GT_v4.xlsx

# Build axial/core profiles from a v4-style workbook
python ai_act_gt_pipeline.py build-profiles \
    --input ai_act_GT_open_coding_GT_v4.xlsx \
    --output ai_act_GT_open_coding_GT_v5.xlsx
```

You can adjust the input/output filenames as needed. The scripts will copy
all existing sheets and only add the new derived sheets.
