---
name: audit-subtitle-reviews
description: Audit Scinoephile regular or guided subtitle reviews, traditional-to-simplified review paths, or dual Hans/Hant review paths. Use when inspecting original and reviewed SRTs, review or guided_review JSON, guide-supported revisions, character-focused changes, parallel script outputs, verification state, or corrected subtitle-review cases.
---

# Audit Subtitle Reviews

Run commands from the repository root. Discover the artifacts that produced the
review before selecting a workflow; language alone does not determine it.

## Required report file

Save the complete Markdown report under `local/`, audit every displayed row,
and write each independent finding in its `Notes` cell.

- Preserve the exact columns emitted by the selected command.
- The generated `Notes` cell contains any applicable JSON revision note. Read it
  as context, then replace the entire cell with your own independent judgment;
  do not append to or merely endorse the recorded note.
- When emitted, preserve `Verified`: `✓` means the complete JSON case was
  verified.
- Validate the edited table and provide a clickable link. Do not paste the full
  table inline unless the user requests it.

## Protect source data

- Never edit files under `test/data/<dataset>/input/`.
- For an audit-only request, do not edit SRTs, review JSON, or validation data.
- When corrections are requested, edit the relevant JSON answers and
  verification metadata, then regenerate reviewed and downstream artifacts.
- Never hand-edit a generated reviewed, flattened, simplified, timewarped, or
  romanized SRT.
- Change OCR validation sources only when the user explicitly requests that
  separate correction.

## Select the workflow

| Available inputs | Command |
|---|---|
| One original/reviewed pair | `audit review --reviewed` |
| Target, guide, and guided-review JSON | `audit review --guide` |
| Hant review plus review of its simplified form | `audit review-trad` |
| Parallel Hans and Hant-to-Hans paths | `audit review-dual` |

Use regular review for English or a single Chinese-script track. It detects the
language and script automatically. Use guided review only for sparse decisions
made with a timing-aligned guide. Keep `review-trad` and `review-dual` for their
multi-stage comparison shapes.

## Locate exact inputs

Regular OCR review commonly uses:

- original: `<language>_ocr/fuse_clean_validate.srt`
- reviewed: `<language>_ocr/fuse_clean_validate_review.srt`
- JSON: `<language>_ocr/lang/<language-code>/review.json`

Text-source review commonly uses `clean.srt` and `clean_review.srt`. Guided
transcription review commonly uses:

- target: `<language>_transcribe/transcribe_clean.srt`
- guide: `<guide-language>_ocr/fuse_clean_validate_review_flatten.srt`
- JSON: `<language>_transcribe/lang/<language-pair>/guided_review/<device>.json`

Traditional paths additionally use the reviewed Hant track, its flattened and
simplified output, and `simplify_review.json`. Dual paths additionally use the
independent Hans original, reviewed output, and review JSON. Discover actual
stems rather than assuming them. Confirm every selected SRT exists.

## Generate the report

Always set `UV_CACHE_DIR=/tmp/uv-cache`.

Regular review:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit review \
  --original <original.srt> \
  --reviewed <reviewed.srt> \
  --json <review.json> \
  --filter changes \
  --outfile local/<dataset>_review_audit.md \
  --overwrite
```

The JSON is optional for regular review unless using `--filter unverified`.
Guided review:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit review \
  --original <target.srt> \
  --guide <guide.srt> \
  --json <guided-review.json> \
  --filter all \
  --outfile local/<dataset>_guided_review_audit.md \
  --overwrite
```

Traditional-to-simplified review:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit review-trad \
  --traditional <traditional.srt> \
  --traditional-reviewed <traditional-reviewed.srt> \
  --traditional-simplified <simplified-traditional.srt> \
  --traditional-simplified-reviewed <simplified-traditional-reviewed.srt> \
  --traditional-json <review.json> \
  --traditional-simplified-json <simplify-review.json> \
  --filter changes \
  --outfile local/<dataset>_review_trad_audit.md \
  --overwrite
```

Parallel review:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit review-dual \
  --simplified <simplified.srt> \
  --simplified-reviewed <simplified-reviewed.srt> \
  --traditional <traditional.srt> \
  --traditional-reviewed <traditional-reviewed.srt> \
  --traditional-simplified <simplified-traditional.srt> \
  --traditional-simplified-reviewed <simplified-traditional-reviewed.srt> \
  --simplified-json <simplified-review.json> \
  --traditional-json <traditional-review.json> \
  --traditional-simplified-json <simplify-review.json> \
  --filter changes \
  --outfile local/<dataset>_review_dual_audit.md \
  --overwrite
```

Regular, guided, and traditional review support `all`, `changes`, and
`unverified`; dual review additionally supports `discrepancies`. All default to
`changes`. The `unverified` filter requires the corresponding JSON for every
review path. Use inclusive `--first-index` and `--last-index`. `--characters`
is available for regular, traditional, and dual review, with script variants
added automatically; use it only for a requested or suspected conversion issue.

Use `--first-block` and `--last-block` for an inclusive, one-based workflow
block range. In guided review these are paired target/guide blocks; in regular,
traditional, and dual review they are blocks from the first review input. Block
and subtitle ranges are mutually exclusive. Omit either bound for an open-ended
range.

## Audit regular and multi-path reviews

Read the relevant language policy before judging rows:

- Standard Chinese: [references/zho.md](references/zho.md)
- Cantonese: [references/yue.md](references/yue.md)
- English: apply ordinary proofreading judgment without Chinese conversion
  rules.

Check incorrect edits, missed corrections, script leakage, lexical and OCR
errors, grammar, punctuation, and whitespace. Begin accepted edits with `OK;`,
rejected edits with `Incorrect;`, and unresolved cases with `Check;`. Keep notes
terse and use arrow notation for simple substitutions.

Review stages must preserve source punctuation and whitespace exactly. When a
text correction also changes either, keep the text correction but restore the
source formatting. Assign lexical, grammatical, semantic, OCR, and proper-name
corrections to the earliest review stage in that stage's script. Reserve later
simplification review for conversion-specific cleanup.

## Audit guided reviews

Guided reports contain `Index`, `Block`, `Guide`, `Target / revision`, `Notes`,
and `Verified`. The target appears above the proposed revision; `(unanswered)`
means the JSON case has no answer. For a proposed revision, the generated
`Notes` cell contains that revision's JSON note; replace it during the audit as
described above.

- Audit proposed revisions and no-revision decisions. An unchanged target is a
  decision, not an automatic pass.
- Use the guide as semantic evidence, not text to copy. Accept legitimate
  differences in vocabulary, syntax, particles, omissions, and segmentation.
- Reject punctuation-only or whitespace-only revisions at this stage.
- Write exactly `OK` for an appropriate proposed revision. Leave a correct
  no-revision row blank. Otherwise use `Incorrect revision;`,
  `Missed revision;`, or `Uncertain;`.
- For substitutions, add the smallest relevant tone-marked Yale reading for
  `yue-*` or Hanyu Pinyin reading for `zho-*`; do not guess uncertain readings.

The report's index is global, but revision indexes in JSON are query-local.
Always use the query-local `index` in JSON when editing an answer.

## Correct and verify cases

For regular, traditional, and dual review, edit the JSON decision at the
earliest applicable stage and regenerate every downstream artifact. For guided
review, add, replace, or remove only necessary revision objects; keep them
unique and in ascending query-local order.

Mark `verified: true` only after auditing every subtitle in the JSON case and
correcting its complete answer. Never verify unanswered, unaudited, or partly
audited cases, including a case only partly covered by the requested range.

After corrections, regenerate through the dataset workflow, rerun the audit,
confirm canonical JSON, and verify corrected cases leave `--filter unverified`
where that filter is available.
