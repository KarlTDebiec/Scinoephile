#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle analysis cache keys."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scinoephile.core.media import SubtitleStream
from scinoephile.core.paths import get_runtime_cache_dir_path

__all__ = [
    "SCRIPT_ANALYSIS_CACHE_VERSION",
    "get_subtitle_analysis_cache_path",
]

SCRIPT_ANALYSIS_CACHE_VERSION = 4
"""Subtitle script analysis cache schema version."""


def get_subtitle_analysis_cache_path(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    cache_dir_path: Path | None,
    sample_size: int,
) -> Path:
    """Get path to cached script analysis JSON.

    Arguments:
        infile_path: media input file
        stream: subtitle stream
        cache_dir_path: cache directory path
        sample_size: OCR sample size
    Returns:
        analysis cache path
    """
    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("media", "subtitle-analysis")
    cache_key = _get_subtitle_analysis_cache_key(
        infile_path,
        stream,
        sample_size=sample_size,
        ocr_languages=("ch", "chinese_cht"),
    )
    return cache_dir_path / f"{cache_key}.json"


def _get_subtitle_analysis_cache_key(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    sample_size: int,
    ocr_languages: tuple[str, ...],
) -> str:
    """Get a stable cache key for subtitle script analysis.

    Arguments:
        infile_path: media input file
        stream: subtitle stream
        sample_size: OCR sample size
        ocr_languages: OCR languages
    Returns:
        hexadecimal cache key
    """
    resolved_path = infile_path.resolve()
    stat = resolved_path.stat()
    payload = {
        "path": str(resolved_path),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "stream_index": stream.index,
        "codec_name": stream.codec_name,
        "sample_size": sample_size,
        "ocr_languages": ocr_languages,
        "script_analysis_cache_version": SCRIPT_ANALYSIS_CACHE_VERSION,
    }
    encoded_payload = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded_payload).hexdigest()
