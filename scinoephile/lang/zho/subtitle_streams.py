#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Chinese subtitle stream helpers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from logging import getLogger
from pathlib import Path

from scinoephile.core.media import SubtitleStream
from scinoephile.core.media.language import is_chinese
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series
from scinoephile.lang.zho.script_analysis.subtitles import (
    DEFAULT_ZHO_SUBTITLE_SAMPLE_SIZE,
    ZHO_SUBTITLE_OCR_LANGUAGES,
    ZhoSubtitleScriptAnalysis,
    get_zho_image_subtitle_script_analysis,
    get_zho_subtitle_script_analysis,
)
from scinoephile.media.probe import get_streams
from scinoephile.media.subtitles.cache import (
    cache_subtitles,
    get_or_create_image_subtitle_dir_path,
    get_subtitle_cache_path,
)
from scinoephile.media.subtitles.details import with_stream_details

__all__ = [
    "analyze_zho_subtitle_stream_script",
    "get_zho_subtitle_streams",
]

logger = getLogger(__name__)


def analyze_zho_subtitle_stream_script(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    cache_dir_path: Path | None = None,
    sample_size: int = DEFAULT_ZHO_SUBTITLE_SAMPLE_SIZE,
) -> ZhoSubtitleScriptAnalysis:
    """Analyze the Chinese script used by a subtitle stream.

    Arguments:
        infile_path: media input file
        stream: subtitle stream to analyze
        cache_dir_path: cache directory path
        sample_size: maximum number of image subtitles to OCR
    Returns:
        subtitle script analysis
    """
    if not is_chinese(stream.language):
        return get_zho_subtitle_script_analysis(
            "",
            failure_reason="not a Chinese subtitle stream",
        )

    analysis_cache_path = _get_subtitle_analysis_cache_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
        sample_size=sample_size,
    )
    if analysis_cache_path.exists():
        logger.info(
            f"Loaded subtitle script analysis from cache: {analysis_cache_path}"
        )
        return _load_subtitle_script_analysis(analysis_cache_path)

    stream_path = get_subtitle_cache_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )

    if stream.extension == "sup":
        image_dir_path = get_or_create_image_subtitle_dir_path(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        )
        analysis = get_zho_image_subtitle_script_analysis(
            image_dir_path,
            title=stream.title,
            sample_size=sample_size,
        )
    else:
        cache_subtitles(infile_path, [stream], cache_dir_path=cache_dir_path)
        series = Series.load(stream_path)
        text = "\n".join(event.text for event in series)
        analysis = get_zho_subtitle_script_analysis(text)

    _save_subtitle_script_analysis(analysis, analysis_cache_path)
    logger.info(f"Saved subtitle script analysis to cache: {analysis_cache_path}")
    return analysis


def get_zho_subtitle_streams(
    infile_path: Path,
    *,
    cache_dir_path: Path | None = None,
) -> list[SubtitleStream]:
    """Get subtitle stream metadata enriched with Chinese script details.

    Arguments:
        infile_path: media input file to inspect
        cache_dir_path: cache directory path
    Returns:
        enriched subtitle stream metadata
    """
    detailed_streams = []
    for stream in get_streams(infile_path):
        if not isinstance(stream, SubtitleStream):
            continue
        language = stream.language
        if is_chinese(language):
            analysis = analyze_zho_subtitle_stream_script(
                infile_path,
                stream,
                cache_dir_path=cache_dir_path,
            )
            language = language.split("-", 1)[0]
            if analysis.script is not None:
                language = analysis.script
            else:
                language = f"{language}-Unknown"
            detailed_streams.append(
                replace(
                    stream,
                    language=language,
                )
            )
        else:
            detailed_streams.append(stream)
    return [
        stream
        for stream in with_stream_details(
            infile_path,
            detailed_streams,
            cache_dir_path=cache_dir_path,
        )
        if isinstance(stream, SubtitleStream)
    ]


def _get_subtitle_analysis_cache_path(
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
    resolved_path = infile_path.resolve()
    stat = resolved_path.stat()
    payload = {
        "path": str(resolved_path),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "stream_index": stream.index,
        "codec_name": stream.codec_name,
        "sample_size": sample_size,
        "ocr_languages": ZHO_SUBTITLE_OCR_LANGUAGES,
    }
    encoded_payload = json.dumps(payload, sort_keys=True).encode("utf-8")
    cache_key = hashlib.sha256(encoded_payload).hexdigest()
    return cache_dir_path / f"{cache_key}.json"


def _load_subtitle_script_analysis(cache_path: Path) -> ZhoSubtitleScriptAnalysis:
    """Load subtitle script analysis from cache.

    Arguments:
        cache_path: analysis cache path
    Returns:
        subtitle script analysis
    """
    with cache_path.open("r", encoding="utf-8") as file:
        raw = json.load(file)
    return ZhoSubtitleScriptAnalysis(
        script=raw["script"],
        simplified_count=int(raw["simplified_count"]),
        traditional_count=int(raw["traditional_count"]),
        shared_count=int(raw["shared_count"]),
        sample_indexes=tuple(raw["sample_indexes"]),
        ocr_languages=tuple(raw["ocr_languages"]),
        failure_reason=raw["failure_reason"],
    )


def _save_subtitle_script_analysis(
    analysis: ZhoSubtitleScriptAnalysis,
    cache_path: Path,
):
    """Save subtitle script analysis to cache.

    Arguments:
        analysis: subtitle script analysis
        cache_path: analysis cache path
    """
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("w", encoding="utf-8") as file:
        json.dump(asdict(analysis), file, ensure_ascii=False, sort_keys=True)
