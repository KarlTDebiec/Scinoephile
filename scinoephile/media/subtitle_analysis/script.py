#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle stream script analysis."""

from __future__ import annotations

import json
from dataclasses import asdict
from logging import getLogger
from pathlib import Path

from scinoephile.core.media import SubtitleStream
from scinoephile.core.subtitles import Series
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.zho.language import is_zho_language
from scinoephile.lang.zho.script_analysis import (
    ZhoScriptAnalysis,
    get_zho_script_analysis,
)

from .artifacts import (
    cache_subtitle_stream_artifacts,
    get_cached_subtitle_artifact_path,
)
from .cache_keys import get_subtitle_analysis_cache_path
from .image_cache import (
    get_or_create_image_subtitle_dir_path,
    load_cached_image_subtitles,
    load_image_subtitle_manifest,
)
from .types import SubtitleScriptAnalysis

__all__ = ["analyze_subtitle_stream_script"]

logger = getLogger(__name__)

DEFAULT_SAMPLE_SIZE = 4
"""Default number of image subtitle samples to OCR."""
CONFLICT_SAMPLE_SIZE = 16
"""Number of image subtitle samples to OCR when more evidence is needed."""


def analyze_subtitle_stream_script(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    cache_dir_path: Path | None = None,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
) -> SubtitleScriptAnalysis:
    """Analyze the Chinese script used by a subtitle stream.

    Arguments:
        infile_path: media input file
        stream: subtitle stream to analyze
        cache_dir_path: cache directory path
        sample_size: maximum number of image subtitles to OCR
    Returns:
        subtitle script analysis
    """
    if not is_zho_language(stream.language):
        return _from_zho_analysis(
            get_zho_script_analysis(""),
            failure_reason="not a Chinese subtitle stream",
        )

    analysis_cache_path = get_subtitle_analysis_cache_path(
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

    artifact_path = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    if not artifact_path.exists():
        cache_subtitle_stream_artifacts(
            infile_path,
            [stream],
            cache_dir_path=cache_dir_path,
        )

    if stream.extension == "sup":
        analysis = _analyze_image_subtitle_artifact(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
            sample_size=sample_size,
        )
    else:
        analysis = _analyze_text_subtitle_artifact(artifact_path)

    _save_subtitle_script_analysis(analysis, analysis_cache_path)
    logger.info(f"Saved subtitle script analysis to cache: {analysis_cache_path}")
    return analysis


def _analyze_cached_image_subtitle_samples(
    image_dir_path: Path,
    sample_indexes: list[int],
) -> SubtitleScriptAnalysis:
    """Analyze selected cached image subtitles using PaddleOCR.

    Arguments:
        image_dir_path: rendered image subtitle cache directory path
        sample_indexes: zero-based indexes of subtitles to OCR
    Returns:
        subtitle script analysis
    """
    sampled_events = load_cached_image_subtitles(image_dir_path, sample_indexes)
    analyses = []
    for language in ("ch", "chinese_cht"):
        from scinoephile.image.ocr.paddle import (  # noqa: PLC0415
            ocr_image_series_with_paddle,
        )

        sampled_series = ImageSeries(events=sampled_events)
        text_series = ocr_image_series_with_paddle(
            sampled_series,
            language=language,
        )
        text = "\n".join(event.text for event in text_series)
        analyses.append(get_zho_script_analysis(text))

    first_analysis = analyses[0]
    second_analysis = analyses[1]
    script = first_analysis.script
    failure_reason = None
    if script is None or second_analysis.script != script:
        script = None
        failure_reason = "OCR script analyses did not agree"

    return SubtitleScriptAnalysis(
        script=script,
        simplified_count=first_analysis.simplified_count,
        traditional_count=first_analysis.traditional_count,
        shared_count=first_analysis.shared_count,
        sample_indexes=tuple(sample_indexes),
        ocr_languages=("ch", "chinese_cht"),
        failure_reason=failure_reason,
    )


def _analyze_image_subtitle_artifact(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    cache_dir_path: Path | None,
    sample_size: int,
) -> SubtitleScriptAnalysis:
    """Analyze an image subtitle artifact using PaddleOCR.

    Arguments:
        infile_path: media input file
        stream: subtitle stream to analyze
        cache_dir_path: cache directory path
        sample_size: maximum number of image subtitles to OCR
    Returns:
        subtitle script analysis
    """
    image_dir_path = get_or_create_image_subtitle_dir_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    manifest = load_image_subtitle_manifest(image_dir_path)
    sample_indexes = _get_evenly_spaced_indexes(
        int(manifest["event_count"]),
        sample_size,
    )
    if not sample_indexes:
        return SubtitleScriptAnalysis(
            script=None,
            simplified_count=0,
            traditional_count=0,
            shared_count=0,
            failure_reason="no subtitle images to sample",
        )

    analysis = _analyze_cached_image_subtitle_samples(
        image_dir_path,
        sample_indexes,
    )
    expected_script = _get_expected_script_from_title(stream.title)
    should_expand_samples = False
    if int(manifest["event_count"]) > len(sample_indexes):
        if analysis.script is None:
            should_expand_samples = True
        elif expected_script is not None and analysis.script != expected_script:
            should_expand_samples = True

    if should_expand_samples:
        expanded_sample_indexes = _get_evenly_spaced_indexes(
            int(manifest["event_count"]),
            CONFLICT_SAMPLE_SIZE,
        )
        analysis = _analyze_cached_image_subtitle_samples(
            image_dir_path,
            expanded_sample_indexes,
        )
    return analysis


def _analyze_text_subtitle_artifact(artifact_path: Path) -> SubtitleScriptAnalysis:
    """Analyze a text subtitle artifact.

    Arguments:
        artifact_path: cached text subtitle artifact path
    Returns:
        subtitle script analysis
    """
    series = Series.load(artifact_path)
    text = "\n".join(event.text for event in series)
    analysis = get_zho_script_analysis(text)
    failure_reason = None
    if analysis.script is None:
        failure_reason = "Chinese script could not be determined"
    return _from_zho_analysis(analysis, failure_reason=failure_reason)


def _from_zho_analysis(
    analysis: ZhoScriptAnalysis,
    *,
    failure_reason: str | None = None,
) -> SubtitleScriptAnalysis:
    """Convert Chinese text analysis to subtitle stream analysis.

    Arguments:
        analysis: Chinese text analysis
        failure_reason: failure reason, if any
    Returns:
        subtitle script analysis
    """
    return SubtitleScriptAnalysis(
        script=analysis.script,
        simplified_count=analysis.simplified_count,
        traditional_count=analysis.traditional_count,
        shared_count=analysis.shared_count,
        failure_reason=failure_reason,
    )


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


def _get_expected_script_from_title(title: str | None) -> str | None:
    """Get expected Chinese script from a stream title.

    Arguments:
        title: stream title
    Returns:
        expected script, if a title contains an explicit script hint
    """
    if title is None:
        return None
    normalized_title = title.casefold()
    if "simplified" in normalized_title or "hans" in normalized_title:
        return "zho-Hans"
    if "traditional" in normalized_title or "hant" in normalized_title:
        return "zho-Hant"
    return None


def _load_subtitle_script_analysis(cache_path: Path) -> SubtitleScriptAnalysis:
    """Load subtitle script analysis from cache.

    Arguments:
        cache_path: analysis cache path
    Returns:
        subtitle script analysis
    """
    with cache_path.open("r", encoding="utf-8") as file:
        raw = json.load(file)
    return SubtitleScriptAnalysis(
        script=raw["script"],
        simplified_count=int(raw["simplified_count"]),
        traditional_count=int(raw["traditional_count"]),
        shared_count=int(raw["shared_count"]),
        sample_indexes=tuple(raw["sample_indexes"]),
        ocr_languages=tuple(raw["ocr_languages"]),
        failure_reason=raw["failure_reason"],
    )


def _save_subtitle_script_analysis(
    analysis: SubtitleScriptAnalysis,
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
