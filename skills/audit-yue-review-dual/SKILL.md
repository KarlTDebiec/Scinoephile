---
name: audit-yue-review-dual
description: Audit Cantonese subtitle reviews across yue-Hans, yue-Hant, and simplified yue-Hant tracks, including OCR and SRT datasets, review notes, character-focused checks, and final script discrepancies.
---

# Audit Yue Review Dual

Use `scinoephile audit` to produce one table showing:

- yue-Hans review changes
- yue-Hant review changes
- simplified yue-Hant review changes
- final yue-Hans versus simplified yue-Hant discrepancies

Run commands from the repository root.

## Protect source data

- Never edit files under `test/data/<dataset>/input/`.
- Do not edit generated reviewed, flattened, simplified, or romanized SRT files.
- Apply review corrections only to the relevant review JSON, then regenerate
  outputs.
- Never Mandarinize Cantonese wording. In particular, do not replace Cantonese
  particles or short forms with Mandarin equivalents such as `咗 -> 了`.

## Run an OCR dataset

Replace `<dataset>` and run:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit \
  --simplified test/data/<dataset>/output/yue-Hans_ocr/fuse_clean_validate.srt \
  --simplified-reviewed test/data/<dataset>/output/yue-Hans_ocr/fuse_clean_validate_review.srt \
  --traditional test/data/<dataset>/output/yue-Hant_ocr/fuse_clean_validate.srt \
  --traditional-reviewed test/data/<dataset>/output/yue-Hant_ocr/fuse_clean_validate_review.srt \
  --traditional-simplified test/data/<dataset>/output/yue-Hant_ocr/fuse_clean_validate_review_flatten_simplify.srt \
  --traditional-simplified-reviewed test/data/<dataset>/output/yue-Hant_ocr/fuse_clean_validate_review_flatten_simplify_review.srt \
  --simplified-json test/data/<dataset>/output/yue-Hans_ocr/lang/yue/review.json \
  --traditional-json test/data/<dataset>/output/yue-Hant_ocr/lang/yue/review.json \
  --traditional-simplified-json test/data/<dataset>/output/yue-Hant_ocr/lang/yue/simplify_review.json
```

## Run an SRT dataset

Replace `<dataset>` and run:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit \
  --simplified test/data/<dataset>/input/yue-Hans.srt \
  --simplified-reviewed test/data/<dataset>/output/yue-Hans/clean_review.srt \
  --traditional test/data/<dataset>/input/yue-Hant.srt \
  --traditional-reviewed test/data/<dataset>/output/yue-Hant/clean_review.srt \
  --traditional-simplified test/data/<dataset>/output/yue-Hant/clean_review_flatten_timewarp_simplify.srt \
  --traditional-simplified-reviewed test/data/<dataset>/output/yue-Hant/clean_review_flatten_timewarp_simplify_review.srt \
  --simplified-json test/data/<dataset>/output/yue-Hans/lang/yue/review.json \
  --traditional-json test/data/<dataset>/output/yue-Hant/lang/yue/review.json \
  --traditional-simplified-json test/data/<dataset>/output/yue-Hant/lang/yue/simplify_review.json
```

`--simplified-reviewed` is both the reviewed yue-Hans track and the
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
are included automatically. Yue characters commonly worth checking include:

- `些`: decide whether colloquial usage should be `啲`
- `番`: distinguish `返`, `翻`, and legitimate `番`
- `是`: decide whether the Cantonese copula should be `係`
- `着`: check Cantonese aspect and lexical usage
- `喇啦啰`: check final-particle choice; normally combine with the default
  changed-row filter because these particles are common
- `这那`: consider `呢` or `嗰` in colloquial dialogue

For an occurrence audit, append options such as:

```shell
--filter all --characters 些 番 是 着 这那
```

For a changed-row particle audit, append:

```shell
--characters 喇啦啰
```

Use inclusive 1-indexed bounds with `--first-index` and `--last-index`. The CLI
prints Markdown to stdout by default; use `--outfile <path>.md` for a large
report that needs inspection before presentation.

## Review the report

Inspect every displayed row. Compare the two initial review columns for
asymmetric corrections, the traditional-simplified review for final cleanup,
and the final comparison for remaining lexical, OCR, punctuation, whitespace,
or Mandarinization issues.

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
