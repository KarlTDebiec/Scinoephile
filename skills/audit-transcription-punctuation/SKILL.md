---
name: audit-transcription-punctuation
description: Audit Scinoephile pairwise or sparse windowed block transcription punctuation JSON by matching its guides and fixed target text to reference and punctuated target SRTs. Use when inspecting punctuation-*.json, block_punctuation-*.json, legacy mps.json or cuda.json, correcting punctuation, or verifying cases. Do not assess transcription accuracy.
---

# Audit Transcription Punctuation

Audit the punctuation and whitespace added to fixed transcription text. The
same CLI automatically recognizes legacy pairwise JSON, complete sparse block
JSON, and overlapping sparse block windows.
Produce a Markdown report, inspect every requested row, and record a concise
judgment in each `Notes` cell.

## Scope

Assess only whether the punctuation operation appropriately combined and
punctuated the supplied target fragments. Treat the target characters as fixed.

Do not assess transcription accuracy, translation accuracy, wording, character
choice, Mandarinisms, omissions, or repetitions. Those belong to later review
stages. Do not criticize the delineation of the input fragments except where the
punctuation answer itself joins or separates them incorrectly.

An empty target has no punctuation work to perform. If it remains empty, judge
that index as correct; do not treat the absence of transcribed text as a
punctuation error. A literal punctuation-only target is different and remains
subject to the deterministic punctuation-only validation rule below.

## Protect the source data

Generating and annotating an audit is read-only with respect to the source JSON
and SRT files. Do not modify them unless the user explicitly asks for fixes or
verification. When asked to fix a case, update its JSON answer and propagate the
correction to any derived output required by the repository workflow.

## Locate the inputs

Find these three inputs for the requested dataset:

- the reference or guide SRT used during punctuation
- the punctuated target SRT, normally `transcribe.srt`
- the punctuation test-case JSON, currently often
  `punctuation-<provider>.json` or `block_punctuation-<provider>.json`, and in
  older workflows `punctuation/mps.json` or `punctuation/cuda.json`

The target SRT is used only to distinguish repeated reference subtitles. Do not
use it as evidence that the transcription is accurate.

The CLI auto-detects the JSON shape; do not pass an implementation-mode option
or use a separate command for block JSON.

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

Use `--first-block` and `--last-block` for an inclusive, one-based range of
reference blocks. Block and subtitle bounds are mutually exclusive. Omit either
block bound for an open-ended range.

Use `--filter changes` only when the user explicitly wants cases whose answers
changed punctuation or whitespace. Use `--filter unverified` when continuing
verification of a partly audited file. The report summary labels requested
bounds as the reference subtitle or block range.

The report has exactly six columns. Pairwise JSON uses:

| Index | Reference | Input | Output | Notes | Verified |
| ---: | --- | --- | --- | --- | :---: |

Block JSON uses:

| Indexes | Reference | Input | Output | Notes | Verified |
| ---: | --- | --- | --- | --- | :---: |

For pairwise JSON, the Input column stacks the query fragments with `<br>`. For
block JSON, each row is one complete logged case. `Indexes` identifies the case
number and resolved reference range. Window rows also identify `Owns refs ...`;
Reference and Input mark each local index as `[owned]` or `[context]`. The
ownership fields persisted in JSON are inclusive `first_owned_index` and
`last_owned_index` values. Output lists only the answer's sparse replacement
indexes. Output is blank when the case made no punctuation or
whitespace change and `(unanswered)` when no answer is present. Verified
contains `✓` for a verified JSON case and is otherwise blank. A subtitle range
includes a complete legacy block only when its full guide range is selected; it
includes a window when its full owned range is selected, even if displayed
context extends outside the range. Within indexed Input or Output text, an empty
string is displayed as `(empty)` so that it cannot be confused with a literal em
dash, which is displayed as `—`. Rows are sorted by resolved reference start;
repeated logged cases remain separate.

## Audit every row

Open the Markdown file and inspect every requested row. In a window row, inspect
every owned subtitle and use context only to understand it. Never demand or add
a punctuation change for a context index; another overlapping window owns that
output. The reference
punctuation is useful context, but it does not dictate the target punctuation:
Cantonese phrasing and sentence boundaries may differ from the guide.

Current Cantonese block punctuation rejects three deterministic output defects
and retries them before saving: owned subtitles beginning with closing sentence
punctuation, nonempty owned subtitles containing only punctuation or whitespace,
and half-width sentence punctuation adjacent to Hanzi. Decimal points and other
punctuation internal to Western numbers or terms remain valid. Continue checking
these rules during an audit because older verified or no-op data may predate the
validator. The validator does not detect semantically missing question marks,
wrong punctuation choices, or discourse errors; audit those manually.

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
- For pairwise JSON, edit the complete `output` string.
- For block JSON, keep `answer.changes` sparse: include only changed owned
  indexes, store each index's complete replacement text, and remove entries that
  no longer change anything. Sparse means unchanged indexes are omitted, not
  that only a few owned indexes should be inspected. After punctuation and
  whitespace are removed, every replacement must preserve the original
  characters at that same index.
- Mark a case `verified: true` only after auditing the entire pairwise or
  complete-block row, or every owned subtitle in a window, and correcting its
  answer where necessary.
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
