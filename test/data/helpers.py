#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared helpers for processing test-data subtitle series."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scinoephile.core import Language
from scinoephile.core.subtitles import Series
from scinoephile.core.timing import get_series_timewarped
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_converted
from scinoephile.workflows.clean import clean_series
from scinoephile.workflows.flatten import flatten_series
from scinoephile.workflows.review import review_series
from scinoephile.workflows.romanize import romanize_series

__all__ = [
    "load_or_clean_series",
    "load_or_flatten_series",
    "load_or_review_series",
    "load_or_romanize_series",
    "load_or_simplify_series",
    "load_or_timewarp_series",
]


def load_or_clean_series(
    series: Series,
    output_path: Path,
    language: Language,
    overwrite: bool = False,
    *,
    informational_detected_language: Language | None = None,
) -> Series:
    """Load or create a cleaned subtitle series.

    Arguments:
        series: series to clean
        output_path: cleaned subtitle output path
        language: subtitle language
        overwrite: whether to overwrite an existing output
        informational_detected_language: detected mismatch language to log at info
            rather than warning, or None to warn for every mismatch
    Returns:
        cleaned series
    """
    if output_path.exists() and not overwrite:
        return Series.load(output_path)

    cleaned = clean_series(
        series,
        language=language,
        informational_detected_language=informational_detected_language,
    )
    cleaned.save(output_path)
    return cleaned


def load_or_flatten_series(
    series: Series,
    output_path: Path,
    language: Language,
    overwrite: bool = False,
) -> Series:
    """Load or create a flattened subtitle series.

    Arguments:
        series: series to flatten
        output_path: flattened subtitle output path
        language: subtitle language
        overwrite: whether to overwrite an existing output
    Returns:
        flattened series
    """
    if output_path.exists() and not overwrite:
        return Series.load(output_path)

    flattened = flatten_series(series, language=language)
    flattened.save(output_path)
    return flattened


def load_or_review_series(
    series: Series,
    output_path: Path,
    language: Language,
    overwrite: bool = False,
    reviewer_kw: dict[str, Any] | None = None,
) -> Series:
    """Load or create a reviewed subtitle series.

    Arguments:
        series: series to review
        output_path: reviewed subtitle output path
        language: subtitle language
        overwrite: whether to overwrite an existing output
        reviewer_kw: keyword arguments for reviewer construction
    Returns:
        reviewed series
    """
    if output_path.exists() and not overwrite:
        return Series.load(output_path)

    reviewer_kw = dict(reviewer_kw or {})
    reviewer_kw.setdefault(
        "test_case_path",
        output_path.parent / "lang" / language.language / "review.json",
    )
    reviewer_kw.setdefault("auto_verify", True)

    reviewed = review_series(series, language=language, **reviewer_kw)
    reviewed.save(output_path)
    return reviewed


def load_or_romanize_series(
    series: Series,
    output_path: Path,
    language: Language,
    overwrite: bool = False,
) -> Series:
    """Load or create a romanized subtitle series.

    Arguments:
        series: series to romanize
        output_path: romanized subtitle output path
        language: subtitle language
        overwrite: whether to overwrite an existing output
    Returns:
        romanized series
    """
    if output_path.exists() and not overwrite:
        return Series.load(output_path)

    romanized = romanize_series(series, language=language, append=True)
    romanized.save(output_path)
    return romanized


def load_or_simplify_series(
    series: Series,
    output_path: Path,
    overwrite: bool = False,
) -> Series:
    """Load or create a simplified Chinese-script subtitle series.

    Arguments:
        series: series to simplify
        output_path: simplified subtitle output path
        overwrite: whether to overwrite an existing output
    Returns:
        simplified series
    """
    if output_path.exists() and not overwrite:
        return Series.load(output_path)

    simplified = get_zho_converted(series, OpenCCConfig.t2s)
    simplified.save(output_path)
    return simplified


def load_or_timewarp_series(
    series: Series,
    reference: Series,
    output_path: Path,
    *,
    one_start_idx: int | None = None,
    one_end_idx: int | None = None,
    two_start_idx: int | None = None,
    two_end_idx: int | None = None,
    overwrite: bool = False,
) -> Series:
    """Load or create a timewarped subtitle series.

    Arguments:
        series: source series to timewarp
        reference: anchor series whose timing should be followed
        output_path: timewarped subtitle output path
        one_start_idx: 1-based start index in the anchor series
        one_end_idx: 1-based end index in the anchor series
        two_start_idx: 1-based start index in the source series
        two_end_idx: 1-based end index in the source series
        overwrite: whether to overwrite an existing output
    Returns:
        timewarped series
    """
    if output_path.exists() and not overwrite:
        return Series.load(output_path)

    timewarped = get_series_timewarped(
        reference,
        series,
        one_start_idx=one_start_idx,
        one_end_idx=one_end_idx,
        two_start_idx=two_start_idx,
        two_end_idx=two_end_idx,
    )
    timewarped.save(output_path)
    return timewarped
