---
name: run-transcription-workflow
description: "Run and verify Scinoephile reference-guided transcription in consecutive block batches using the command-line interface, limited to audio extraction, transcription, delineation audit, and punctuation audit. Use when building or continuing a movie transcription from a provided media file and guide SRT without performing guided review or translation. Requires an explicit existing media file; never discover media from machine-specific locations."
---

# Run Transcription Audits

Run commands from the repository root. Build and verify one cumulative
transcription prefix at a time using only the `scinoephile` CLI. Stop after
delineation and punctuation. Do not run guided review or any translation stage.
Do not call `test/data/transcription.py`, dataset generation helpers, or workflow
internals.

## Require inputs

Resolve these values before changing files:

- `media`: explicit existing media file supplied by the caller
- `guide`: exact reviewed, flattened guide SRT
- `output_dir`: transcription output directory
- `target_language` and `guide_language`
- `first_block` and `last_block`: inclusive one-based block batch to complete
- `stream_index`: optional explicit audio stream index
- `context`: optional prompt-ready movie context file
- `state_stem`: stable filename stem reused by both JSON logs, such as `mps`
- optional Whisper model, Demucs, or VAD overrides

Stop and request the media file if the caller did not provide one or it does not
exist. Never search a home directory, mounted volume, media library, or another
machine-specific location for it. Resolve the guide and output directly from the
caller or an unambiguous supplied dataset root. Never edit anything under
`test/data/<dataset>/input/`.

Use one stable set of paths throughout the run:

```text
<output_dir>/audio/audio.wav
<output_dir>/transcribe.srt
<output_dir>/lang/<target_language>_<guide_language>/transcription/delineation/<state_stem>.json
<output_dir>/lang/<target_language>_<guide_language>/transcription/punctuation/<state_stem>.json
```

Use language-family directory names for `<target_language>_<guide_language>`;
for example, use `yue_zho` for `yue-Hant` guided by `zho-Hant`. Reuse an
existing state stem when continuing prior work. Create missing parent
directories.

Before the first batch, reuse an existing prompt-ready transcription context if
the caller or dataset provides one. Otherwise read
`../write-movie-context/SKILL.md` completely and use it once to create
`local/<dataset>_transcription_context.txt` in the target transcription
language. Reuse that file for every later batch; do not repeat the research.

## Protect evaluation integrity

Treat any target-language reference subtitle as evaluation-only data. Do not
open, search, align, quote, or otherwise consult it while transcribing or while
correcting delineation or punctuation JSON. Do not use CER to choose an answer.
Keep the target-language reference unavailable until the selected transcription
range is fully corrected and verified.

Use only these stage inputs:

- transcription: audio, guide, and optional movie context
- delineation audit: fixed transcription fragments and the guide
- punctuation audit: fixed transcription fragments and the guide

Delineation and punctuation audits do not assess transcription accuracy. Never
rewrite target words to resemble either the guide or an evaluation reference.

## Read the stage guidance

Read each complete sibling skill immediately before auditing or correcting that
stage. Load only the next stage's skill:

- `../audit-transcription-delineation/SKILL.md`
- `../audit-transcription-punctuation/SKILL.md`

Follow their scope, report shape, correction, and verification rules. This
orchestration is a correction-and-verification request: fix incorrect JSON
answers and mark a case verified only after inspecting the complete case. Never
hand-edit a generated SRT.

## Prepare audio once

If the stream index was not supplied, inspect the provided media:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile media probe \
  --infile <media>
```

Select the original target-language audio, excluding commentary and dubs. Ask
only if multiple plausible streams remain. Extract it once to the stable WAV:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile media extract-audio \
  --infile <media> \
  --stream-index <stream_index> \
  --outfile <output_dir>/audio/audio.wav
```

Omit `--stream-index` when the media has one unambiguous audio stream. Reuse an
existing WAV on later batches; do not extract it again. Never overwrite it
unless the supplied media or selected stream changed.

## Process one batch

Unless the caller requests another size, process consecutive batches of at most
five blocks. The final batch may contain fewer than five blocks, and a one-block
batch is valid. Let `A` and `B` be the inclusive first and last blocks in the
current batch.

Begin a requested batch with transcription even when earlier blocks and JSON
state already exist. Do not generate a preflight audit against the previous
cumulative prefix.

For batch `A-B`, every generation command must process the cumulative prefix
once with `--last-block B`. Do not launch separate cumulative commands for `A`,
`A + 1`, and so on, and do not pass `--first-block A` to transcription. The
command rebuilds its complete derived SRT; do not concatenate block outputs.
Use `--overwrite` only for the generated SRT.

Preserve CLI defaults unless the caller explicitly supplied an override. Do not
invent Demucs, VAD, or Whisper-model settings from the media format, stream
description, device, or a performance guess.

Every audit must isolate the new batch with `--first-block A` and
`--last-block B`. Use a stable canonical report such as
`local/<dataset>_<stage>_blocks_A_B.md` and pass `--overwrite` when refreshing it
after a correction.

Run dependent commands serially. Poll a live process until it exits, and require
status 0 before reading its output or starting the next stage. The existence,
size, or modification time of an SRT or JSON file is not proof that its writer
finished. On a nonzero exit, diagnose or report the failure before continuing.

### 1. Transcribe

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile transcribe \
  --media-infile <output_dir>/audio/audio.wav \
  --guide-infile <guide> \
  --language <target_language> \
  --guide-language <guide_language> \
  --last-block B \
  --delineation-json <delineation_json> \
  --punctuation-json <punctuation_json> \
  --outfile <output_dir>/transcribe.srt \
  --overwrite
```

Add `--llm-additional-content-file <context>` when context is present. Do not
pass the original media after the stable WAV exists.

If every Whisper candidate for a block is unusable, accept the empty block and
continue. Do not seed or alter Whisper caches, copy guide text into the output,
or hand-edit the generated SRT. Record the missing speech as an unresolved
transcription gap outside the delineation and punctuation scopes.

### 2. Audit and correct delineation

Generate a complete batch report using `--filter all`. Inspect every row under
the delineation skill, correct the delineation JSON, and rerun cumulative
transcription. Repeat until the selected batch has no delineation errors or
unresolved cases and every fully audited case is verified.

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit delineation \
  --reference <guide> \
  --json <delineation_json> \
  --first-block A --last-block B \
  --filter all \
  --outfile local/<dataset>_delineation_blocks_A_B.md \
  --overwrite
```

Always rerun transcription after a delineation edit before auditing
punctuation; a boundary correction may change punctuation queries.

### 3. Audit and correct punctuation

Generate the punctuation report from the latest `transcribe.srt`. Inspect every
row under the punctuation skill, correct and verify the punctuation JSON, and
rerun cumulative transcription. Repeat until clean.

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit punctuation \
  --reference <guide> \
  --target <output_dir>/transcribe.srt \
  --json <punctuation_json> \
  --first-block A --last-block B \
  --filter all \
  --outfile local/<dataset>_punctuation_blocks_A_B.md \
  --overwrite
```

## Finish the batch

Before reporting completion:

1. Rerun cumulative transcription after the final correction.
2. Refresh both canonical batch reports from the final JSON and SRT state.
3. Generate uniquely named `--filter unverified` reports for both stages and
   confirm each contains zero selected rows.
4. Confirm no fully selected case remains unverified; do not verify a partial,
   unanswered, or uncertain case.
5. Confirm `transcribe.srt` contains every previously completed batch and ends
   within the selected guide prefix.
6. Do not run `scinoephile review`, `scinoephile translate`, `audit review`, or
   `audit translation` as part of this skill.
7. Review `git diff` and `git status`; preserve unrelated work and never stage
   or commit unless requested.
8. Link the final interpreted delineation and punctuation reports and summarize
   corrections, remaining uncertainty, and the selected media stream.

Do not advance to the batch beginning at `B + 1` until batch `A-B` is fully
regenerated and verified. Treat an oversized-block error as the end of the guide
rather than silently clamping the range; retry only with the actual final block
as `B`.
