---
name: audit-yue-review-dual
description: Use when auditing Cantonese datasets across yue-Hans review, yue-Hant review, and final yue-Hans versus simplified yue-Hant outputs in one combined table, including OCR and SRT pipelines.
---

# Audit Yue Review Dual

Use this workflow when a Yue dataset needs one table that shows:

- what yue-Hans block review changed
- what yue-Hant block review changed
- what still differs between final yue-Hans and final simplified yue-Hant

This is useful when review decisions should be checked across both scripts at
the same subtitle number.

Important:

- Never edit files under `test/data/<dataset>/input/`.
- Do not edit source `.srt` or reviewed `.srt` fixture files directly.
- Only edit review JSON files and regenerate reviewed outputs from them.

## Inputs

For OCR datasets, use:

- `test/data/<dataset>/output/yue-Hans_ocr/fuse_clean_validate.srt`
- `test/data/<dataset>/output/yue-Hans_ocr/fuse_clean_validate_review.srt`
- `test/data/<dataset>/output/yue-Hans_ocr/fuse_clean_validate_review_flatten.srt`
- `test/data/<dataset>/output/yue-Hant_ocr/fuse_clean_validate.srt`
- `test/data/<dataset>/output/yue-Hant_ocr/fuse_clean_validate_review.srt`
- `test/data/<dataset>/output/yue-Hant_ocr/fuse_clean_validate_review_flatten_simplify_review.srt`

For SRT datasets, the review step happens before
timewarping:

- yue-Hans source: `test/data/<dataset>/input/yue-Hans.srt`
- yue-Hans review: `test/data/<dataset>/output/yue-Hans/clean_review.srt`
- final yue-Hans: `test/data/<dataset>/output/yue-Hans/clean_review_flatten_timewarp.srt`
- yue-Hant source: `test/data/<dataset>/input/yue-Hant.srt`
- yue-Hant review: `test/data/<dataset>/output/yue-Hant/clean_review.srt`
- final simplified yue-Hant: `test/data/<dataset>/output/yue-Hant/clean_review_flatten_timewarp_simplify_review.srt`

Edit these review JSON files (and only these) when applying corrections:

- OCR datasets:
  - `test/data/<dataset>/output/yue-Hans_ocr/lang/yue/block_review.json`
  - `test/data/<dataset>/output/yue-Hant_ocr/lang/yue/block_review.json`
  - `test/data/<dataset>/output/yue-Hant_ocr/lang/yue/simplify_block_review.json`
- SRT datasets:
  - `test/data/<dataset>/output/yue-Hans/lang/yue/block_review.json`
  - `test/data/<dataset>/output/yue-Hant/lang/yue/block_review.json`
  - `test/data/<dataset>/output/yue-Hant/lang/yue/simplify_block_review.json`

For SRT datasets, source/review timings should match within each script, and
final yue-Hans/final simplified yue-Hant timings should match after timewarp.
Do not require pre-timewarp source timings to match post-timewarp final timings.

## Run

On Windows, set UTF-8 first:

```powershell
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()
$env:UV_CACHE_DIR = "/tmp/uv-cache"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
```

Run the bundled script from the repository root:

```powershell
uv run python skills/audit-yue-review-dual/scripts/audit_yue_review_dual.py --dataset acoptc
```

To limit the audit to a subtitle-number range, pass `--first-index` and/or
`--last-index`. These bounds are 1-indexed subtitle numbers and are inclusive:

```powershell
uv run python skills/audit-yue-review-dual/scripts/audit_yue_review_dual.py --dataset tmm --first-index 1 --last-index 200
```

To print only rows that need attention, add `--omit-ok`. This omits rows whose
generated note is exactly `OK`:

```powershell
uv run python skills/audit-yue-review-dual/scripts/audit_yue_review_dual.py --dataset tmm --first-index 1 --last-index 1000 --omit-ok
```

For SRT datasets, run:

```powershell
uv run python skills/audit-yue-review-dual/scripts/audit_yue_review_dual.py --dataset <dataset> --layout non-ocr
```

The script prints Markdown. Redirect it to a temporary file when the table is
large:

```powershell
uv run python skills/audit-yue-review-dual/scripts/audit_yue_review_dual.py --dataset acoptc > local/acoptc-yue-review-dual.md
```

The script fails before printing the table if any of the yue-Hans input,
yue-Hans reviewed, final yue-Hans, yue-Hant input, yue-Hant reviewed, or final
simplified yue-Hant SRT files disagree on subtitle numbers. It also fails if
timings differ within comparable timing groups: all files for OCR datasets,
source/review pairs plus final/final pairs for SRT datasets.

## Interpret

Review the union table row by row. A row appears when at least one of these is
true:

- yue-Hans review changed the subtitle
- yue-Hant review changed the subtitle
- final yue-Hans text differs from final simplified yue-Hant text

Use the yue-Hans and yue-Hant columns to check whether both scripts made the
same approved correction at the same subtitle number. Use the final-comparison
columns to find remaining simplification, Mandarinization, punctuation, or
whitespace issues.

Flag asymmetric review corrections as discrepancies. If one script makes an
approved lexical or OCR correction and the corresponding other-script line has
the same underlying issue, the other script should usually make the same
correction in its review output instead of leaving it to simplification review
or final comparison.

The script output is a draft table. Read that Python script output first.

You must provide a non-empty note for every row before printing or presenting
the table. Default script notes are intentionally minimal; they may need to be
reviewed and replaced with stronger editorial callouts.

Use plain, specific notes that say what changed:

- `OK` when the review edits make sense as written Cantonese,
  Cantonese-script normalization, or clear OCR/spacing cleanup
- Only Hans changed (`罗` -> `啰`); Hant stayed `囉`
- Only Hant changed (`...` -> `...`); Hans stayed `...`
- No review edits, but the finals still differ: `...` vs `...`
- Both sides changed, but the finals still differ: Hans `...` -> `...`; Hant `...` -> `...`; finals `...` vs `...`
- `OK`

Do not leave the `Notes` column blank in user-facing output. If a displayed row
is accepted without any issue, mark it explicitly as `OK`. When the user asks to
omit accepted rows, use `--omit-ok` so the summary and table stay consistent.

## Output

When you run this skill, the script output must be returned directly in your response.
Do not summarize or replace it.
Include the full Markdown report text (summary + table) exactly as printed.

Before presenting, ensure every row in the table has a non-empty `Notes` cell.
If any note is missing in the raw script output, replace it with `OK`.

Start with the script summary, including subtitle counts, the successful timing
alignment check, changed counts, and image-index links. Then output the table
with the `Notes` column filled in.

The table columns are:

| Subtitle | yue-Hans | yue-Hant | yue-Hans vs Hant->Hans | Notes |
|---:|---|---|---|---|

In the `yue-Hans` and `yue-Hant` columns, stack the before and after review text
on separate lines when that script changed. When only one script changed at a
subtitle number, include the unchanged counterpart text once in its own column
so the two scripts can be compared in context. Do not stack unchanged text. In
the `yue-Hans vs Hant->Hans` column, stack the final yue-Hans text and final
simplified yue-Hant text on separate lines. Do not use arrows in these cells.

In the `Subtitle` column, output only the shared subtitle number, such as `123`.
The yue-Hans and yue-Hant series must be 1:1, so do not include separate Hans
and Hant anchor IDs or repeated subtitle numbers.
