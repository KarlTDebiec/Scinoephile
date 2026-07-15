#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared workflow helpers."""

from __future__ import annotations

from logging import getLogger

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.lang.id import get_series_language

__all__ = ["resolve_language"]

logger = getLogger(__name__)


def resolve_language(series: Series, explicit_language: Language | None) -> Language:
    """Resolve a detected or explicit language for a subtitle series.

    Arguments:
        series: subtitle series to classify
        explicit_language: explicit language argument, if provided
    Returns:
        resolved language
    Raises:
        ScinoephileError: if language detection fails and no explicit language exists
    """
    detected_language = get_series_language(series)
    if explicit_language is not None:
        if detected_language is not None and detected_language is not explicit_language:
            message = (
                f"Explicit language {explicit_language.code} does not "
                f"match detected language {detected_language.code}; "
                f"using {explicit_language.code}"
            )
            if (
                explicit_language.is_chinese
                and detected_language.is_chinese
                and explicit_language.script == detected_language.script
            ):
                logger.info(message)
            else:
                logger.warning(message)
        return explicit_language
    if detected_language is None:
        raise ScinoephileError("Unable to determine language")
    return detected_language
