---
name: audit-zho-review-dual
description: Use when auditing standard Chinese OCR datasets across zho-Hans review, zho-Hant review, and final zho-Hans versus simplified zho-Hant outputs in one combined table.
---

# Audit Zho Review Dual

Use this workflow when a Zho OCR dataset needs one table that shows:

- what zho-Hans review changed
- what zho-Hant review changed
- what still differs between final zho-Hans and final simplified zho-Hant

This is useful when review decisions should be checked across both scripts at
the same subtitle number.

Important:

- Never edit files under `test/data/<dataset>/input/`.
- Do not edit generated reviewed, flattened, simplified, or romanized SRT files
  directly.
- Edit review JSON files for review corrections, then regenerate reviewed
  outputs from them.
- Edit `fuse_clean_validate.srt` and `image/index.html` only when the user
  explicitly asks for an OCR validation-source correction.

## Inputs

The audit uses these OCR files:

- `test/data/<dataset>/output/zho-Hans_ocr/fuse_clean_validate.srt`
- `test/data/<dataset>/output/zho-Hans_ocr/fuse_clean_validate_review.srt`
- `test/data/<dataset>/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt`
- `test/data/<dataset>/output/zho-Hant_ocr/fuse_clean_validate.srt`
- `test/data/<dataset>/output/zho-Hant_ocr/fuse_clean_validate_review.srt`
- `test/data/<dataset>/output/zho-Hant_ocr/fuse_clean_validate_review_flatten_simplify_review.srt`

Edit these review JSON files when applying review corrections:

- `test/data/<dataset>/output/zho-Hans_ocr/lang/zho/review.json`
- `test/data/<dataset>/output/zho-Hant_ocr/lang/zho/review.json`
- `test/data/<dataset>/output/zho-Hant_ocr/lang/zho/simplify_review.json`

All audited Zho OCR SRT files should share subtitle numbers and timings.

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
uv run python skills/audit-zho-review-dual/scripts/audit_zho_review_dual.py --dataset tmm
```

To limit the audit to a subtitle-number range, pass `--first-index` and/or
`--last-index`. These bounds are 1-indexed subtitle numbers and are inclusive:

```powershell
uv run python skills/audit-zho-review-dual/scripts/audit_zho_review_dual.py --dataset tmm --first-index 1 --last-index 200
```

The script prints Markdown directly to stdout for review in the
console/conversation. Do not redirect to an intermediate `.md` file during
normal runs.

The script fails before printing the table if any audited SRT file disagrees on
subtitle numbers or timings.

## Interpret

Review the union table row by row. A row appears when at least one of these is
true:

- zho-Hans review changed the subtitle
- zho-Hant review changed the subtitle
- final zho-Hans text differs from final simplified zho-Hant text

Use the zho-Hans and zho-Hant columns to check whether both scripts made the
same approved correction at the same subtitle number. Use the final-comparison
column to find remaining simplification, OCR, punctuation, or whitespace issues.

Flag asymmetric review corrections as discrepancies. If one script makes an
approved OCR, punctuation, or lexical correction and the corresponding
other-script line has the same underlying issue, the other script should usually
make the same correction in its initial review instead of leaving it to
simplification review or final comparison.

Manual review rule:

- The script intentionally leaves `Notes` blank; fill every row manually before
  sending a user-facing audit table.
- Do not change subtitle numbers, text columns, or summary lines.
- Write one concise note per row describing the review behavior or remaining
  discrepancy.
- Do not send a table with any blank Notes cell.

Output safety rule:

- Do not wrap the report in code fences.
- The final user-facing audit response must begin with the report title, such as
  `# tmm Zho Review Dual`, and contain only raw Markdown report content.
