# MiMo Transcription Backend

MiMo transcription is an opt-in backend for Cantonese transcription workflows.
Whisper remains the default backend.

Scinoephile exposes MiMo through `yue transcribe-vs-zho` with
`--asr-backend mimo`. By default, MiMo inference runs in the Scinoephile process
and caches the loaded MLX model for subsequent audio blocks. Pass
`--mimo-worker-command` only when MiMo needs to run in a separate Python
environment.

## Runtime Modes

Use `--mimo-runtime` to choose the inference runtime:

- `auto`: use MLX on Apple Silicon and fail clearly elsewhere
- `mlx`: use the Apple Silicon MLX runtime

The initial MiMo implementation supports MLX only. CUDA support is intentionally
out of scope because the official CUDA path currently requires a separate Python
3.12, PyTorch, CUDA, and FlashAttention dependency stack. The default MiMo model
is `mlx-community/MiMo-V2.5-ASR-MLX`; passing `--mimo-model-name` overrides it.

The MiMo request includes the temporary WAV path, model name, tokenizer name,
runtime, language metadata, optional audio tag, and optional generation limits.
The response contains transcript text plus timing/runtime metadata. Scinoephile
then runs forced timestamp alignment and only accepts MiMo output when word
timings are recovered. If fallback is enabled, MiMo failures can fall back to
Whisper, and unusable Whisper output can fall back to MiMo.

## Generation Controls

MiMo defaults to `--mimo-language yue`. Use `--mimo-language auto` to pass
automatic language detection through to the MLX runtime. On KOB data, `auto`
reduced block-count CER in one first-10-block run but increased time-window CER
because it inserted substantially more text, so `yue` remains the safer default.

Use `--mimo-max-tokens` to override the MLX runtime's generation token limit.
The MLX MiMo default can truncate long audio blocks, so long staged audio should
set an explicit token limit or use chunking.

Use `--mimo-chunk-duration` and `--mimo-chunk-overlap` to transcribe long audio
blocks as shorter overlapping windows. The overlap is only context; Scinoephile
keeps segments whose midpoint falls inside each chunk's non-overlap core. A
practical starting point for KOB is:

```shell
--mimo-max-tokens 512 --mimo-chunk-duration 20 --mimo-chunk-overlap 1
```

## Timestamp Alignment Modes

Use `--mimo-aligner` to choose the timestamp aligner:

- `whisperx`: use WhisperX alignment as a reference implementation
- `ctc`: use Scinoephile's in-house CTC trellis aligner

WhisperX should usually run through `--mimo-aligner-worker-command` in a
separate environment because current WhisperX releases pin an older Torch and
Hugging Face dependency line than Scinoephile's `transcription` extra. The worker
reads JSON on stdin, writes a WhisperX-style alignment result on stdout, and can
be run directly from this source tree:

```shell
/path/to/whisperx/.venv/bin/python \
  /path/to/Scinoephile/scinoephile/audio/transcription/forced_alignment_worker.py
```

The in-house `ctc` aligner runs in the Scinoephile process and uses a Hugging
Face CTC model. By default it uses
`jonatasgrosman/wav2vec2-large-xlsr-53-chinese-zh-cn`; pass
`--mimo-aligner-model` to use a local or alternate checkpoint. Install the
`transcription` extra, or at least `torch` and `transformers`, before using this
mode.

MiMo output is cached after alignment as normal `TranscribedSegment` payloads, so
downstream subtitle splitting consumes the same timestamped segment objects used
by Whisper.

## Apple Silicon MLX Setup

Install the MLX MiMo dependency into the Scinoephile virtual environment for the
default in-process runtime:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv pip install \
  --python .venv/bin/python \
  'git+https://github.com/ailuntx/mlx-audio@feat/mimo-v25-asr' \
  huggingface-hub soundfile
```

Download the local model files:

```shell
mkdir -p /Users/karldebiec/Code/Scinoephile/local/mimo-mlx
UV_CACHE_DIR=/tmp/uv-cache uv run hf download \
  mlx-community/MiMo-V2.5-ASR-MLX \
  --local-dir /Users/karldebiec/Code/Scinoephile/local/mimo-mlx/models/MiMo-V2.5-ASR-MLX
UV_CACHE_DIR=/tmp/uv-cache uv run hf download \
  mlx-community/MiMo-Audio-Tokenizer \
  --local-dir /Users/karldebiec/Code/Scinoephile/local/mimo-mlx/models/MiMo-Audio-Tokenizer
```

Smoke-test the in-process runtime directly:

```shell
cd /path/to/Scinoephile
printf '%s' '{
  "audio_path": "/Users/karldebiec/Code/Scinoephile/local/mimo-mlx/yue_hello.wav",
  "model_name": "/Users/karldebiec/Code/Scinoephile/local/mimo-mlx/models/MiMo-V2.5-ASR-MLX",
  "runtime": "mlx",
  "language": "yue"
}' | UV_CACHE_DIR=/tmp/uv-cache uv run python \
  scinoephile/audio/transcription/mimo_worker.py
```

Use the in-process runtime from the CLI:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile yue transcribe-vs-zho \
  --media-infile INPUT.mp4 \
  --zho-infile INPUT.zho.srt \
  --asr-backend mimo \
  --mimo-runtime mlx \
  --mimo-model-name /Users/karldebiec/Code/Scinoephile/local/mimo-mlx/models/MiMo-V2.5-ASR-MLX \
  --mimo-aligner ctc \
  -o OUTPUT.yue.srt
```

To keep MiMo dependencies out of the main environment, create the same MLX setup
in a separate virtual environment and pass `--mimo-worker-command`. In that mode,
`MimoTranscriber` prepends the Scinoephile source root to the worker subprocess
`PYTHONPATH`, so the external MLX environment does not need an editable
Scinoephile install.

## KOB Benchmark

The staged KOB audio fixture can be benchmarked directly with
`yue benchmark-transcription`. If the candidate subtitle file already exists,
the command reuses it and only calculates CER.

Reuse the existing simplified Whisper candidate:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile yue benchmark-transcription \
  --audio-series-indir test/data/kob/output/yue-Hans_transcribe/audio \
  --zho-infile test/data/kob/output/zho-Hant_ocr/fuse_clean_validate_review_flatten_simplify_review.srt \
  --reference-infile test/data/kob/output/yue-Hans/timewarp_clean_flatten.srt \
  --candidate-outfile test/data/kob/output/yue-Hans_transcribe/test_simplified/transcribe.srt \
  --cer-outfile local/kob-whisper.cer.txt
```

Run a MiMo MLX smoke test on the first audio block:

```shell
mkdir -p local
rsync -a \
  test/data/kob/output/yue-Hans_transcribe/multilang/yue_zho/transcription/ \
  local/kob-transcription-test-cases/
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile yue benchmark-transcription \
  --audio-series-indir test/data/kob/output/yue-Hans_transcribe/audio \
  --zho-infile test/data/kob/output/zho-Hant_ocr/fuse_clean_validate_review_flatten_simplify_review.srt \
  --reference-infile test/data/kob/output/yue-Hans/timewarp_clean_flatten.srt \
  --candidate-outfile local/kob-mimo-mlx-ctc-block0.srt \
  --cer-outfile local/kob-mimo-mlx-ctc-block0.cer.txt \
  --asr-backend mimo \
  --mimo-runtime mlx \
  --mimo-model-name /Users/karldebiec/Code/Scinoephile/local/mimo-mlx/models/MiMo-V2.5-ASR-MLX \
  --mimo-tokenizer-name /Users/karldebiec/Code/Scinoephile/local/mimo-mlx/models/MiMo-Audio-Tokenizer \
  --mimo-aligner ctc \
  --mimo-max-tokens 512 \
  --mimo-chunk-duration 20 \
  --mimo-chunk-overlap 1 \
  --cer-window time \
  --test-case-directory local/kob-transcription-test-cases \
  --stop-at-idx 0
```

Remove `--stop-at-idx 0` for the full KOB MiMo run. In-process MiMo loads the
MLX model once and reuses it across the full 188-block run.

`--cer-window block` is the historical behavior and compares the same number of
subtitle blocks in the reference and candidate. For staged audio experiments,
`--cer-window time` is usually fairer because it compares all reference and
candidate subtitles whose timestamps overlap the processed audio blocks.

## WhisperX Reference Setup

Use a separate WhisperX environment when comparing against the in-house CTC
aligner:

```shell
mkdir -p /Users/karldebiec/Code/Scinoephile/local/whisperx
UV_CACHE_DIR=/tmp/uv-cache uv venv \
  --python 3.13 \
  /Users/karldebiec/Code/Scinoephile/local/whisperx/.venv
UV_CACHE_DIR=/tmp/uv-cache uv pip install \
  --python /Users/karldebiec/Code/Scinoephile/local/whisperx/.venv/bin/python \
  'whisperx>=3.8.5'
```

Run MiMo with WhisperX alignment:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile yue transcribe-vs-zho \
  --media-infile INPUT.mp4 \
  --zho-infile INPUT.zho.srt \
  --asr-backend mimo \
  --mimo-runtime mlx \
  --mimo-aligner whisperx \
  --mimo-aligner-worker-command "/Users/karldebiec/Code/Scinoephile/local/whisperx/.venv/bin/python /path/to/Scinoephile/scinoephile/audio/transcription/forced_alignment_worker.py" \
  -o OUTPUT.whisperx.yue.srt
```

Run the same input with the in-house aligner:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile yue transcribe-vs-zho \
  --media-infile INPUT.mp4 \
  --zho-infile INPUT.zho.srt \
  --asr-backend mimo \
  --mimo-runtime mlx \
  --mimo-aligner ctc \
  -o OUTPUT.ctc.yue.srt
```
