---
name: audit-guided-subtitle-reviews
description: Audit Scinoephile guided subtitle review JSON against the exact target and guide SRT files used to generate it. Use when inspecting guided_review mps.json, cuda.json, or cpu.json files; judging sparse per-subtitle revisions or missed revisions; checking model explanations; or verifying guided-review test cases.
---

# Audit Guided Subtitle Reviews

Run commands from the repository root. Audit the guided-review stage applied to
the cleaned transcription. The dataset workflow chains this stage after
transcription and cleaning, but its decisions remain separate from transcription
generation, delineation, punctuation, and gap translation.

## Required report file

Always save the complete six-column Markdown report under `local/`. After
auditing every row, add each concise audit note directly to that file's `Notes`
cell. Do not leave notes only in commentary, tool output, or the final response.

- Keep the table at exactly these columns: `Index`, `Block`, `Guide`,
  `Target / revision`, `Notes`, and `Verified`.
- `Block` is the one-based guided-review block containing the target subtitle.
- In `Target / revision`, show the input target first and stack the proposed
  revision beneath it. Show only the target when an answered case proposed no
  revision, and stack `(unanswered)` beneath it when the case has no answer.
- Replace the model-provided JSON note with your own independent interpretation
  in `Notes`; never copy or lightly paraphrase the model's explanation.
- Write `OK` only for a proposed revision that is clearly appropriate. For an
  unchanged target, leave `Notes` blank only when the no-revision decision is
  clearly appropriate.
- Preserve the generated `Verified` cell: `✓` means the JSON test case is
  verified, and an empty cell means it is not verified.
- Keep observations beside their rows rather than adding a findings section.
- Validate the saved report after adding notes, then provide a clickable link
  to it in the final response. Do not paste the table inline unless the user
  explicitly requests it.

## Protect source data

- Never edit files under `test/data/<dataset>/input/`.
- For an audit-only request, do not edit target or guide SRT files, reviewed
  output, or guided-review JSON.
- When corrections are requested, edit only the relevant JSON answers and
  verification metadata, then regenerate downstream output through the dataset
  workflow. Never hand-edit generated reviewed SRT files.
- Preserve each JSON query exactly. A revision index is local to its query's
  target block, not the global SRT subtitle number shown by the audit report.

## Locate artifacts

Find the exact target SRT and guide SRT supplied to `review_series_guided` and
the corresponding guided-review JSON. Do not substitute a later reviewed
output, an official subtitle track, or a similarly named guide.

Transcription-dataset artifacts commonly look like:

- target: `<language>_transcribe/transcribe_clean.srt`
- guide: `<guide-language>_ocr/fuse_clean_validate_review_flatten.srt`
- JSON: `<language>_transcribe/lang/<language-pair>/guided_review/<device>.json`

The CLI internally reconstructs the same inputs used by guided review and
matches each logged query by both target and guide text. It then aligns guide
subtitles by timing and emits one row per target subtitle. It rejects missing
or ambiguous matches rather than assigning misleading global indexes.

## Generate the report

Always set `UV_CACHE_DIR=/tmp/uv-cache`:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit guided-review \
  --target <target.srt> \
  --guide <guide.srt> \
  --json <guided-review.json> \
  --first-index <first> \
  --last-index <last> \
  --filter all \
  --outfile local/<dataset>_guided_review_audit_<first>-<last>.md
```

Use `--filter all` for a complete audit, including no-revision answers that may
have missed errors. Use `--filter changes` only for a focused review of proposed
revisions. Use `--filter unverified` when continuing verification of a partly
audited file. The default is `all`.

The summary distinguishes revised, unchanged, and unanswered subtitles. An
unanswered case is incomplete; do not interpret it as an explicit no-revision
decision.

`--first-index` and `--last-index` are inclusive, one-based indexes in the
target SRT. The report includes exactly the target subtitles in the requested
range. Summarize the range without restating the index convention.

## Audit every subtitle

Judge whether each sparse answer appropriately reviewed the target subtitle
using its timing-aligned guide subtitle or subtitles as evidence.

- Check that every proposed revision fixes a clear target error, uses the
  correct target subtitle, and retains natural target-language wording.
- Check no-revision answers for clear missed corrections. An empty revision
  list is a decision that must be audited, not an automatically acceptable row.
- Treat the guide as semantic evidence, not text to translate literally.
  Standard Chinese and Cantonese may differ legitimately in vocabulary,
  particles, syntax, omissions, repetitions, and segmentation.
- Do not replace idiomatic Cantonese with Mandarin-like wording merely to match
  the guide.
- Treat `OK` as a positive conclusion, not a default. Require clear support
  from the target error and guide context; when they leave competing readings
  plausible, use `Uncertain;` rather than accepting a revision.
- Read model-provided JSON notes as context, not proof. Replace them in the
  report with your own interpretation of the evidence and decision.
- When a proposed or missed change substitutes one target-language expression
  for another, append the original and replacement readings to the note. Use
  tone-marked Yale for `yue-*` targets and tone-marked Hanyu Pinyin for `zho-*`
  targets. Romanize the smallest meaningful substituted spans, not the full
  subtitle, and include every independent substitution. Use the format
  `Yale: 原文 (reading) → 新文 (reading)` or
  `Hanyu Pinyin: 原文 (reading) → 新文 (reading)`. Do not add romanization for
  pure insertions, deletions, punctuation, or whitespace changes. Use the
  repository's language romanizers and verify context-sensitive readings; if
  a reading cannot be established, state that it is uncertain rather than
  guessing.
- Because guided review follows punctuation and cleaning, reject punctuation-only
  or whitespace-only revisions. When a valid text correction also changes
  punctuation or whitespace unnecessarily, retain the correction while
  restoring the input punctuation and whitespace.
- If target and guide text do not provide enough evidence, mark the decision
  uncertain rather than guessing from an unavailable audio track.

Use concise English audit notes. Write exactly `OK` for an appropriate proposed
revision. When a decision has a problem, begin the note with one of these
labels and give only the material detail:

- `Incorrect revision;` when a proposed change is wrong, unsupported, assigned
  to the wrong target, or contains unrelated rewriting.
- `Missed revision;` when a no-revision answer or partial answer leaves a clear
  error that the guide resolves.
- `Uncertain;` when the available block does not establish the correct reading.

Every proposed revision receives either `OK` or a problem note. Leave `Notes`
blank only when an unchanged target was appropriately left alone. Read the
saved report from beginning to end, write all notes into its table, and confirm
that every generated row has been independently audited.

## Correct and verify cases

When the user requests corrections, update the sparse JSON answer rather than
the generated SRT:

- Add, replace, or remove only the necessary revision objects.
- Use the query-local target index shown inside the JSON, not the report's
  global SRT index.
- Keep each revision's full corrected target text and a concise explanation.
- Keep revisions unique and in ascending local-index order.
- Mark a case `verified: true` only after auditing every target subtitle in its
  query and correcting its answer where necessary. If the requested range
  includes only part of a query, do not mark that case verified yet.
- Do not mark unanswered or unaudited cases verified.

After corrections, regenerate `transcribe_clean_review.srt` and downstream
outputs through the dataset workflow, then rerun the audit over the corrected
range. Confirm the JSON remains canonical and the report contains the expected
decisions before linking the complete interpreted report.
