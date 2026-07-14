---
name: audit-transcription-delineation
description: Audit Scinoephile transcription delineation logs by matching JSON reference pairs to their guide SRT subtitle indexes and reviewing input/output target boundary shifts. Use when inspecting transcription delineation mps.json or cuda.json files, identifying incorrect shifts or no-shift answers, or distinguishing model errors from guide-subtitle and transcription errors.
---

# Audit Transcription Delineation

Run commands from the repository root. A delineation audit assesses whether
target text was divided appropriately across each pair of adjacent guide
subtitles; it does not assess punctuation or rewrite transcription text.

## Mandatory final output

If this skill runs an audit, paste the **entire five-column Markdown report
inline in the final response**. This is a non-negotiable completion requirement.

- Tool-call output, commentary, counts, findings, and a local file do not count
  as showing the report.
- A file link may supplement the inline report but must never replace it.
- Never omit or truncate rows, even when the report is long.
- Never wrap the report in a code fence.
- Keep the table at exactly these columns: `Subtitle indexes`, `Reference
  subtitles`, `Input target subtitles`, `Output target subtitles`, and `Notes`.
- Before responding, fill each row's `Notes` cell with your concise audit note
  when you have one. Leave it blank when the row needs no note.
- Do not add a separate findings section; keep each observation beside the row
  it describes.

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

An official target-language subtitle track may be consulted as secondary
evidence when available, but it is not an input to the CLI and does not belong
in the report as a separate column. Its timing, wording, or segmentation need
not match the transcription exactly.

## Generate the report

Always set `UV_CACHE_DIR=/tmp/uv-cache`:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit delineation \
  --reference <guide.srt> \
  --json <delineation.json> \
  --first-index <first> \
  --last-index <last>
```

For a large report, also save it under `local/` so it can be read completely:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit delineation \
  --reference <guide.srt> \
  --json <delineation.json> \
  --outfile local/<dataset>_delineation_audit.md
```

On PowerShell, configure UTF-8 as directed by the repository `AGENTS.md` before
printing subtitles.

The index bounds are inclusive and retain only pairs wholly contained in the
requested range. Omit either bound for an open-ended range. The default
`--filter all` includes shifts, no-shift answers, and unanswered cases; use
`--filter changes` to show only decisions that moved the target boundary. A
complete audit must use `all`, because `changes` cannot reveal missed shifts.

Each table cell stacks the first and second subtitle with `<br>`. A blank line
is displayed as `—`. Sort rows by their matched subtitle indexes. Preserve the
original log order among repeated cases for the same boundary because they may
record successive decisions. An empty JSON answer (`{}`) means no boundary
shift was made; display `—` in the output cell instead of repeating the input
pair. The CLI leaves `Notes` cells blank for interpretation during the audit.

## Audit every row

Read the saved report from beginning to end and judge every row independently.
The target characters may move across the boundary, but their concatenation
must remain unchanged. Assess whether the output divides the target speech more
faithfully between the meanings and utterances represented by the two guide
subtitles.

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

Classify notes precisely:

- **Delineation error:** the model chose the wrong boundary or failed to shift a
  clearly misplaced phrase.
- **Guide issue:** the reference pair itself is wrongly segmented, mistranslated,
  or missing material, so it is unreliable evidence for the target boundary.
- **Transcription issue:** the target wording appears wrong, but the boundary
  decision is reasonable for the provided target text. Record this separately;
  delineation must not rewrite it.
- **Uncertain:** audio or broader context is needed to distinguish plausible
  boundaries.

After reviewing every row, fill the saved report's `Notes` cells wherever you
have an observation. Begin each note with `Delineation error;`, `Guide issue;`,
`Transcription issue;`, or `Uncertain;`, followed by a concise explanation.
Leave the cell blank when the row needs no note. Paste the entire interpreted
report inline without adding a separate findings list. Do not claim the audit
is complete until every row has been reviewed and the complete report is
present in the final response.
