#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for cleaning subtitles."""

from __future__ import annotations

from copy import deepcopy

from scinoephile.core import Language
from scinoephile.core.subtitles import Series
from scinoephile.lang.eng.cleaning import get_eng_text_cleaned
from scinoephile.lang.zho.cleaning import get_zho_text_cleaned

from .helpers import resolve_language

__all__ = ["clean_series"]


def clean_series(
    series: Series,
    *,
    language: Language | None = None,
    remove_empty: bool = True,
) -> Series:
    """Clean a subtitle series.

    Arguments:
        series: subtitle series to clean
        language: explicit language, or None to detect it
        remove_empty: whether to remove subtitles with empty text
    Returns:
        cleaned subtitle series
    Raises:
        ScinoephileError: if a language cannot be resolved
    """
    resolved_language = resolve_language(series, language)
    if resolved_language is Language.eng:
        clean_text = get_eng_text_cleaned
    else:
        clean_text = get_zho_text_cleaned

    cleaned = deepcopy(series)
    cleaned_events = []
    for event in cleaned:
        text = clean_text((event.text or "").strip())
        if text or not remove_empty:
            event.text = text if text is not None else ""
            cleaned_events.append(event)
    cleaned.events = cleaned_events
    return cleaned
