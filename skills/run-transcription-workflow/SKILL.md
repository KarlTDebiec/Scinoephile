---
name: run-transcription-workflow
description: Run and verify Scinoephile aligned multi-source Cantonese transcription in hard-cut audio-block batches. Use when generating a consensus SRT and versioned alignment artifact from media, continuing a partial transcription, or evaluating the finished output against a Cantonese reference without leaking reference evidence into production.
---

# Run Aligned Transcription

Run commands from the repository root with
`UV_CACHE_DIR=/tmp/uv-cache uv run`. The production pipeline uses VAD only to
choose low-risk hard cut points, runs every configured ASR on each complete,
non-overlapping block without internal VAD, aligns their character/timing
evidence, asks the consensus LLM for text and subtitle splits, CTC-aligns that
result, and writes an SRT plus a versioned alignment artifact.

## Require inputs

Resolve the media file, target language, output SRT, output alignment JSON,
optional audio stream index, optional movie-context file, and inclusive audio
block range. Stop and ask for the media file when it was not supplied; never
search machine-specific media locations.

Use stable outputs:

```text
<output_dir>/transcribe.srt
<output_dir>/transcribe.alignment.json
<output_dir>/transcribe.run.json
<output_dir>/transcription.json
```

Never edit files under `test/data/<dataset>/input/`. Preserve existing caches
unless the caller explicitly asks to overwrite them.

## Protect evaluation integrity

A Cantonese reference is evaluation-only. Do not open it before production is
complete, and never pass its text, boundaries, timing, or subtitle count to ASR,
alignment, the merge LLM, CTC alignment, or speaker diarization. The reference
may be supplied only to the completed artifact's audit command.

The speaker row is evidence, not transcript text. `Ａ`/`Ｂ`/… represent diarized
speakers, `・` represents a shared timed pause unit whose duration is recorded
in the artifact, and `　` is an ordinary alignment gap.

## Run one cumulative batch

Unless the caller requests otherwise, process at most five new blocks per batch.
Let `B` be the inclusive last audio block in the cumulative prefix. Rebuild the
prefix once with `--last-block B`; do not concatenate per-block SRT files.

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile transcribe \
  --media-infile <media> \
  --language yue-Hant \
  --last-block B \
  --json <output_dir>/transcription.json \
  --outfile <output_dir>/transcribe.srt \
  --overwrite
```

Add `--stream-index` and `--llm-additional-context-file` only when supplied.
Preserve the default six-source registry, block planner, diarization, MiMo token
guard, and display timing unless the caller explicitly requests an experiment.
Poll until the command exits and require status 0 before auditing.

## Audit the artifact

Read `../audit-transcription/SKILL.md` completely before auditing.
Without a reference, inspect the production evidence directly:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit transcription \
  --alignment <output_dir>/transcribe.alignment.json \
  --first-block A --last-block B \
  --outfile local/<dataset>_alignment_blocks_A_B.md \
  --overwrite
```

After the production range is fixed, a separate evaluation may add
`--reference <name>=<cantonese-reference.srt>`. Review source failures, implausible
character alignment, omissions or hallucinations in the merged row, subtitle
breaks relative to pauses and speaker changes, CER, and temporal overlap.

Do not hand-edit the generated SRT or artifact. Fix pipeline code, source
configuration, prompt/test-case state, or global display-timing settings; then
regenerate the cumulative prefix and refresh the audit.

## Finish

Confirm that the SRT and artifact describe the same subtitle count and timing,
all artifact rows have equal widths, source failures are explicit, and the
selected range is complete. Review `git diff` and `git status`, preserve
unrelated work, and do not stage or commit unless requested. Link the final
audit and summarize block range, subtitle count, source failures, merged CER,
subtitle-break behavior, and timing overlap.
