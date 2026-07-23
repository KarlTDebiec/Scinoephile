---
name: audit-ocr-fusion
description: Audit Scinoephile OCR-fusion output against the exact two OCR source SRTs and optional OCR-fusion JSON used to generate it, optionally comparing every fused subtitle with a one-to-one validated SRT as ground truth. Use when inspecting ocr_fusion.json decisions, source selection, fused OCR errors, validation discrepancies, verification state, or corrected OCR-fusion cases.
---

# Audit OCR Fusion

Run commands from the repository root. Audit the fused OCR track, not later
cleaning or review stages.

## Required report file

Save the complete Markdown report under `local/`.

- Keep these columns: `Subtitle`, `Case`, `Difficulty`, `Source one`, `Source
  two`, `Fused`, `Validated`, and `Notes`. When JSON is supplied, also include
  `Verified`.
- `Case` and `Difficulty` are `—` for deterministic rows and rows audited
  without JSON. When JSON is supplied, `Verified` is `—` for deterministic
  rows, `✓` for verified JSON cases, and empty for unverified JSON cases.
- Treat `Validated` as ground truth when supplied. It is `—` when omitted.
- Generated `Notes` contains the recorded LLM note when JSON is supplied, an
  automatic fusion explanation for deterministic rows, or an empty cell when
  no context is available. Read it as context, then replace the entire cell
  with your own independent judgment; do not append to or merely endorse the
  generated content.
- Validate the saved table after generating it and provide a clickable link.
  Do not paste the full table inline unless the user requests it.

## Protect source data

- Never edit files under `test/data/<dataset>/input/`.
- For an audit-only request, do not edit either OCR source, the fused or
  validated SRT, or OCR-fusion JSON.
- When corrections are requested, edit an LLM decision in OCR-fusion JSON and
  regenerate the fused and downstream tracks. Never hand-edit `fuse.srt`.
- Treat a validated-track correction as a separate source-data change and make
  it only when the user explicitly requests it.

## Locate exact inputs

Find the artifacts from the same OCR run:

- source one: commonly `lens.srt`
- source two: commonly `tesseract.srt` or `paddle.srt`
- fused output: `fuse.srt`
- optional JSON: `<ocr-output>/lang/<language-code>/ocr_fusion.json`
- optional truth: a one-to-one validated track derived from the fused OCR
  workflow, commonly a later `*_validate.srt`

All supplied SRTs must have identical subtitle counts and exact timings. Do not
substitute an official subtitle track with different segmentation; use an
aligned-diff audit for that comparison.

## Generate the report

Always set `UV_CACHE_DIR=/tmp/uv-cache`:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit ocr-fusion \
  --source-one <source-one.srt> \
  --source-two <source-two.srt> \
  --fused <fuse.srt> \
  --json <ocr_fusion.json> \
  --validated <validated.srt> \
  --first-index <first> \
  --last-index <last> \
  --filter changes \
  --outfile local/<dataset>_ocr_fusion_audit_<first>-<last>.md \
  --overwrite
```

Omit `--json` when no decision log is available. Omit `--validated` when no
aligned truth track exists. The inclusive range uses fused-track indexes. Filters
are:

- `changes`: source disagreements, including deterministic one-source rows
- `all`: every fused subtitle, including identical and empty sources
- `unverified`: only unverified LLM cases; without JSON, all rows requiring an
  LLM decision are unverified
- `discrepancies`: only fused rows that differ from `--validated`; this filter
  requires the validated track and includes deterministic rows

Use `--first-block` and `--last-block` for an inclusive, one-based range of
fused-track blocks. Block and subtitle bounds are mutually exclusive. Omit
either block bound for an open-ended block range.

The CLI verifies that deterministic fused rows match the processor rules. When
JSON is supplied, it also verifies that answered LLM outputs match `fuse.srt`,
uses the latest logged case for a repeated source pair, and rejects missing
current decisions.

## Audit every row

Judge whether `Fused` is the most accurate rendering supported by the sources.
When `Validated` is present, treat any substantive difference as a fusion error
unless the validated track itself is demonstrably wrong.

- Check characters, words, case, line breaks, punctuation, spacing, and obvious
  OCR confusions.
- When JSON is supplied, check whether the note accurately describes the selected
  output, but do not accept a decision merely because its explanation sounds
  plausible.
- For deterministic rows, verify that choosing the sole nonempty source or the
  identical source text remains correct against validated truth.
- Do not assess later cleaning, translation, or subtitle-review decisions.

When reporting a finding, use exactly `OK` for a correct fusion. Otherwise begin
the finding with one of:

- `Incorrect fusion;` for a clear wrong selection or synthesized error
- `Validated discrepancy;` when fused text differs from reliable validated
  truth
- `Incorrect note;` when output is acceptable but the explanation is not
- `Uncertain;` when the sources and available truth do not establish the text

## Correct and verify cases

When corrections are requested:

- Edit only the matching JSON answer's `output` and `note`; preserve its query.
- Mark `verified: true` only after auditing the complete case and correcting
  both output and note where necessary.
- Never verify unanswered, unaudited, or partially audited cases.

Regenerate the fused OCR track and every downstream artifact through the
dataset workflow. Rerun the audit, confirm the JSON is canonical, and ensure
corrected cases no longer appear with `--filter unverified`.
