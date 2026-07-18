---
name: audit-gap-translations
description: Audit Scinoephile gap-translation JSON against the exact gapped target and complete guide SRT files used to generate it. Use when inspecting gap_translation mps.json, cuda.json, or cpu.json files; filtering cases by difficulty or verification state; judging translations generated for missing target subtitles; finding mistranslated, unnecessary, empty, or unanswered gap outputs; or verifying corrected gap-translation test cases.
---

# Audit Gap Translations

Run commands from the repository root. Audit only target subtitles generated to
fill gaps. Treat existing target subtitles as context; do not review or rewrite
them during this audit.

## Required report file

Save the complete eight-column Markdown report under `local/`. Audit every row
and write each concise finding directly into that file's `Notes` cell.

- Keep exactly these columns: `Indexes`, `Case / block`, `Difficulty`, `Guide`,
  `Target context`, `Translation`, `Notes`, and `Verified`.
- `G` is the global one-based guide SRT index. `Q` is the query-local index used
  by the JSON output. `C` is the one-based JSON case position, and `B` is the
  reconstructed block number.
- Preserve the generated `Verified` cell. `✓` means the entire JSON case is
  verified, not merely that one displayed output was checked.
- Keep findings beside their rows rather than adding a separate findings table.
- Validate the saved report, then provide a clickable link. Do not paste the
  table inline unless the user explicitly requests it.

## Protect source data

- Never edit files under `test/data/<dataset>/input/`.
- For an audit-only request, do not edit the target, guide, translated output,
  JSON, or downstream reviewed subtitles.
- When corrections are requested, edit the relevant JSON output and verification
  metadata. Never hand-edit the generated gap-translated SRT.
- Preserve each JSON query exactly. Use the report's query-local `Q` index when
  editing an output; do not substitute the global `G` index.

## Locate the exact inputs

Find the same two series passed to `translate_series_gaps` and their persisted
test-case JSON:

- target: the gapped target-language SRT before translation, commonly
  `transcribe_clean_review.srt` or `transcribe_review.srt`
- guide: the complete source-language SRT used to identify and translate gaps
- JSON: `<target-output>/lang/<target_source>/gap_translation/<device>.json`

Do not pass `transcribe_clean_review_translate.srt` or another translated output
as `--target`; doing so removes the gaps the CLI must reconstruct. Do not
substitute a similarly named guide or a later reviewed guide.

## Generate the report

Always set `UV_CACHE_DIR=/tmp/uv-cache`:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit gap-translation \
  --target <gapped-target.srt> \
  --guide <complete-guide.srt> \
  --json <gap_translation/device.json> \
  --first-index <first> \
  --last-index <last> \
  --filter all \
  --difficulty <level> \
  --outfile local/<dataset>_gap_translation_audit_<first>-<last>.md
```

The inclusive one-based range refers to global guide SRT indexes and includes
only missing target positions within that range. Omit either bound for an
open-ended range. Use `--filter all` for a complete audit and
`--filter unverified` when resuming verification. The default is `all`.
Omit `--difficulty` to include every difficulty, or pass one or more exact
levels, such as `--difficulty 1 2`. Difficulty and verification filters compose.
Use difficulty to prioritize work, not as evidence that an output is correct or
incorrect. A case with any nonempty generated translation has minimum difficulty
1; explicit higher values are preserved.

The CLI reconstructs the same pause-delimited blocks and timing-overlap mapping
used by gap translation. It matches current JSON queries exactly, ignores older
queries only when a current case supersedes them, and rejects unmatched or
ambiguous selected cases rather than assigning misleading indexes.

Each row represents one missing target position. `Target context` contains the
nearest existing target subtitle before and after the gap when available.
`(empty)` is an answered output that intentionally emits no target text;
`(unanswered)` means the case has no answer.

## Audit every gap

Judge whether each translation accurately and idiomatically expresses the
corresponding guide subtitle in the target language while fitting the existing
target context.

- Preserve the requested target language and script.
- Preserve established names, terminology, register, speaker voice, and
  discourse continuity from nearby target subtitles.
- Translate the guide's meaning rather than copying its grammar or forcing
  source-language wording into the target language.
- Check omissions, additions, mistranslations, pronouns, names, numbers,
  polarity, modality, and punctuation that changes meaning.
- Treat existing target subtitles as contextual evidence, not as text to edit.
- Accept an empty output only when the guide position genuinely needs no target
  subtitle. Treat an unanswered case as incomplete.
- Consult surrounding guide and target SRT rows when the report's nearest-neighbor
  context is insufficient. Use audio only when available and necessary.

Write exactly `OK` for a clearly appropriate nonempty translation. Otherwise
begin the note with one of these labels and include only the material reason:

- `Incorrect translation;` for a wrong, unsupported, unidiomatic, or
  wrong-script output.
- `Missing translation;` when an empty or unanswered output omits content that
  should be translated.
- `Unnecessary translation;` when the output invents a target subtitle where
  the guide position should remain empty.
- `Uncertain;` when the available guide, target context, and optional audio do
  not establish the right output.

Audit every displayed row. Do not leave a nonempty translation without `OK` or
a finding. An acceptable empty output may use `OK`; an unanswered output must
not be marked `OK`.

## Correct and verify cases

When the user requests corrections, update the sparse JSON answer rather than a
generated SRT:

- Add or replace the output object with the report's query-local `Q` index.
- Keep output indexes unique and ascending, with exactly one output for every
  guide index absent from the query targets.
- Use an empty string only for an intentional no-subtitle result.
- Mark a case `verified: true` only after auditing and correcting every output
  in that case. Do not verify a case when the requested range includes only
  some of its gaps.
- Never mark an unanswered or unaudited case verified.

After corrections, regenerate the gap-translated SRT and downstream guided
review or translation artifacts through the dataset workflow. Rerun the audit
over the corrected range, confirm the JSON remains canonical, and link the
complete interpreted report.
