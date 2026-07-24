# MiMo Transcription Backend

MiMo-V2.5-ASR is an alternative backend for reference-guided transcription.
Whisper remains the default. Select MiMo explicitly with `--backend mimo`;
Whisper is not invoked during that run.

Demucs and VAD apply to either backend. With MiMo, `--demucs auto` first tries
Demucs-separated audio and then the original audio if needed. `--vad auto`
first tries Silero VAD-filtered audio and then unfiltered audio if needed. The
`on` and `off` modes strictly enable or disable each preprocessing step.

If MiMo fails or produces unusable timestamped output, the block remains empty
for downstream gap translation.

## Runtime

The current implementation supports the MLX runtime on Apple Silicon. The
default model is `mlx-community/MiMo-V2.5-ASR-MLX`; it may instead be a local
path. MLX-Audio resolves the audio tokenizer from the model manifest or from a
sibling directory named `MiMo-Audio-Tokenizer`.

Install the MiMo-capable MLX-Audio branch:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv pip install \
  --python .venv/bin/python \
  'git+https://github.com/ailuntx/mlx-audio@feat/mimo-v25-asr'
```

Download local model files if desired:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run hf download \
  mlx-community/MiMo-V2.5-ASR-MLX \
  --local-dir /path/to/models/MiMo-V2.5-ASR-MLX
UV_CACHE_DIR=/tmp/uv-cache uv run hf download \
  mlx-community/MiMo-Audio-Tokenizer \
  --local-dir /path/to/models/MiMo-Audio-Tokenizer
```

MiMo can run in the Scinoephile process or through an isolated Python
environment. In-process inference caches the loaded model for subsequent
blocks. For an isolated environment, pass the full worker command with shell
quoting; Scinoephile adds its source root to the worker's `PYTHONPATH`.

## Timestamp Alignment

MiMo returns transcript text without word timestamps. Scinoephile accepts MiMo
output only after forced alignment produces `TranscribedSegment` and
`TranscribedWord` objects with usable timings.

The default `ctc` aligner runs in the Scinoephile process using Torch and
Transformers from the `transcription` extra. `whisperx` is also supported,
normally through a separate environment selected with
`--mimo-aligner-worker-command`.

Aligned MiMo output is cached separately from Whisper output using the audio,
model, runtime, generation, chunking, and aligner configuration.

## CLI

Run MiMo in the Scinoephile environment with the default CTC aligner:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile transcribe INPUT.mp4 \
  --reference-infile REFERENCE.srt \
  --language yue-Hant \
  --backend mimo \
  --mimo-runtime mlx \
  --mimo-model /path/to/models/MiMo-V2.5-ASR-MLX \
  --mimo-aligner ctc \
  -o OUTPUT.yue-Hant.srt
```

Run MiMo and WhisperX through isolated environments:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile transcribe INPUT.mp4 \
  --reference-infile REFERENCE.srt \
  --language yue-Hant \
  --backend mimo \
  --mimo-model /path/to/models/MiMo-V2.5-ASR-MLX \
  --mimo-worker-command \
    '/path/to/mimo/.venv/bin/python /path/to/Scinoephile/scinoephile/audio/transcription/mimo_worker.py' \
  --mimo-aligner whisperx \
  --mimo-aligner-worker-command \
    '/path/to/whisperx/.venv/bin/python /path/to/Scinoephile/scinoephile/audio/transcription/forced_alignment_worker.py' \
  -o OUTPUT.yue-Hant.srt
```

Relevant controls include:

- `--mimo-language`: MiMo language metadata; defaults to `yue`
- `--mimo-max-tokens`: generation-token limit
- `--mimo-chunk-duration`: optional chunk duration for long blocks
- `--mimo-chunk-overlap`: context overlap between chunks
- `--mimo-aligner-model`: alternate CTC or WhisperX alignment model

MiMo is used only when `--backend mimo` is selected; `--backend whisper` is the
default.
