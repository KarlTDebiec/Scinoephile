# Cantonese transcription

The `transcription` extra provides the six Cantonese recognition sources used by
`scinoephile transcribe`: Whisper, MiMo, Qwen3-ASR, SenseVoice, FireRedASR2, and
GLM-ASR. Recognition checkpoints and the MiMo audio tokenizer use immutable
revisions declared in the corresponding model specifications. MLX-Audio uses the
upstream 0.6.5 release.

## Windows x64 with NVIDIA CUDA

Use native x64 Python 3.13 and an NVIDIA GPU with compute capability 7.5 or newer.
Use NVIDIA driver 596.36 or newer for the tested lockfile. MLX's baseline CUDA 13
requirement is a driver from the 580 series or newer; see the
[MLX installation requirements](https://github.com/ml-explore/mlx/blob/v0.32.4/docs/src/install.rst).
FFmpeg and FFprobe must be available on `PATH` for media extraction.

Install from a repository checkout with uv so the lockfile, platform-specific
PyTorch index, and dependency correction apply:

```powershell
$env:UV_CACHE_DIR = "/tmp/uv-cache"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()
uv sync --locked --extra transcription
```

Windows installs both `mlx==0.32.4` and `mlx-cuda-13==0.32.4`. MLX's `cuda13`
extra selects its backend only on Linux. The backend wheel also declares NCCL
without a platform marker even though NCCL has no Windows wheel. The uv override
restricts NCCL to Linux, matching the
[upstream packaging correction](https://github.com/ml-explore/mlx/blob/main/setup.py).
Do not replace this installation with `pip install mlx[cuda13]` on Windows.

The Windows PyTorch and TorchAudio packages come from the official
[`cu130` wheel index](https://download.pytorch.org/whl/cu130).
The tested lockfile selects PyTorch 2.14.1+cu130 and TorchAudio 2.11.0+cu130.
PyPI CPU-only Torch wheels are insufficient for this CUDA configuration.

Verify both accelerators before downloading recognition models:

```powershell
uv run --locked --extra transcription python -c "import torch; assert torch.cuda.is_available(); print(torch.__version__, torch.cuda.get_device_name()); print((torch.ones((8, 8), device='cuda') @ torch.ones((8, 8), device='cuda'))[0, 0].item())"
uv run --locked --extra transcription python -c "import mlx.core as mx; assert mx.cuda.is_available(); mx.set_default_device(mx.gpu); x = mx.ones((8, 8)) @ mx.ones((8, 8)); mx.eval(x); print(mx.device_info()); print(x[0, 0].item())"
```

Both matrix operations should return `8.0`. A missing native MLX backend produces
a dependency error naming the matching packages and driver requirement before
Scinoephile downloads a recognition checkpoint.

### GPU residency

On Windows, the production pipeline releases recognition weights after each
source. MLX recognition weights are released before forced alignment, and CTC
weights are released between sources and after consensus timing. All sources,
Whisper's decoding recovery, and consensus timing share one CTC aligner. Its
processor and persistent alignment cache remain available when weights unload.
Recognition weights reload for uncached blocks; this trades loading time for
bounded GPU residency.

The Apple Silicon path retains models between calls. Callers constructing
`MlxAudioModel` directly can select `release_after_inference=True`, and callers
constructing `MultiSourceTranscriber` directly can select
`release_source_models=True` when residency must be bounded.

### Running the CLI

Select the correct audio stream explicitly when a video includes dubbed tracks
or commentary. To inspect available streams:

```powershell
ffprobe -v error -show_entries stream=index,codec_type:stream_tags=language,title -of json "movie.mkv"
```

For a local Cantonese WAV, this command exercises all six sources, alignment,
deterministic consensus, and subtitle output without an LLM API request:

```powershell
uv run --locked --extra transcription scinoephile transcribe `
  --media-infile "cantonese.wav" --language yue-Hant `
  --block-vad-implementation silero --diarization off `
  --language-identification off --audio-events off --llm-no-op `
  --cache-dir "local/transcription-cache" --outfile "local/transcription.srt"
```

The command also writes `.alignment.json` and `.run.json` sidecars. Inspect each
alignment block's source rows and `source_errors` to distinguish contributing
recognizers from failed or rejected output. Deterministic consensus validates
the local pipeline; remove `--llm-no-op` and configure a provider for LLM consensus.
Optional diarization, language identification, and audio-event analysis have
separate model requirements and were disabled for the CUDA recognition benchmark.

### ACOPOPB benchmark

The native Windows benchmark uses the supplied *A Chinese Odyssey Part One
Pandora's Box (1995)* remux, original mono audio stream 3, from 120 through 165
seconds. Extract the input with:

```powershell
ffmpeg -hide_banner -loglevel error -ss 120 -i "movie.mkv" `
  -map 0:3 -t 45 -ar 16000 -ac 1 -c:a pcm_s16le "acopopb-120s-45s.wav"
```

Run the CLI command above with this WAV and an empty transcription cache.
Pre-download model snapshots when measuring inference separately from network
transfer. Sample total device memory with `nvidia-smi
--query-gpu=memory.used --format=csv,noheader,nounits --loop-ms=250` in a separate
terminal while the CLI runs. This measures sampled resident device memory,
including desktop use and both runtimes; it is not an allocator-only peak or a
guarantee for longer inputs.

The initial 10-second probes verified Qwen3-ASR plus Cantonese CTC alignment,
Whisper, and MiMo plus Cantonese CTC alignment on the RTX 3070 Laptop GPU.
Their sampled peaks were 3,128 MiB, 7,424 MiB, and 7,916 MiB respectively.
Those probes retained loaded weights; the production Windows pipeline instead
releases weights between recognition and timing. MiMo's upstream loader accepted
the pinned local audio-tokenizer weights with strict loading.

The complete CLI run on November 20, 2026 used CPython 3.13.5, NVIDIA driver
596.36, the locked dependencies above, and an 8,192 MiB RTX 3070 Laptop GPU.
Model snapshots were already downloaded, and the transcription cache was empty.
The 44.999-second extracted input produced four speech blocks and nine subtitles
in 227.6 seconds. Peak sampled total device memory was **7,863 MiB**.

| Recognition source | Contributing blocks | Timing |
| --- | --- | --- |
| Whisper large-v3 Cantonese | 4 / 4 | Whisper word timestamps |
| MiMo-V2.5-ASR | 4 / 4 | Cantonese CTC |
| Qwen3-ASR 0.6B 8-bit | 4 / 4 | Cantonese CTC |
| SenseVoiceSmall | 4 / 4 | Cantonese CTC |
| FireRedASR2-AED | 4 / 4 | Cantonese CTC |
| GLM-ASR-Nano 8-bit | 4 / 4 | Cantonese CTC |

Every block had an empty `source_errors` mapping. The output SRT matched the
validated alignment artifact, all subtitle intervals stayed inside the clip,
and the run manifest's alignment digest matched the artifact. Consensus was
deterministic; this run establishes runtime and output validity rather than
human-reviewed transcription accuracy. Longer films and optional analysis
models need separate memory measurements.

## Apple Silicon

On macOS with native arm64 Python 3.13, install with:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv sync --locked --extra transcription
```

The CUDA backend and PyTorch CUDA index are selected only on Windows x64. macOS
continues to use MLX Metal and the existing Torch device selection. Platform,
pinned-snapshot, model-loader, and local-tokenizer tests exercise this path with
mocked runtimes on Windows; a physical Apple Silicon inference run is still
required to verify the upstream runtime on that hardware.
