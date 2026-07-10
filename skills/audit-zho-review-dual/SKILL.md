---
name: audit-zho-review-dual
description: Audit standard Chinese OCR subtitle reviews across zho-Hans, zho-Hant, and simplified zho-Hant tracks, including review notes, character-focused checks, and final script discrepancies.
---

# Audit Zho Review Dual

Use `scinoephile audit` to produce one table showing:

- zho-Hans review changes
- zho-Hant review changes
- simplified zho-Hant review changes
- final zho-Hans versus simplified zho-Hant discrepancies

Run commands from the repository root.

## Protect source data

- Never edit files under `test/data/<dataset>/input/`.
- Do not edit generated reviewed, flattened, simplified, or romanized SRT files.
- Apply review corrections only to the relevant review JSON, then regenerate
  outputs.
- Edit `fuse_clean_validate.srt` and `image/index.html` only when the user
  explicitly requests an OCR validation-source correction.

## Run an OCR dataset

Replace `<dataset>` and run:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit \
  --simplified test/data/<dataset>/output/zho-Hans_ocr/fuse_clean_validate.srt \
  --simplified-reviewed test/data/<dataset>/output/zho-Hans_ocr/fuse_clean_validate_review.srt \
  --traditional test/data/<dataset>/output/zho-Hant_ocr/fuse_clean_validate.srt \
  --traditional-reviewed test/data/<dataset>/output/zho-Hant_ocr/fuse_clean_validate_review.srt \
  --traditional-simplified test/data/<dataset>/output/zho-Hant_ocr/fuse_clean_validate_review_flatten_simplify.srt \
  --traditional-simplified-reviewed test/data/<dataset>/output/zho-Hant_ocr/fuse_clean_validate_review_flatten_simplify_review.srt \
  --simplified-json test/data/<dataset>/output/zho-Hans_ocr/lang/zho/review.json \
  --traditional-json test/data/<dataset>/output/zho-Hant_ocr/lang/zho/review.json \
  --traditional-simplified-json test/data/<dataset>/output/zho-Hant_ocr/lang/zho/simplify_review.json
```

`--simplified-reviewed` is both the reviewed zho-Hans track and the
simplified-side input to the final comparison. The command exits if the six SRT
tracks do not contain the same number of subtitles.

On PowerShell, configure UTF-8 before running commands that print subtitles:

```powershell
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()
$env:UV_CACHE_DIR = "/tmp/uv-cache"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
```

## Focus the audit

The default `--filter changes` includes every review change and final
discrepancy. Use `--filter discrepancies` for final discrepancies only, or
`--filter all` for every subtitle.

Add `--characters` to keep only rows containing any requested character in any
track. Values may be separate or combined. Simplified and traditional variants
are included automatically. Zho characters commonly worth checking include
`著`, `着`, `甚`, and `什`.

For example, append this for a complete occurrence audit:

```shell
--filter all --characters 著 着 甚 什
```

Use inclusive 1-indexed bounds with `--first-index` and `--last-index`. The CLI
prints Markdown to stdout by default; use `--outfile <path>.md` for a large
report that needs inspection before presentation.

## Review the report

Inspect every displayed row. Compare the two initial review columns for
asymmetric corrections, the traditional-simplified review for final cleanup,
and the final comparison for remaining simplification, lexical, OCR,
punctuation, or whitespace issues.

The JSON arguments populate `Notes` with the reasons recorded for matching
review changes. Preserve useful JSON notes. Before presenting the report, fill
every remaining blank note with one concise judgment based on the row. Do not
use placeholders such as `N/A` or `-`.

If one script makes an appropriate lexical, OCR, or punctuation correction and
the other contains the same underlying issue, flag the asymmetry. Prefer making
the correction in the corresponding initial review instead of relying on later
simplification cleanup.

Return the complete raw Markdown report. Do not wrap it in a code fence and do
not replace it with a summary.
