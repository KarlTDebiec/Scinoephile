---
name: audit-transcription-delineation
description: Audit Scinoephile transcription delineation logs by matching JSON reference pairs to their guide SRT subtitle indexes and judging whether target boundary shifts or no-shift answers align fixed target text appropriately. Use when inspecting transcription delineation mps.json or cuda.json files or identifying incorrect boundary decisions. Do not assess transcription accuracy.
---

# Audit Transcription Delineation

Run commands from the repository root. A delineation audit assesses whether
target text was divided appropriately across each pair of adjacent guide
subtitles. Treat the provided target text as fixed input, even when it appears
incorrect. Do not assess or comment on transcription accuracy, punctuation,
wording, or character choice; those are reviewed later in a separate workflow.

## Required report file

Always save the complete six-column Markdown report under `local/`. After
auditing every row, add each concise audit note directly to that file's `Notes`
cell. Do not leave notes only in commentary, tool output, or the final response.

- Keep the table at exactly these columns: `Indexes`, `Reference`, `Input`,
  `Output`, `Notes`, and `Verified`.
- Delineation JSON has no note field, so generated `Notes` cells begin blank.
  If a future schema populates one, read it as context and replace the entire
  cell with your own independent judgment; never append to or merely endorse
  generated note content. Leave the cell blank when a row needs no finding.
- Preserve the generated `Verified` cell: `✓` means the JSON test case is
  verified, and an empty cell means it is not verified.
- Do not add a separate findings section; keep each observation beside the row
  it describes.
- Validate the saved report after adding notes, then provide a clickable link
  to it in the final response. Do not paste the table inline unless the user
  explicitly requests it.

## Protect source data

- Never edit files under `test/data/<dataset>/input/`.
- For an audit-only request, do not edit delineation JSON, guide subtitles,
  transcription output, or validation sources.
- When corrections are requested, apply model-answer corrections to the
  relevant delineation JSON and regenerate downstream outputs.
- Treat guide or transcription-source corrections as separate changes and make
  them only when the user explicitly requests them.

## Locate artifacts

Find the exact guide SRT used during transcription and the logged delineation
JSON. Do not substitute a similarly named subtitle track. Transcription outputs
normally place delineation logs below a directory named `delineation`, with
provider-specific names such as `mps.json` or `cuda.json`.

The guide SRT is required because delineation JSON stores reference text but not
subtitle numbers. The CLI matches each logged reference pair to consecutive
guide subtitles and rejects absent or ambiguous matches rather than displaying
misleading indexes.

An official target-language subtitle track may be consulted only to determine
which utterance owns text near a boundary. It is not an input to the CLI and
does not belong in the report as a separate column. Never use it to evaluate or
comment on the accuracy of the target transcription.

## Generate the report

Always set `UV_CACHE_DIR=/tmp/uv-cache`:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit delineation \
  --reference <guide.srt> \
  --json <delineation.json> \
  --first-index <first> \
  --last-index <last> \
  --filter all \
  --outfile local/<dataset>_delineation_audit_<first>-<last>.md \
  --overwrite
```

On PowerShell, configure UTF-8 as directed by the repository `AGENTS.md` before
printing subtitles.

The index bounds are inclusive and retain only pairs wholly contained in the
requested range. Omit either bound for an open-ended range. The default
`--filter all` includes shifts, no-shift answers, and unanswered cases; use
`--filter changes` to show only decisions that moved the target boundary, or
`--filter unverified` when continuing verification of a partly audited file. A
complete audit must use `all`, because `changes` cannot reveal missed shifts.
The report summary labels these bounds as the reference subtitle range.

Use `--first-block` and `--last-block` for an inclusive, one-based range of
reference blocks. A boundary is included only when both reference subtitles
belong to selected blocks. Block and subtitle bounds are mutually exclusive.
Omit either block bound for an open-ended range.

Each table cell stacks the first and second subtitle with `<br>`. A blank line
is displayed as `—`. Sort rows by their matched subtitle indexes. Preserve the
original log order among repeated cases for the same boundary because they may
record successive decisions. An empty JSON answer (`{}`) means no boundary
shift was made; leave the output cell blank instead of repeating the input
pair. The CLI leaves `Notes` cells blank for interpretation during the audit.

## Audit every row

Read the saved report from beginning to end and judge every row independently.
The target characters may move across the boundary, but their concatenation
must remain unchanged. Assess whether the output divides the target speech more
faithfully between the meanings and utterances represented by the two guide
subtitles.

Judge only alignment. Ignore misspellings, mistranscriptions, Mandarinisms,
punctuation, omissions, repetitions, and other defects in the target text except
as fixed evidence for deciding which side of the boundary owns each phrase. Do
not mention these defects in Notes. Leave Notes blank when the shift or no-shift
answer is appropriate.

Use semantic and discourse alignment rather than literal word matching:

- Keep a phrase together when splitting it would damage its meaning or grammar.
- Do not move a Cantonese sentence-final particle solely because the guide lacks
  an equivalent token; attach it to the utterance it pragmatically completes.
- Treat vocatives, discourse markers, repetitions, and other speech absent from
  the guide according to their role in the target-language dialogue.
- Accept a no-shift answer when the input division is already the best available
  alignment; a change is not required merely because the two languages segment
  an idea differently.
- Flag a shift that makes alignment worse, and flag a no-shift answer when a
  clear phrase belongs on the other side of the boundary.

Classify alignment notes precisely:

- **Delineation error:** the model chose the wrong boundary or failed to shift a
  clearly misplaced phrase.
- **Uncertain:** the appropriateness of the boundary cannot be determined from
  the provided target text, guide pair, and available context.

After reviewing every row, fill the saved report's `Notes` cells wherever you
have an alignment observation. Begin each note with `Delineation error;` or
`Uncertain;`, followed by a concise explanation focused only on boundary
ownership. Leave the cell blank when the row needs no note. Validate that the
edited file retains every generated row and the exact six-column shape. Do not
claim the audit is complete until every row has been reviewed, all notes have
been written to the saved report, and its link is ready for the final response.

## Correct and verify cases

When the user requests corrections, update the delineation JSON answer rather
than a generated SRT:

- Correct the boundary output before marking the case verified.
- Mark a case `verified: true` only after auditing the entire boundary case and
  correcting its answer where necessary.
- Leave unanswered, unaudited, or partially audited cases unverified. Do not
  treat an empty no-shift answer as unanswered; only a missing answer is
  unanswered.

After corrections, regenerate the transcription output and downstream
artifacts through the dataset workflow. Rerun the audit over the corrected
range, confirm the JSON remains canonical, and confirm corrected cases no
longer appear with `--filter unverified` before linking the complete interpreted
report.
