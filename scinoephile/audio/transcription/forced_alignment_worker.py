#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subprocess worker for optional forced-alignment backends."""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping, Sequence
from typing import Any, cast

__all__ = [
    "align_with_whisperx",
    "main",
]

_WHISPERX_EXTRA_MESSAGE = (
    "WhisperX alignment worker requires whisperx and its alignment dependencies."
)


def align_with_whisperx(request: Mapping[str, object]) -> dict[str, object]:
    """Run WhisperX alignment for one transcript.

    Arguments:
        request: worker request payload
    Returns:
        WhisperX alignment payload
    Raises:
        ImportError: if WhisperX is unavailable
        ValueError: if request fields are missing or malformed
    """
    audio_path = _get_required_string(request, "audio_path")
    transcript_text = _get_required_string(request, "text").strip()
    duration_seconds = _get_required_number(request, "duration_seconds")
    language = _get_optional_string(request, "language") or "zh"
    model_name = _get_optional_string(request, "model_name")
    device = _get_optional_string(request, "device") or "cpu"
    if not transcript_text:
        raise ValueError("Cannot align empty transcript.")

    whisperx = _get_whisperx_module()
    load_align_model_kwargs: dict[str, object] = {
        "language_code": language,
        "device": device,
    }
    if model_name is not None:
        load_align_model_kwargs["model_name"] = model_name
    align_model, align_metadata = whisperx.load_align_model(**load_align_model_kwargs)
    transcript = [
        {"start": 0.0, "end": float(duration_seconds), "text": transcript_text}
    ]
    result = whisperx.align(
        transcript=transcript,
        model=align_model,
        align_model_metadata=align_metadata,
        audio=audio_path,
        device=device,
        return_char_alignments=False,
    )
    compatible_result = _to_json_compatible(result)
    if not isinstance(compatible_result, dict):
        raise ValueError("WhisperX alignment did not return a JSON object.")
    return cast(dict[str, object], compatible_result)


def main() -> int:
    """Run the forced-alignment worker from JSON stdin to JSON stdout.

    Returns:
        process exit code
    """
    try:
        request = json.loads(sys.stdin.read())
        if not isinstance(request, Mapping):
            raise ValueError("Worker request must be a JSON object.")
        backend = _get_optional_string(request, "backend") or "whisperx"
        if backend != "whisperx":
            raise ValueError(f"Unsupported alignment worker backend: {backend}")
        payload = align_with_whisperx(cast(Mapping[str, object], request))
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(payload, ensure_ascii=False))
    return 0


def _get_optional_number(request: Mapping[str, object], key: str) -> float | None:
    """Get an optional numeric field from a worker request.

    Arguments:
        request: worker request payload
        key: field key
    Returns:
        numeric value, if present
    Raises:
        ValueError: if the value is malformed
    """
    value = request.get(key)
    if value is None:
        return None
    if isinstance(value, int | float):
        return float(value)
    raise ValueError(f"Worker request field {key!r} must be numeric.")


def _get_optional_string(request: Mapping[str, object], key: str) -> str | None:
    """Get an optional string field from a worker request.

    Arguments:
        request: worker request payload
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
        raise ValueError(f"Worker request field {key!r} must be a string.")
    return value


def _get_required_number(request: Mapping[str, object], key: str) -> float:
    """Get a required numeric field from a worker request.

    Arguments:
        request: worker request payload
        key: field key
    Returns:
        numeric value
    Raises:
        ValueError: if the value is missing or malformed
    """
    value = _get_optional_number(request, key)
    if value is None:
        raise ValueError(f"Worker request field {key!r} is required.")
    return value


def _get_required_string(request: Mapping[str, object], key: str) -> str:
    """Get a required string field from a worker request.

    Arguments:
        request: worker request payload
        key: field key
    Returns:
        string value
    Raises:
        ValueError: if the value is missing or malformed
    """
    value = _get_optional_string(request, key)
    if value is None:
        raise ValueError(f"Worker request field {key!r} is required.")
    return value


def _get_whisperx_module() -> Any:
    """Import WhisperX on demand.

    Returns:
        imported WhisperX module
    Raises:
        ImportError: if WhisperX is unavailable
    """
    try:
        import whisperx  # ty: ignore[unresolved-import]  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(_WHISPERX_EXTRA_MESSAGE) from exc
    return whisperx


def _to_json_compatible(value: object) -> object:
    """Convert common model payload objects to JSON-compatible values.

    Arguments:
        value: value to convert
    Returns:
        JSON-compatible value
    """
    if isinstance(value, Mapping):
        return {str(key): _to_json_compatible(item) for key, item in value.items()}
    if isinstance(value, str | int | float | bool) or value is None:
        return value
    if isinstance(value, Sequence):
        return [_to_json_compatible(item) for item in value]
    item = getattr(value, "item", None)
    if callable(item):
        return _to_json_compatible(item())
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
