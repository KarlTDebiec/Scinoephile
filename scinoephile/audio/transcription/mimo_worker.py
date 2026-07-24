#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MiMo ASR runtime helpers and optional subprocess worker."""

from __future__ import annotations

import json
import platform
import sys
import time
import wave
from collections.abc import Mapping
from importlib import import_module
from pathlib import Path
from typing import Any, cast

try:
    from .mimo_runtime import MimoRuntime
except ImportError:
    from mimo_runtime import MimoRuntime  # ty: ignore[unresolved-import]

__all__ = [
    "main",
    "transcribe_with_mimo",
]

_MIMO_MLX_EXTRA_MESSAGE = (
    "MiMo MLX runtime requires mlx-audio with MiMo-V2.5-ASR support installed."
)
_MLX_MODEL_BY_REFERENCE: dict[str, Any] = {}
"""Loaded MLX MiMo models keyed by model reference."""


def main() -> int:
    """Run MiMo from JSON stdin to JSON stdout.

    Returns:
        process exit code
    """
    try:
        request = json.loads(sys.stdin.read())
        if not isinstance(request, Mapping):
            raise ValueError("MiMo request must be a JSON object.")
        payload = transcribe_with_mimo(request)
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(payload, ensure_ascii=False))
    return 0


def transcribe_with_mimo(request: Mapping[str, object]) -> dict[str, object]:
    """Transcribe one audio file using MiMo.

    Arguments:
        request: MiMo runtime request payload
    Returns:
        MiMo runtime response payload
    Raises:
        ValueError: if required request fields are missing
        ImportError: if MiMo runtime imports are unavailable
    """
    runtime = MimoRuntime(_get_optional_string(request, "runtime") or MimoRuntime.AUTO)
    if runtime == MimoRuntime.AUTO:
        runtime = _get_default_runtime()
    if runtime == MimoRuntime.MLX:
        return _transcribe_with_mlx(request)
    raise ValueError(f"Unsupported MiMo runtime: {runtime}")


def _get_default_runtime() -> MimoRuntime:
    """Get the platform-appropriate default MiMo runtime.

    Returns:
        MiMo runtime
    """
    if platform.system() == "Darwin" and platform.machine() in {"arm64", "aarch64"}:
        return MimoRuntime.MLX
    raise ValueError(
        "MiMo support currently requires Apple Silicon MLX. "
        "CUDA support is not included in this initial implementation."
    )


def _get_mlx_language(language: str | None) -> str | None:
    """Map Scinoephile language metadata to MLX MiMo language options.

    Arguments:
        language: requested language metadata
    Returns:
        MLX language code, if one should be passed
    """
    if language is None:
        return None
    lowered = language.lower()
    if lowered in {"auto", ""}:
        return None
    if lowered in {"yue", "yue-hant", "yue-hans", "zh", "zho", "zh-cn"}:
        return "zh"
    if lowered in {"en", "eng", "english"}:
        return "en"
    return None


def _get_mlx_load() -> Any:
    """Get the MLX-Audio STT model loader.

    Returns:
        MLX-Audio STT load function
    Raises:
        ImportError: if MLX-Audio is unavailable
    """
    try:
        mlx_stt = import_module("mlx_audio.stt")
    except ImportError as exc:
        raise ImportError(_MIMO_MLX_EXTRA_MESSAGE) from exc
    return getattr(mlx_stt, "load")


def _get_mlx_model(model_name: str) -> Any:
    """Get a cached MLX MiMo model.

    Arguments:
        model_name: model name or local path
    Returns:
        loaded MLX MiMo model
    """
    model_path = Path(model_name).expanduser()
    model_reference: str | Path = model_name
    if model_path.is_absolute() or model_name.startswith("~"):
        model_reference = model_path
    cache_key = str(model_reference)
    if cache_key not in _MLX_MODEL_BY_REFERENCE:
        load = _get_mlx_load()
        _MLX_MODEL_BY_REFERENCE[cache_key] = load(model_reference)
    return _MLX_MODEL_BY_REFERENCE[cache_key]


def _get_optional_number(source: object, key: str) -> float | None:
    """Get an optional numeric value from an object or mapping.

    Arguments:
        source: object or mapping to inspect
        key: value key or attribute name
    Returns:
        number as float, if present
    """
    if isinstance(source, Mapping):
        value = cast(Mapping[str, object], source).get(key)
    else:
        value = getattr(source, key, None)
    if isinstance(value, int | float):
        return float(value)
    return None


def _get_optional_int(source: object, key: str) -> int:
    """Get an optional integer-compatible value from an object or mapping.

    Arguments:
        source: object or mapping to inspect
        key: value key or attribute name
    Returns:
        integer value, or zero when absent
    """
    value = _get_optional_number(source, key)
    if value is None:
        return 0
    return int(value)


def _get_optional_positive_int(request: Mapping[str, object], key: str) -> int | None:
    """Get an optional positive integer field from a request mapping.

    Arguments:
        request: MiMo runtime request payload
        key: field key
    Returns:
        positive integer value, if present
    Raises:
        ValueError: if the value is malformed
    """
    value = request.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"MiMo request field {key!r} must be a positive integer.")
    return value


def _get_optional_string(request: Mapping[str, object], key: str) -> str | None:
    """Get an optional string field from a MiMo runtime request.

    Arguments:
        request: MiMo runtime request payload
        key: field key
    Returns:
        string value, if present
    Raises:
        ValueError: if the value is malformed
    """
    value = request.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"MiMo request field {key!r} must be a string.")
    return value


def _get_output_segments(source: object) -> list[object]:
    """Get transcript segment payloads from an MLX output object.

    Arguments:
        source: MLX output object
    Returns:
        segment payload list
    """
    if isinstance(source, Mapping):
        value = cast(Mapping[str, object], source).get("segments")
    else:
        value = getattr(source, "segments", None)
    if isinstance(value, list):
        return cast(list[object], value)
    return []


def _get_output_string(source: object, key: str) -> str | None:
    """Get an optional string value from an output object.

    Arguments:
        source: output object or mapping to inspect
        key: value key or attribute name
    Returns:
        string value, if present
    """
    if isinstance(source, Mapping):
        value = cast(Mapping[str, object], source).get(key)
    else:
        value = getattr(source, key, None)
    if isinstance(value, str):
        return value
    return None


def _get_required_string(request: Mapping[str, object], key: str) -> str:
    """Get a required string field from a MiMo runtime request.

    Arguments:
        request: MiMo runtime request payload
        key: field key
    Returns:
        string value
    Raises:
        ValueError: if the value is missing or malformed
    """
    value = _get_optional_string(request, key)
    if value is None:
        raise ValueError(f"MiMo request field {key!r} is required.")
    return value


def _transcribe_with_mlx(request: Mapping[str, object]) -> dict[str, object]:
    """Transcribe one audio file using the MLX MiMo runtime.

    Arguments:
        request: MiMo runtime request payload
    Returns:
        MiMo runtime response payload
    Raises:
        ValueError: if required request fields are missing
        ImportError: if MLX-Audio imports are unavailable
    """
    audio_path = Path(_get_required_string(request, "audio_path"))
    model_name = _get_required_string(request, "model_name")
    language = _get_optional_string(request, "language")
    max_tokens = _get_optional_positive_int(request, "max_tokens")

    start_time = time.monotonic()
    model = _get_mlx_model(model_name)
    generate_kwargs: dict[str, object] = {"language": _get_mlx_language(language)}
    if max_tokens is not None:
        generate_kwargs["max_tokens"] = max_tokens
    result = model.generate(str(audio_path), **generate_kwargs)
    with wave.open(str(audio_path), "rb") as file:
        duration_seconds = file.getnframes() / file.getframerate()
    elapsed_seconds = _get_optional_number(result, "total_time")
    if elapsed_seconds is None:
        elapsed_seconds = time.monotonic() - start_time
    result_language = _get_output_string(result, "language")

    return {
        "text": _get_output_string(result, "text") or "",
        "segments": _get_output_segments(result),
        "backend": "mimo",
        "runtime": MimoRuntime.MLX,
        "model_name": model_name,
        "language": result_language or _get_mlx_language(language) or "",
        "duration_seconds": duration_seconds,
        "elapsed_seconds": elapsed_seconds,
        "prompt_tokens": _get_optional_int(result, "prompt_tokens"),
        "generation_tokens": _get_optional_int(result, "generation_tokens"),
        "total_tokens": _get_optional_int(result, "total_tokens"),
    }


if __name__ == "__main__":
    raise SystemExit(main())
