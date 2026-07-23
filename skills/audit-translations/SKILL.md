---
name: audit-translations
description: Audit Scinoephile standard, gapped, or guided translation JSON against the exact source, target-context, and guide SRT files used to generate it. Use when inspecting translation, gap_translation, or guided_translation JSON; judging translated, empty, unnecessary, or unanswered outputs; filtering by verification state; or correcting and verifying translation cases.
---

# Audit Translations

Run commands from the repository root. Select the workflow from the JSON and
the inputs that produced it; do not infer it from language alone.

## Select the inputs

| Workflow | Required SRT inputs |
|---|---|
| Standard translation | source track |
| Translation of missing target positions | gapped target and complete guide |
| Translation using target-language guide context | source and guide |

The `scinoephile audit translation` command infers the workflow from the SRT
inputs.

## Required report file

Save the complete Markdown report under `local/`, audit every row, and write
each finding into its `Notes` cell.

Standard and guided reports have exactly: `Indexes`, `Case / block`,
`Difficulty`, `Source`, `Guide`, `Translation`, `Notes`, `Verified`. Gapped
reports have exactly: `Indexes`, `Case / block`, `Difficulty`, `Guide`,
`Target context`, `Translation`, `Notes`, `Verified`.

- In standard and guided reports, `S` is the global source index and `Q` is
  its query-local JSON index; guided `G` labels are query-local guide indexes.
  In gapped reports, `G` is the global guide index and `Q` is its query-local
  JSON index. Always use `Q` when editing an answer.
- `C` is the one-based JSON case position and `B` the reconstructed block.
- `✓` means the entire JSON case is verified, not merely one displayed row.
- Keep findings beside rows, validate the edited report, and provide its link.
  Do not paste the table inline unless the user requests it.

## Protect source data

- Never edit files under `test/data/<dataset>/input/`.
- For an audit-only request, do not modify input SRTs, JSON, generated
  translations, or downstream review artifacts.
- When corrections are requested, edit JSON answers and verification metadata,
  then regenerate outputs. Never hand-edit a generated translated SRT.
- Preserve every JSON query exactly.

## Locate exact inputs

Standard translation uses the source SRT passed to the regular translator and
its `translation.json`. Guided translation uses the source and guide SRTs
passed to guided translation and its `guided_translation/<device>.json`.

Gapped translation uses:

- target: the gapped target before translation, commonly
  `transcribe_clean_review.srt` or `transcribe_review.srt`
- guide: the complete source-language SRT used to identify gaps
- JSON: `<target-output>/lang/<target-source>/gap_translation/<device>.json`

Never pass the already gap-translated output as `--target`; doing so removes
the gaps the audit must reconstruct.

## Generate the report

Always set `UV_CACHE_DIR=/tmp/uv-cache`.

Standard:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit translation \
  --source <source.srt> \
  --json <translation.json> \
  --filter all \
  --outfile local/<dataset>_translation_audit.md \
  --overwrite
```

Gapped:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit translation \
  --target <gapped-target.srt> \
  --guide <complete-guide.srt> \
  --json <gap_translation/device.json> \
  --filter all \
  --outfile local/<dataset>_gap_translation_audit.md \
  --overwrite
```

Guided:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit translation \
  --source <source.srt> \
  --guide <target-language-guide.srt> \
  --json <guided_translation/device.json> \
  --filter all \
  --outfile local/<dataset>_guided_translation_audit.md \
  --overwrite
```

Use inclusive `--first-index` and `--last-index`. They refer to global source
indexes in standard and guided workflows, and global guide indexes in the gapped
workflow.
Use `--first-block` and `--last-block` for inclusive, one-based workflow block
ranges: source blocks in the standard workflow and paired blocks in guided or
gapped workflows. Block and subtitle bounds may be combined; their intersection
determines the displayed rows. Omit either bound for an open-ended range.
Use `--filter unverified` to resume verification; the default is `all`.

`(unanswered)` means the case has no answer. In the gapped workflow, `(empty)`
is an answered output that intentionally emits no target subtitle.

## Audit every translation

Judge whether each output accurately and idiomatically expresses its source in
the intended target language and script.

- Check omissions, additions, mistranslations, polarity, modality, pronouns,
  names, numbers, register, terminology, continuity, and meaning-changing
  punctuation.
- Preserve natural target-language grammar rather than copying source syntax.
- In the guided workflow, use the guide as target-language context and semantic
  evidence, not as text that must be copied.
- In the gapped workflow, treat existing target subtitles as context, not as
  text to rewrite. Accept an empty output only when the guide position genuinely
  needs no target subtitle.
- Treat every unanswered case as incomplete.

Write exactly `OK` for a clearly appropriate translation. Otherwise begin with:

- `Incorrect translation;` for wrong, unsupported, unidiomatic, or wrong-script
  output
- `Missing translation;` for an empty or unanswered gap that needs text
- `Unnecessary translation;` for a generated gap that should remain empty
- `Uncertain;` when the source, guide, target context, and optional audio do not
  establish the correct output

Audit every displayed row. Do not mark an unanswered row `OK`.

## Correct and verify cases

When corrections are requested:

- For standard and guided cases, keep one output for every source `Q` index in
  ascending order.
- For gapped cases, keep one output for every guide `Q` index absent from query
  targets; use an empty string only for an intentional no-subtitle result.
- Mark `verified: true` only after auditing and correcting every output in the
  case. Do not verify a case when the selected range contains only some rows.
- Never verify unanswered or unaudited cases.

Regenerate translated and downstream artifacts through the dataset workflow.
Rerun the corrected range, confirm canonical JSON, and confirm corrected cases
leave `--filter unverified` before linking the interpreted report.
