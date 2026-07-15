#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for flattening subtitles."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from copy import deepcopy
from logging import getLogger

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.lang.eng.flattening import get_eng_text_flattened
from scinoephile.lang.zho.flattening import get_zho_text_flattened

from .helpers import resolve_language

__all__ = ["flatten_series"]


logger = getLogger(__name__)


def flatten_series(
    series: Series,
    *,
    language: Language | None = None,
    exclusions: Iterable[int] | None = None,
) -> Series:
    """Flatten a multi-line subtitle series to single lines.

    Arguments:
        series: subtitle series to flatten
        language: explicit language, or None to detect it
        exclusions: 1-based subtitle indexes to exclude from flattening
    Returns:
        flattened subtitle series
    Raises:
        ScinoephileError: if a language cannot be resolved or an exclusion index is
            invalid
    """
    exclusion_set = set(exclusions or [])
    if any(idx < 1 for idx in exclusion_set):
        raise ScinoephileError("Exclusion indexes must be positive (1-based).")

    resolved_language = resolve_language(series, language)
    flatten_text: Callable[[str], str]
    if resolved_language is Language.eng:
        flatten_text = get_eng_text_flattened
    else:
        flatten_text = get_zho_text_flattened

    flattened = deepcopy(series)
    for i, event in enumerate(flattened, 1):
        if i in exclusion_set:
            logger.info(
                f"Skipping flattening of subtitle {i}, with text:\n{event.text}"
            )
            continue
        text = event.text
        if resolved_language is Language.eng:
            text = text.strip()
        event.text = flatten_text(text)
    return flattened
