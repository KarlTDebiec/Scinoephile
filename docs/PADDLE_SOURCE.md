# Paddle source builds

Python 3.14 OCR uses the pinned Paddle development revision in
`pyproject.toml`. Published Python 3.13 wheels cannot be installed into this
runtime. Core installation and tests do not build Paddle; selecting an OCR extra
does. The first source build requires a native compiler and can take tens of
minutes.

The `paddle-build` dependency group supplies Python build tools. Paddle builds
without PEP 517 isolation because its metadata hook requires an existing CMake
configuration. Static dependency metadata lets `uv lock` resolve the optional
backends without compiling them. Keep that metadata aligned with
`python/requirements.txt` at the pinned Paddle revision when updating the pin.

## Apple Silicon CPU

Install the Xcode Command Line Tools before building. From the repository root:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv sync --locked --python 3.14 --group paddle-build
source .venv/bin/activate
export WITH_ARM=ON
export MAX_JOBS=6
export PYTHON_EXECUTABLE="$(python -c 'import sys; print(sys.executable)')"
export PYTHON_INCLUDE_DIR="$(python -c 'import sysconfig; print(sysconfig.get_path("include"))')"
export PYTHON_LIBRARY="$(python -c 'import sysconfig; from pathlib import Path; print(Path(sysconfig.get_config_var("LIBDIR")) / "libpython3.14.dylib")')"
UV_CACHE_DIR=/tmp/uv-cache uv sync --locked --group paddle-build --extra ocr
UV_CACHE_DIR=/tmp/uv-cache uv run --locked --group paddle-build --extra ocr python -c 'import paddle; print(paddle.__version__); paddle.utils.run_check()'
```

This builds a CPU runtime. Paddle does not supply an MPS OCR backend.

## Windows CUDA

Use an x64 Visual Studio developer shell with an installed CUDA toolkit and
cuDNN development libraries. Installing PyTorch CUDA packages alone does not
provide the native compiler toolchain. Keep the CUDA toolkit, Visual Studio
compiler, and cuDNN versions compatible with each other.

From the repository root in PowerShell:

```powershell
$env:UV_CACHE_DIR = "/tmp/uv-cache"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
uv sync --locked --python 3.14 --group paddle-build
$env:MAX_JOBS = "4"
$env:PYTHON_EXECUTABLE = (& .venv\Scripts\python.exe -c "import sys; print(sys.executable)")
$env:PYTHON_INCLUDE_DIR = (& .venv\Scripts\python.exe -c "import sysconfig; print(sysconfig.get_path('include'))")
$env:PYTHON_LIBRARY = (& .venv\Scripts\python.exe -c "import sys; from pathlib import Path; print(Path(sys.base_prefix) / 'libs' / 'python314.lib')")
uv sync --locked --group paddle-build --extra ocr-cuda
uv run --locked --group paddle-build --extra ocr-cuda python -c "import paddle; print(paddle.__version__); assert paddle.is_compiled_with_cuda(); paddle.utils.run_check()"
```

The CUDA build uses the installed toolkit and cuDNN instead of adding a second
set of pinned CUDA runtime packages through Paddle. If several CUDA toolkits are
installed, select the intended toolkit with `CUDA_TOOLKIT_ROOT_DIR` and put its
`bin` directory on `PATH` before building.

## Downstream projects

Direct Git requirements preserve the source pin in downstream dependency
metadata. uv's build variables, static dependency metadata, and isolation
settings are project configuration and do not propagate to dependent projects.
A downstream project that installs an OCR extra must carry the same build
configuration and supply the `paddle-build` tools before building Paddle.

## References

- [Pinned Paddle source](https://github.com/PaddlePaddle/Paddle/tree/abadcba928490aae564260a1eefc5a7279db5f3e)
- [Paddle macOS source build](https://www.paddlepaddle.org.cn/documentation/docs/en/install/compile/macos-compile-make_en.html)
- [Paddle Windows source build](https://www.paddlepaddle.org.cn/documentation/docs/en/install/compile/windows-compile_en.html)
- [uv build configuration](https://docs.astral.sh/uv/concepts/projects/config/)
