---
name: run-transcription-workflow
description: "Run and verify Scinoephile's reference-guided transcription pipeline block by block using the command-line interface: audio extraction, transcription, delineation correction, punctuation correction, cleaning, guided review, and gapped translation when needed. Use when building or continuing a movie transcription from a provided media file and guide SRT, especially Cantonese transcription guided by Chinese subtitles. Requires an explicit existing media file; never discover media from machine-specific locations."
---

# Run Transcription Workflow

Run commands from the repository root. Build one cumulative, reviewed
transcription prefix at a time using only the `scinoephile` CLI. Do not call
`test/data/transcription.py`, dataset generation helpers, or workflow internals.

## Require inputs

Resolve these values before changing files:

- `media`: explicit existing media file supplied by the caller
- `guide`: exact reviewed, flattened guide SRT
- `output_dir`: transcription output directory
- `target_language` and `guide_language`
- `block`: one-based block to complete
- `stream_index`: optional explicit audio stream index
- `context`: optional prompt-ready movie context file
- `transcription_reference`: optional exact reviewed target-language SRT used
  only as audit evidence
- `state_stem`: stable filename stem reused by all JSON logs, such as `mps`
- optional LLM provider, LLM model, Whisper model, Demucs, or VAD overrides

Stop and request the missing media file if the caller did not provide one or it
does not exist. Never search a home directory, mounted volume, media library, or
other machine-specific location for it. The guide and output may be supplied
directly or unambiguously resolved from a supplied dataset root. Never edit
anything under `test/data/<dataset>/input/`.

Use one stable set of paths throughout the run:

```text
<output_dir>/audio/audio.wav
<output_dir>/transcribe.srt
<output_dir>/transcribe_clean.srt
<output_dir>/transcribe_clean_review.srt
<output_dir>/transcribe_clean_review_translate.srt
<output_dir>/lang/<target_language>_<guide_language>/transcription/delineation/<state_stem>.json
<output_dir>/lang/<target_language>_<guide_language>/transcription/punctuation/<state_stem>.json
<output_dir>/lang/<target_language>_<guide_language>/guided_review/<state_stem>.json
<output_dir>/lang/<target_language>_<guide_language>/gap_translation/<state_stem>.json
```

Use language-family directory names for `<target_language>_<guide_language>`;
for example, `yue_zho` for `yue-Hant` guided by `zho-Hant`. Reuse an existing
state stem when continuing prior work. Create missing parent directories.

Before block 1, reuse an existing prompt-ready transcription context if the
caller or dataset provides one. Otherwise read
`../write-movie-context/SKILL.md` completely and use it once to create
`local/<dataset>_transcription_context.txt` for the target transcription
language. Reuse that file for every later block; do not repeat the research.
Do not invent a context merely from the film title when stronger subtitle or
canonical evidence is available.

## Read the stage guidance

Read each complete sibling skill immediately before auditing or correcting that
stage. Load only the next stage's skill; do not load all later audit skills up
front:

- `../audit-transcription-delineation/SKILL.md`
- `../audit-transcription-punctuation/SKILL.md`
- `../audit-subtitle-reviews/SKILL.md`
- `../audit-translations/SKILL.md`

Follow their scope, report shape, correction, and verification rules. For
Cantonese guided review, also read the Yue reference required by the subtitle
review skill. This orchestration is a correction-and-verification request, not
an audit-only request: fix incorrect JSON answers and mark a case verified only
after inspecting the complete case. Never hand-edit generated SRT files.

When an exact reviewed target-language subtitle track is available, use it as
additional evidence during guided review and gap review. Do not pass it into
generation commands, assume it overrides clearly different audio, or modify it.

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
existing WAV on later blocks; do not extract it again. Never overwrite it unless
the supplied media or selected stream changed.

## Process one block

Begin a requested block with step 1 below, even when earlier blocks and their
JSON state already exist. Do not generate a preflight audit to test whether the
new block has been processed; an audit against the previous cumulative prefix
will only create a misleading zero-row report.

For block `N`, every generation command must process the cumulative prefix with
`--last-block N`. Do not pass `--first-block N` to transcription, review,
cleaning, or translation. Each command rebuilds its complete derived SRT; do
not concatenate block outputs. Use `--overwrite` only for these generated SRTs.

Preserve CLI defaults unless the caller explicitly supplied an override. Do not
invent `--demucs`, `--vad`, Whisper model, LLM provider, or LLM model settings
from the media format, stream description, device, or a performance guess.

Every audit must isolate the new block with both `--first-block N` and
`--last-block N`. Audit CLIs do not overwrite reports. Use names such as
`local/<dataset>_<stage>_block_N_pass_1.md` for intermediate correction passes,
then write the final interpreted state once to the canonical
`local/<dataset>_<stage>_block_N.md`. Do not delete and recreate the canonical
report during the loop.

Run dependent commands serially. A command that yields a live process or
session is still running: poll it until it exits, and require exit status 0
before reading its output or starting the next stage. The existence, size, or
modification time of an SRT or JSON file is not proof that its writer finished.
Never generate an audit from a partial generation run. On a nonzero exit,
diagnose or report the failure before continuing.

### 1. Transcribe

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile transcribe \
  <output_dir>/audio/audio.wav \
  --reference-infile <guide> \
  --language <target_language> \
  --reference-language <guide_language> \
  --last-block N \
  --delineation-json <delineation_json> \
  --punctuation-json <punctuation_json> \
  --outfile <output_dir>/transcribe.srt \
  --overwrite
```

Add the context and requested model/provider/audio-processing overrides to every
applicable LLM command. Do not pass the original media to transcription after
the stable WAV exists.

When `context` is present, add
`--llm-additional-content-file <context>` to transcription, guided review, and
gapped translation. Reuse the same context only when it is written for all
three target-language operations; otherwise use the operation-specific files
provided by the caller.

### 2. Audit and correct delineation

Generate a complete block report using `--filter all`, inspect every row under
the delineation skill, correct the delineation JSON, and rerun cumulative
transcription. Repeat the report and correction loop until the selected block
has no delineation errors or unresolved cases and all fully audited cases are
verified.

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit delineation \
  --reference <guide> \
  --json <delineation_json> \
  --first-block N --last-block N \
  --filter all \
  --outfile local/<dataset>_delineation_block_N_pass_1.md
```

Always rerun transcription after a delineation edit before auditing
punctuation; a boundary correction may change punctuation queries.

### 3. Audit and correct punctuation

Generate the punctuation report from the latest `transcribe.srt`, inspect every
row under the punctuation skill, correct and verify the punctuation JSON, then
rerun cumulative transcription. Repeat until clean.

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit punctuation \
  --reference <guide> \
  --target <output_dir>/transcribe.srt \
  --json <punctuation_json> \
  --first-block N --last-block N \
  --filter all \
  --outfile local/<dataset>_punctuation_block_N_pass_1.md
```

### 4. Clean and guided-review

Rebuild the cleaned cumulative transcription:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile process \
  --infile <output_dir>/transcribe.srt \
  --language <target_language> \
  --clean \
  --outfile <output_dir>/transcribe_clean.srt \
  --overwrite
```

Run cumulative guided review:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile review \
  <output_dir>/transcribe_clean.srt \
  --guide-infile <guide> \
  --language <target_language> \
  --guide-language <guide_language> \
  --last-block N \
  --json <guided_review_json> \
  --outfile <output_dir>/transcribe_clean_review.srt \
  --overwrite
```

Audit block `N` in guided mode with `--filter all`, including unchanged
decisions. Correct and verify the guided-review JSON, rerun cumulative review,
and repeat until clean.

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit review \
  --mode guided \
  --original <output_dir>/transcribe_clean.srt \
  --guide <guide> \
  --json <guided_review_json> \
  --first-block N --last-block N \
  --filter all \
  --outfile local/<dataset>_guided_review_block_N_pass_1.md
```

If an upstream correction changes transcription text, rebuild cleaning and all
later stages before trusting their reports.

### 5. Fill and audit gaps when present

Run gapped translation after guided review. It is applicable when guide
positions are absent from the reviewed target; if no gaps exist, the output may
remain unchanged and the block audit may contain no rows.

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile translate \
  <guide> \
  --gapped-infile <output_dir>/transcribe_clean_review.srt \
  --source-language <guide_language> \
  --target-language <target_language> \
  --last-block N \
  --json <gap_translation_json> \
  --outfile <output_dir>/transcribe_clean_review_translate.srt \
  --overwrite
```

Audit the original gapped target, never the gap-filled output. If rows exist,
inspect all of them, correct and verify the JSON, rerun cumulative translation,
and repeat until clean.

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit translation \
  --mode gapped \
  --target <output_dir>/transcribe_clean_review.srt \
  --guide <guide> \
  --json <gap_translation_json> \
  --first-block N --last-block N \
  --filter all \
  --outfile local/<dataset>_gap_translation_block_N_pass_1.md
```

## Finish the block

Before reporting completion:

1. Regenerate every downstream SRT affected by the final correction.
2. Rerun each block report to its canonical filename so it reflects the final
   JSON and SRT state. Also generate a uniquely named `--filter unverified`
   report for each stage and confirm it contains zero selected rows.
3. Confirm no fully selected case remains unverified; do not falsely verify a
   partial, unanswered, or uncertain case.
4. Confirm the four cumulative SRTs end within the selected guide prefix and
   contain all previously completed blocks.
5. Review `git diff` and `git status`; preserve unrelated work and never stage
   or commit unless requested.
6. Link the final interpreted reports and summarize corrections, remaining
   uncertainty, selected media stream, and whether gap translation was needed.

Do not advance to block `N + 1` until block `N` is fully regenerated and
verified. Treat any oversized-block error as the end of the guide rather than
silently clamping the range.
