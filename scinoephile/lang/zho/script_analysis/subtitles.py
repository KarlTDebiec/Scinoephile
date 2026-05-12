#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Chinese subtitle script analysis."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scinoephile.image.subtitles import ImageSeries
from scinoephile.media.subtitles.cache import (
    load_cached_image_subtitles,
    load_image_subtitle_manifest,
)

from .analysis import get_zho_script_analysis
from .result import ZhoScriptAnalysis

__all__ = [
    "CONFLICT_ZHO_SUBTITLE_SAMPLE_SIZE",
    "DEFAULT_ZHO_SUBTITLE_SAMPLE_SIZE",
    "ZHO_SUBTITLE_OCR_LANGUAGES",
    "ZhoSubtitleScriptAnalysis",
    "get_zho_image_subtitle_script_analysis",
    "get_zho_subtitle_script_analysis",
]

DEFAULT_ZHO_SUBTITLE_SAMPLE_SIZE = 4
"""Default number of image subtitle samples to OCR."""
CONFLICT_ZHO_SUBTITLE_SAMPLE_SIZE = 16
"""Number of image subtitle samples to OCR when more evidence is needed."""
ZHO_SUBTITLE_OCR_LANGUAGES = ("ch", "chinese_cht")
"""PaddleOCR languages to compare for Chinese subtitle script analysis."""


@dataclass(frozen=True)
class ZhoSubtitleScriptAnalysis:
    """Chinese subtitle stream script analysis result."""

    script: str | None
    """Detected script tag, when determined."""
    simplified_count: int
    """Number of simplified-only Hanzi observed."""
    traditional_count: int
    """Number of traditional-only Hanzi observed."""
    shared_count: int
    """Number of non-decisive Hanzi observed."""
    sample_indexes: tuple[int, ...] = ()
    """Indexes sampled for OCR, if applicable."""
    ocr_languages: tuple[str, ...] = ()
    """OCR languages used, if applicable."""
    failure_reason: str | None = None
    """Reason script could not be determined."""


def get_zho_image_subtitle_script_analysis(
    image_dir_path: Path,
    *,
    title: str | None = None,
    sample_size: int = DEFAULT_ZHO_SUBTITLE_SAMPLE_SIZE,
) -> ZhoSubtitleScriptAnalysis:
    """Analyze Chinese script in rendered image subtitles using PaddleOCR.

    Arguments:
        image_dir_path: rendered image subtitle cache directory path
        title: stream title, if available
        sample_size: maximum number of image subtitles to OCR
    Returns:
        Chinese subtitle script analysis
    """
    manifest = load_image_subtitle_manifest(image_dir_path)
    event_count = int(manifest["event_count"])
    sample_indexes = _get_evenly_spaced_indexes(event_count, sample_size)
    if not sample_indexes:
        return ZhoSubtitleScriptAnalysis(
            script=None,
            simplified_count=0,
            traditional_count=0,
            shared_count=0,
            failure_reason="no subtitle images to sample",
        )

    analysis = _get_cached_image_subtitle_sample_analysis(
        image_dir_path,
        sample_indexes,
    )
    expected_script = _get_expected_script_from_title(title)
    should_expand_samples = False
    if event_count > len(sample_indexes):
        if analysis.script is None:
            should_expand_samples = True
        elif expected_script is not None and analysis.script != expected_script:
            should_expand_samples = True

    if should_expand_samples:
        expanded_sample_indexes = _get_evenly_spaced_indexes(
            event_count,
            CONFLICT_ZHO_SUBTITLE_SAMPLE_SIZE,
        )
        analysis = _get_cached_image_subtitle_sample_analysis(
            image_dir_path,
            expanded_sample_indexes,
        )
    return analysis


def get_zho_subtitle_script_analysis(
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
    return _from_zho_analysis(analysis, failure_reason=failure_reason)


def _from_zho_analysis(
    analysis: ZhoScriptAnalysis,
    *,
    failure_reason: str | None = None,
) -> ZhoSubtitleScriptAnalysis:
    """Convert Chinese text analysis to subtitle stream analysis.

    Arguments:
        analysis: Chinese text analysis
        failure_reason: failure reason, if any
    Returns:
        Chinese subtitle script analysis
    """
    return ZhoSubtitleScriptAnalysis(
        script=analysis.script,
        simplified_count=analysis.simplified_count,
        traditional_count=analysis.traditional_count,
        shared_count=analysis.shared_count,
        failure_reason=failure_reason,
    )


def _get_cached_image_subtitle_sample_analysis(
    image_dir_path: Path,
    sample_indexes: list[int],
) -> ZhoSubtitleScriptAnalysis:
    """Analyze selected cached image subtitles using PaddleOCR.

    Arguments:
        image_dir_path: rendered image subtitle cache directory path
        sample_indexes: zero-based indexes of subtitles to OCR
    Returns:
        Chinese subtitle script analysis
    """
    sampled_events = load_cached_image_subtitles(image_dir_path, sample_indexes)
    analyses = []
    for language in ZHO_SUBTITLE_OCR_LANGUAGES:
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

    return ZhoSubtitleScriptAnalysis(
        script=script,
        simplified_count=first_analysis.simplified_count,
        traditional_count=first_analysis.traditional_count,
        shared_count=first_analysis.shared_count,
        sample_indexes=tuple(sample_indexes),
        ocr_languages=ZHO_SUBTITLE_OCR_LANGUAGES,
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
