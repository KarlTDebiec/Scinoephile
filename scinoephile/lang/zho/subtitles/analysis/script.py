#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Chinese subtitle script analysis."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path

from scinoephile.core import Language
from scinoephile.core.language import is_chinese_language_tag
from scinoephile.core.media import SubtitleStream
from scinoephile.core.paths import get_runtime_cache_root_path
from scinoephile.core.subtitles import Series
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.zho.script.analysis import get_zho_script_analysis
from scinoephile.media.subtitles.cache import SubtitleCache

from .cache import ZhoSubtitleScriptAnalysisCache
from .result import ZhoSubtitleScriptAnalysis

__all__ = ["analyze_zho_subtitle_stream_script"]

_DEFAULT_ZHO_SUBTITLE_SAMPLE_SIZE = 4
"""Default number of image subtitle samples to OCR."""
_ZHO_SUBTITLE_OCR_LANGUAGES = (Language.zho_hans, Language.zho_hant)
"""Languages to compare for Chinese subtitle script analysis."""

logger = getLogger(__name__)


def analyze_zho_subtitle_stream_script(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
    sample_size: int = _DEFAULT_ZHO_SUBTITLE_SAMPLE_SIZE,
    subtitle_cache: SubtitleCache | None = None,
) -> ZhoSubtitleScriptAnalysis:
    """Analyze the Chinese script used by a subtitle stream.

    Arguments:
        infile_path: media input file
        stream: subtitle stream to analyze
        cache_root_path: cache root directory path
        overwrite_cache: whether to replace matching analysis and OCR cache files
        sample_size: maximum number of image subtitles to OCR
        subtitle_cache: subtitle stream cache shared with upstream operations
    Returns:
        subtitle script analysis
    """
    if not is_chinese_language_tag(stream.language):
        return ZhoSubtitleScriptAnalysis(
            failure_reason="not a Chinese subtitle stream",
        )

    # Resolve one subtitle cache and use its policy for related cached artifacts
    if subtitle_cache is None:
        if cache_root_path is None:
            cache_root_path = get_runtime_cache_root_path()
        subtitle_cache = SubtitleCache(cache_root_path, overwrite_cache)
    else:
        cache_root_path = subtitle_cache.cache_root_path
        overwrite_cache = subtitle_cache.overwrite

    # Reuse a matching script analysis when available
    ocr_language_codes = tuple(
        language.code for language in _ZHO_SUBTITLE_OCR_LANGUAGES
    )
    analysis_cache = ZhoSubtitleScriptAnalysisCache(
        cache_root_path,
        overwrite_cache,
    )
    cached_analysis = analysis_cache.load(
        infile_path,
        stream,
        sample_size,
        ocr_language_codes,
    )
    if cached_analysis is not None:
        return cached_analysis

    # Cache the source subtitle stream before inspecting its contents
    subtitle_cache.cache(
        infile_path,
        [stream],
    )
    stream_path = subtitle_cache.get_path(infile_path, stream)

    # Analyze either rendered SUP images or text subtitle events
    if stream.extension == "sup":
        image_dir_path = stream_path.parent / "image-series"
        analysis = _get_zho_image_subtitle_script_analysis(
            image_dir_path,
            cache_root_path=cache_root_path,
            overwrite_cache=overwrite_cache,
            sample_size=sample_size,
        )
    else:
        series = Series.load(stream_path)
        text = "\n".join(event.text for event in series)
        analysis = _get_zho_subtitle_script_analysis(text)

    # Persist the analysis for reuse by later probes
    analysis_cache.save(
        infile_path,
        stream,
        sample_size,
        ocr_language_codes,
        analysis,
    )
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
    *,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
) -> ZhoSubtitleScriptAnalysis:
    """Analyze selected cached image subtitles using PaddleOCR.

    Arguments:
        series: rendered image subtitle series
        sample_indexes: zero-based indexes of subtitles to OCR
        cache_root_path: cache root directory path
        overwrite_cache: whether to replace matching PaddleOCR cache files
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
            cache_root_path=cache_root_path,
            language=language,
            overwrite_cache=overwrite_cache,
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


def _get_zho_image_subtitle_script_analysis(
    image_dir_path: Path,
    *,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
    sample_size: int = _DEFAULT_ZHO_SUBTITLE_SAMPLE_SIZE,
) -> ZhoSubtitleScriptAnalysis:
    """Analyze Chinese script in rendered image subtitles using PaddleOCR.

    Arguments:
        image_dir_path: rendered image subtitle cache directory path
        cache_root_path: cache root directory path
        overwrite_cache: whether to replace matching PaddleOCR cache files
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
        cache_root_path=cache_root_path,
        overwrite_cache=overwrite_cache,
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
