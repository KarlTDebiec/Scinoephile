#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Analysis code for comparing subtitle series.

This module may import from: common, core

Hierarchy within module (lower may import from higher)::
* character_error_rate
* line_diff_kind / replace_cursor
* line_diff
* series_diff
"""

from __future__ import annotations

from typing import Unpack

from scinoephile.core.subtitles import Series

from .character_error_rate_result import CharacterErrorRateResult
from .line_diff import LineDiff
from .series_diff import SeriesDiff, SeriesDiffKwargs

__all__ = [
    "CharacterErrorRateResult",
    "LineDiff",
    "format_colored_line_diff",
    "format_colored_series_diff",
    "get_series_cer",
    "get_series_diff",
    "get_text_cer",
]


def get_series_diff(
    one: Series,
    two: Series,
    **kwargs: Unpack[SeriesDiffKwargs],
) -> SeriesDiff:
    """Compare two subtitle series by line content.

    Arguments:
        one: first subtitle series
        two: second subtitle series
        **kwargs: additional keyword arguments for SeriesDiff
    Returns:
        series diff
    """
    return SeriesDiff(one, two, **kwargs)


def format_colored_line_diff(message: LineDiff, *, use_color: bool = True) -> str:
    """Format a line-level diff as a colored, character-aligned diff.

    Arguments:
        message: line-level diff message
        use_color: whether to output ANSI color escapes
    Returns:
        formatted, multi-line diff chunk
    """
    from .colored_diff import (  # noqa: PLC0415
        format_colored_line_diff as _format_colored_line_diff,
    )

    return _format_colored_line_diff(message, use_color=use_color)


def format_colored_series_diff(diff: SeriesDiff, *, use_color: bool = True) -> str:
    """Format a series diff as a colored, character-aligned diff.

    Arguments:
        diff: series diff
        use_color: whether to output ANSI color escapes
    Returns:
        formatted multi-line diff string
    """
    from .colored_diff import (  # noqa: PLC0415
        format_colored_series_diff as _format_colored_series_diff,
    )

    return _format_colored_series_diff(diff, use_color=use_color)


def get_series_cer(reference: Series, candidate: Series) -> CharacterErrorRateResult:
    """Compute character error rate between subtitle series.

    Arguments:
        reference: reference subtitle series
        candidate: candidate subtitle series
    Returns:
        character error rate results
    """
    from .character_error_rate import get_series_cer as _get_series_cer  # noqa: PLC0415

    return _get_series_cer(reference, candidate)


def get_text_cer(reference: str, candidate: str) -> CharacterErrorRateResult:
    """Compute character error rate between text strings.

    Arguments:
        reference: reference text
        candidate: candidate text
    Returns:
        character error rate results
    """
    from .character_error_rate import get_text_cer as _get_text_cer  # noqa: PLC0415

    return _get_text_cer(reference, candidate)
