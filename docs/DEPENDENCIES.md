# Dependency compatibility

Scinoephile targets Python 3.13. Its NumPy API usage does not require NumPy 2.5;
the minimum is 2.1, the first NumPy release with
[Python 3.13 support](https://numpy.org/doc/2.1/release/2.1.0-notes.html).
NumPy is not overridden in `tool.uv.override-dependencies`, so native extensions
and optional backends participate in selecting a compatible version.

The lockfile resolves optional features together. The pinned
[FireRedASR2S source](https://github.com/FireRedTeam/FireRedASR2S/blob/4e7d9aaf4482a47cec1724807026b9b151926eb5/pyproject.toml)
requires NumPy 2.4.2, while PaddleX 3.7.2 requires NumPy below 2.4. To keep OCR
and transcription installable together, the lockfile selects NumPy 2.4.2,
PaddleOCR 3.4.1, and PaddleX 3.4.3. These older OCR releases support the PaddleOCR
3 API used by Scinoephile. The declared OCR version range remains unchanged;
future dependency updates may select newer compatible releases.

Validate dependency updates with `uv lock --check` and install the locked default,
`ocr`, and `ocr-cuda` feature sets in separate virtual environments. Run
`uv pip check` against each environment and exercise NumPy, Numba, and the Paddle
imports without constructing recognizers or downloading models. The CUDA feature
uses the Windows PaddlePaddle GPU wheel declared in `pyproject.toml`; test it on
Windows separately from the CPU feature to avoid installing both Paddle runtimes
into the same environment.
