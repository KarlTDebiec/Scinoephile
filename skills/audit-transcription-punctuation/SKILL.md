---
name: audit-transcription-punctuation
description: Audit Scinoephile transcription punctuation logs by matching JSON guide text and target fragments to reference and punctuated target SRTs, then judging whether punctuation and whitespace are appropriate without assessing transcription accuracy. Use when inspecting punctuation mps.json or cuda.json files, identifying punctuation errors, or verifying corrected punctuation test cases.
---

# Audit Transcription Punctuation

Audit the punctuation and whitespace added to fixed transcription text. Produce a
Markdown report, inspect every requested row, and record a concise judgment in
each `Notes` cell.

## Scope

Assess only whether the punctuation operation appropriately combined and
punctuated the supplied target fragments. Treat the target characters as fixed.

Do not assess transcription accuracy, translation accuracy, wording, character
choice, Mandarinisms, omissions, or repetitions. Those belong to later review
stages. Do not criticize the delineation of the input fragments except where the
punctuation answer itself joins or separates them incorrectly.

## Protect the source data

Generating and annotating an audit is read-only with respect to the source JSON
and SRT files. Do not modify them unless the user explicitly asks for fixes or
verification. When asked to fix a case, update its JSON answer and propagate the
correction to any derived output required by the repository workflow.

## Locate the inputs

Find these three inputs for the requested dataset:

- the reference or guide SRT used during punctuation
- the punctuated target SRT, normally `transcribe.srt`
- the punctuation test-case JSON, normally `mps.json` or `cuda.json`

The target SRT is used only to distinguish repeated reference subtitles. Do not
use it as evidence that the transcription is accurate.

## Generate the report

Write the report to a Markdown file under `local/`; do not print the full table
in the conversation. Use the inclusive reference-subtitle range requested by the
user:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit punctuation \
  --reference <reference.srt> \
  --target <transcribe.srt> \
  --json <punctuation/mps.json> \
  --first-index <first> \
  --last-index <last> \
  --filter all \
  --outfile local/<dataset>_punctuation_audit_<first>-<last>.md \
  --overwrite
```

Use `--filter changes` only when the user explicitly wants cases whose answers
changed punctuation or whitespace. Use `--filter unverified` when continuing
verification of a partly audited file. The report summary labels the requested
bounds as the reference subtitle range. The report has exactly these columns:

Use `--first-block` and `--last-block` for an inclusive, one-based range of
reference blocks. Block and subtitle bounds are mutually exclusive. Omit either
block bound for an open-ended range.

| Index | Reference | Input | Output | Notes | Verified |
|---:|---|---|---|---|:---:|

The Input column stacks the query fragments with `<br>`. Output is blank when
the answer made no punctuation or whitespace change and `(unanswered)` when no
answer is present. Verified contains `✓` for verified JSON cases and is otherwise
blank. Rows are sorted by subtitle index; repeated logged cases remain separate.

## Audit every row

Open the Markdown file and inspect every requested row. The reference
punctuation is useful context, but it does not dictate the target punctuation:
Cantonese phrasing and sentence boundaries may differ from the guide.

Consider:

- question marks, exclamation marks, full stops, commas, colons, ellipses, and
  quotation marks
- spaces and the joining of the supplied fragments
- particles, vocatives, interjections, and discourse markers
- whether punctuation splits a grammatical phrase or implies the wrong
  relationship between clauses

Write exactly `OK` for an acceptable answer. Otherwise use one of these exact
prefixes:

- `Punctuation error;` for a clear punctuation or whitespace error
- `Uncertain;` when the audio or broader context is needed to judge the choice

Punctuation JSON has no note field, so generated Notes cells begin blank. If a
future schema populates one, read it as context and replace the entire cell with
your own concise judgment rather than appending to or treating it as proof.
Never mark an unanswered row `OK`.

## Correct and verify cases

When the user requests corrections, update the punctuation JSON answer rather
than the generated target SRT:

- Correct the punctuation or whitespace output before marking the case
  verified.
- Mark a case `verified: true` only after auditing the entire punctuation case
  and correcting its answer where necessary.
- Leave unanswered, unaudited, or partially audited cases unverified.

After corrections, regenerate the punctuated target SRT and downstream
artifacts through the dataset workflow. Rerun the audit over the corrected
range, confirm the JSON remains canonical, and confirm corrected cases no
longer appear with `--filter unverified` before linking the complete interpreted
report.

## Validate and deliver

After annotating the Markdown file:

1. Confirm every requested row was inspected.
2. Confirm the table still has exactly six columns and valid Markdown escaping.
3. Confirm notes discuss punctuation only.
4. Link the report file to the user and summarize the number and indexes of
   clear errors and uncertain cases.
