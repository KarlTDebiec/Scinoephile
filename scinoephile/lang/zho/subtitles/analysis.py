#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Chinese subtitle script analysis."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from logging import getLogger
from pathlib import Path

from scinoephile.core import Language
from scinoephile.core.language import is_chinese_language_tag
from scinoephile.core.media import SubtitleStream
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.zho.script.analysis import get_zho_script_analysis
from scinoephile.media.subtitles.cache import cache_subtitles, get_subtitle_cache_path

__all__ = [
    "ZhoSubtitleScriptAnalysis",
    "analyze_zho_subtitle_stream_script",
]

_DEFAULT_ZHO_SUBTITLE_SAMPLE_SIZE = 4
"""Default number of image subtitle samples to OCR."""
_ZHO_SUBTITLE_OCR_LANGUAGES = (Language.zho_hans, Language.zho_hant)
"""Languages to compare for Chinese subtitle script analysis."""

logger = getLogger(__name__)


@dataclass(frozen=True)
class ZhoSubtitleScriptAnalysis:
    """Chinese subtitle stream script analysis result."""

    script: str | None = None
    """Detected script tag, when determined."""
    simplified_count: int = 0
    """Number of simplified-only Hanzi observed."""
    traditional_count: int = 0
    """Number of traditional-only Hanzi observed."""
    shared_count: int = 0
    """Number of non-decisive Hanzi observed."""
    sample_indexes: tuple[int, ...] = ()
    """Indexes sampled for OCR, if applicable."""
    ocr_languages: tuple[str, ...] = ()
    """OCR languages used, if applicable."""
    failure_reason: str | None = None
    """Reason script could not be determined."""


def analyze_zho_subtitle_stream_script(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    cache_dir_path: Path | None = None,
    sample_size: int = _DEFAULT_ZHO_SUBTITLE_SAMPLE_SIZE,
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
    if not is_chinese_language_tag(stream.language):
        return ZhoSubtitleScriptAnalysis(
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

    cache_subtitles(infile_path, [stream], cache_dir_path=cache_dir_path)
    stream_path = get_subtitle_cache_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )

    if stream.extension == "sup":
        image_dir_path = stream_path.parent / "image-series"
        analysis = _get_zho_image_subtitle_script_analysis(
            image_dir_path,
            sample_size=sample_size,
        )
    else:
        series = Series.load(stream_path)
        text = "\n".join(event.text for event in series)
        analysis = _get_zho_subtitle_script_analysis(text)

    _save_subtitle_script_analysis(analysis, analysis_cache_path)
    logger.info(f"Saved subtitle script analysis to cache: {analysis_cache_path}")
    return analysis


def _get_evenly_spaced_indexes(length: int, sample_size: int) -> list[int]:
    """Get evenly spaced indexes for sampling a subtitle series.

    Arguments:
        length: number of available subtitles
        sample_size: maximum number of subtitles to sample
    Returns:
        sampled indexes
    """
    if length <= 0 or sample_size <= 0:
        return []
    if length <= sample_size:
        return list(range(length))
    if sample_size == 1:
        return [length // 2]
    return [
        round(index * (length - 1) / (sample_size - 1)) for index in range(sample_size)
    ]


def _get_image_subtitle_sample_analysis(
    series: ImageSeries,
    sample_indexes: list[int],
) -> ZhoSubtitleScriptAnalysis:
    """Analyze selected cached image subtitles using PaddleOCR.

    Arguments:
        series: rendered image subtitle series
        sample_indexes: zero-based indexes of subtitles to OCR
    Returns:
        Chinese subtitle script analysis
    """
    from scinoephile.image.ocr.paddle import (  # noqa: PLC0415
        ocr_image_series_with_paddle,
    )

    sampled_series = ImageSeries(
        events=[series.events[index] for index in sample_indexes]
    )
    script_analyses = []
    for language in _ZHO_SUBTITLE_OCR_LANGUAGES:
        text_series = ocr_image_series_with_paddle(
            sampled_series,
            language=language,
        )
        text = "\n".join(event.text for event in text_series)
        script_analyses.append(get_zho_script_analysis(text))

    reference_analysis = script_analyses[0]
    script = reference_analysis.script
    failure_reason = None
    if script is None or any(
        analysis.script != script for analysis in script_analyses[1:]
    ):
        script = None
        failure_reason = "OCR script analyses did not agree"

    return ZhoSubtitleScriptAnalysis(
        script=script,
        simplified_count=reference_analysis.simplified_count,
        traditional_count=reference_analysis.traditional_count,
        shared_count=reference_analysis.shared_count,
        sample_indexes=tuple(sample_indexes),
        ocr_languages=tuple(language.code for language in _ZHO_SUBTITLE_OCR_LANGUAGES),
        failure_reason=failure_reason,
    )


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
        "ocr_languages": tuple(
            language.code for language in _ZHO_SUBTITLE_OCR_LANGUAGES
        ),
    }
    encoded_payload = json.dumps(payload, sort_keys=True).encode("utf-8")
    cache_key = hashlib.sha256(encoded_payload).hexdigest()
    return cache_dir_path / f"{cache_key}.json"


def _get_zho_image_subtitle_script_analysis(
    image_dir_path: Path,
    *,
    sample_size: int = _DEFAULT_ZHO_SUBTITLE_SAMPLE_SIZE,
) -> ZhoSubtitleScriptAnalysis:
    """Analyze Chinese script in rendered image subtitles using PaddleOCR.

    Arguments:
        image_dir_path: rendered image subtitle cache directory path
        sample_size: maximum number of image subtitles to OCR
    Returns:
        Chinese subtitle script analysis
    """
    series = ImageSeries.load(image_dir_path)
    event_count = len(series)
    sample_indexes = _get_evenly_spaced_indexes(event_count, sample_size)
    if not sample_indexes:
        return ZhoSubtitleScriptAnalysis(
            failure_reason="no subtitle images to sample",
        )

    return _get_image_subtitle_sample_analysis(
        series,
        sample_indexes,
    )


def _get_zho_subtitle_script_analysis(
    text: str,
    *,
    failure_reason: str | None = None,
) -> ZhoSubtitleScriptAnalysis:
    """Analyze Chinese script in subtitle text.

    Arguments:
        text: subtitle text
        failure_reason: failure reason, if known before analysis
    Returns:
        Chinese subtitle script analysis
    """
    analysis = get_zho_script_analysis(text)
    if failure_reason is None and analysis.script is None:
        failure_reason = "Chinese script could not be determined"
    return ZhoSubtitleScriptAnalysis(
        script=analysis.script,
        simplified_count=analysis.simplified_count,
        traditional_count=analysis.traditional_count,
        shared_count=analysis.shared_count,
        failure_reason=failure_reason,
    )


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
