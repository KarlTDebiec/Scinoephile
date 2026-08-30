---
name: audit-transcription
description: Audit Scinoephile multi-source transcription alignment artifacts, including ASR rows, speaker and pause annotations, merged subtitles, optional reference alignment, CER, and display-timing overlap. Use when inspecting alignment.json, evaluating consensus transcription, checking subtitle breaks, diagnosing source disagreement, or calibrating reference-free subtitle timing.
---

# Audit Transcription

Run commands from the repository root. Treat the alignment artifact as the
complete record of production evidence: source/model metadata, processing block
ranges, aligned ASR rows, speaker annotations, merged text, CTC speech timing,
final display timing, and tolerated source failures.

## Protect evaluation integrity

References are evaluation-only. Never provide reference text, boundaries, or
timing to transcription, multiple-sequence alignment, an aligned merge request,
or CTC alignment. It is safe to pass a reference only to the audit CLI after the
artifact and SRT have been generated.

Never edit files under `test/data/<dataset>/input/`. For an audit-only request,
do not modify the alignment artifact, generated SRT, or reference.

## Generate the report

Always set `UV_CACHE_DIR=/tmp/uv-cache`:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit transcription \
  --alignment <alignment.json> \
  --reference <name>=<independent-reference.srt> \
  --outfile local/<dataset>_transcription_audit.md \
  --overwrite
```

Omit `--reference` when reviewing production evidence without scoring it. Use
multiple `--reference NAME=PATH` arguments to compare named references. Use
`--first-block` and `--last-block` for an inclusive range of original block
numbers, or `--first-index` and `--last-index` for merged subtitle numbers. The
two range types are mutually exclusive. Request optional evidence rows with
`--include-merge-support`, `--include-speaker`, `--include-language`, or
`--include-audio-events`; request detailed timing tables with `--include-timing`.

The default row order is all available ASR sources, a separator, `merged`, and
then each named reference. The optional speaker row follows `merged`; support,
language, music, and singing rows follow the references. `　` is an ordinary
alignment gap, `・` is a shared timed pause unit whose duration is reported in
the summary, and `Ａ`/`Ｂ`/… are diarized speakers. `｜` appears only in a row
whose subtitle ends at that alignment position. All times are overall source
times.

## Interpret the report

Read every selected block and distinguish four kinds of issue:

- Source failure: a named ASR failed or emitted no usable text; consult the
  block's source-error message.
- Alignment issue: corresponding source characters occupy implausible columns,
  especially when Cantonese homophones or Simplified/Traditional forms should
  agree.
- Merge issue: the merged row omits supported speech, introduces unsupported
  text, chooses the wrong variant, or places an unnatural subtitle boundary.
- Timing issue: CTC speech bounds or display padding overlap the text-aligned
  reference poorly. Judge timing separately from text accuracy.

CER compares normalized lexical content across subtitle series and ignores
punctuation and whitespace.
Temporal IoU is the primary balanced timing metric; one-to-one IoU separately
checks unambiguous individual subtitle pairs so split/merge groups cannot hide
poor internal boundaries. Reference-time coverage is supplementary because it
can be increased merely by making subtitles longer. Start error is candidate
start minus reference start, and end error is candidate end minus reference end.
Positive start error means late entry; negative end error means early exit.

For subtitle-boundary assessment, compare the merged subtitle list with `｜`
positions and the text-aligned candidate/reference groups. Similar reference
breaks are evidence, not production instructions: accept a different break when
the merged Cantonese syntax, pause track, or speaker change supports it.

## Calibrate display timing

When experimenting with lead-in, lead-out, or minimum display duration, keep the
stored CTC speech bounds and merged text fixed. Evaluate one global setting over
all requested datasets, rank settings by aggregate temporal IoU, and report
per-dataset results so one title cannot hide a regression in another. Do not
tune each subtitle independently against its reference.

After selecting a policy, regenerate SRT and alignment artifacts from the same
reference-free pipeline. Then rerun this audit to verify that stored display
timing reflects the chosen global policy.

## Deliver the audit

Save substantial reports under `local/`, inspect the complete generated file,
and provide a clickable link. Summarize source failures, CER ordering, merge
errors, subtitle-break behavior, timing overlap, and remaining uncertainty. Do
not claim that reference-based evaluation changed production output.
