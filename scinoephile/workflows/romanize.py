#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for romanizing subtitles."""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.lang.cmn.romanization import get_cmn_text_romanized
from scinoephile.lang.yue.romanization import get_yue_text_romanized

from .helpers import resolve_language

__all__ = ["romanize_series"]


def romanize_series(
    series: Series,
    *,
    language: Language | None = None,
    append: bool = True,
) -> Series:
    """Romanize a subtitle series using the appropriate language-specific system.

    Arguments:
        series: subtitle series to romanize
        language: explicit language, or None to detect it
        append: whether to append romanization to the original text
    Returns:
        romanized subtitle series
    Raises:
        ScinoephileError: if a language cannot be resolved or is unsupported
    """
    resolved_language = resolve_language(series, language)
    romanize_text: Callable[[str], str]
    if resolved_language.is_cantonese:
        romanize_text = get_yue_text_romanized
    elif resolved_language.is_chinese:
        romanize_text = get_cmn_text_romanized
    else:
        raise ScinoephileError(
            f"Romanization does not support language {resolved_language.code}"
        )

    romanized_series = deepcopy(series)
    for event in romanized_series:
        romanized_text = romanize_text(event.text)
        if append:
            if romanized_text:
                event.text = f"{event.text}\\N{romanized_text}"
        else:
            event.text = romanized_text
    return romanized_series
