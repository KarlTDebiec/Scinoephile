---
name: audit-aligned-subtitle-diffs
description: Audit character-aligned subtitle differences between a transcription and a non-authoritative reference, optionally using a timing-aligned guide for context. Use when evaluating transcription accuracy, explaining character-error-rate differences, distinguishing transcription errors from reference errors or acceptable variants, or inspecting aligned subtitle diff reports.
---

# Audit Aligned Subtitle Diffs

Run commands from the repository root. This audit judges every displayed
difference between a transcribed subtitle series and a comparison reference.
The reference is evidence, not an absolute source of truth. Use linguistic and
contextual judgment to decide which text is preferable.

## Required report file

Always save the complete Markdown report under `local/`. Add each audit note
directly to the generated file's `Notes` cell. Do not leave notes only in
commentary, tool output, or the final response.

- Keep exactly three columns: `Indexes`, `Alignment`, and `Notes`.
- Keep the optional original, transcription, reference, and optional guide
  stacked together in the single `Alignment` column.
- Do not add a `Verified` column or a separate findings section.
- Preserve the generated character alignment, including full-width and
  half-width placeholder spaces.
- Validate the edited report, then provide a clickable link to it. Do not paste
  the table inline unless the user explicitly requests it.

## Protect source data

- Never edit files under `test/data/<dataset>/input/`.
- An audit-only request is read-only: do not alter subtitle series, workflow
  JSON, caches, or generated outputs.
- When the user requests corrections, trace each error to the earliest
  responsible transcription stage, update that source or test case, and
  regenerate downstream outputs. Do not hand-edit a generated final SRT.

## Generate the report

Always set `UV_CACHE_DIR=/tmp/uv-cache`:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit aligned-diff \
  --original <optional-original.srt> \
  --transcription <transcription.srt> \
  --reference <reference.srt> \
  --guide <optional-guide.srt> \
  --first-index <first> \
  --last-index <last> \
  --filter changes \
  --outfile local/<dataset>_aligned_diff_audit_<first>-<last>.md \
  --overwrite
```

Omit `--original` or `--guide` when that track is unavailable. Original text is
shown for source subtitles whose timings overlap the target row, so it may have
different segmentation or subtitle counts. Each transcription subtitle must
have a unique exact-timing match in the optional guide; the guide may contain
additional subtitles. The index bounds are inclusive and refer to transcription
subtitle indexes.
Reference-only insertions that overlap the selected transcription time window
are also included. Omit either bound for an open-ended range.

Use `--first-block` and `--last-block` for an inclusive, one-based range of
transcription blocks. Block bounds may be used instead of subtitle bounds or
combined with them; when combined, both selections apply. Omit either block
bound for an open-ended block range.

The default `--filter changes` is appropriate for a difference audit. Use
`--filter all` only when unchanged aligned rows are needed for context. Adjust
`--similarity-cutoff` only when the default `0.6` pairs replacement blocks
poorly.

The `Indexes` cell labels transcription indexes with `T` and reference indexes
with `R`. The `Alignment` cell labels rows with optional original `O`,
transcription `T`, reference `R`, and optional guide `G`, in that order. Blank
space inserted into `T` or `R` is an alignment placeholder, not subtitle
content.

## Audit every row

Read the saved report from beginning to end and write a note for every changed
row. Judge wording, character choice, omissions, additions, punctuation, and
segmentation. Consult surrounding subtitles when the isolated row is
ambiguous. If no correction is warranted, write exactly `OK`; do not add an
"Acceptable variation" label or explanatory filler.

Do not assume a difference is a transcription error merely because it
contributes to CER. The official reference may be wrong, less idiomatic, or a
different acceptable rendering. The optional guide supplies semantic context;
it is not target-language surface-text authority.

Treat optional Cantonese sentence-final particles and interjections as
acceptable variation when they do not change the line's meaning. This includes
their addition, omission, and ordinary spelling variation, such as `呀`, `啦`,
`喇`, `喎`, and an opening `嘩`. Do not mark these as uncertain or erroneous
without separate evidence of a material lexical or semantic difference. Mark
such rows `OK`.

For rows that require a finding, begin the note with one of these
classifications:

- `Transcription error;` when the transcription should be corrected.
- `Reference error;` when the transcription is preferable and the comparison
  reference should be corrected.
- `Alignment error;` when the diff paired text incorrectly or the displayed
  row cannot be judged without a different alignment.
- `Uncertain;` when the available text and context cannot resolve the reading.

Explain the material difference concisely after the classification. A row may
contain more than one difference; account for all of them in its note. Equal
rows shown with `--filter all` may retain a blank note.

Before finishing, verify that every generated changed row has either `OK` or a
classification note, the table still has exactly three columns, and no row or
alignment space was accidentally removed while editing the Markdown.
