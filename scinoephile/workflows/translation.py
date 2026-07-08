#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for translating subtitles across supported language pairs."""

from __future__ import annotations

from logging import getLogger

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.lang.id import get_series_language
from scinoephile.multilang.translation.gapped import (
    get_gap_translated,
    get_gap_translator,
)
from scinoephile.multilang.translation.guided import (
    get_guided_translated,
    get_guided_translator,
)
from scinoephile.multilang.translation.standard import get_translated, get_translator

__all__ = [
    "translate_series",
    "translate_series_gapped",
    "translate_series_guided",
]

logger = getLogger(__name__)


def translate_series(
    source: Series,
    *,
    source_language: Language | None = None,
    target_language: Language | None = None,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
) -> Series:
    """Translate a subtitle series between supported languages.

    Arguments:
        source: source-language subtitle series
        source_language: explicit source language, or None to detect it
        target_language: target language
        provider: LLM provider to use
        additional_context: additional context to include in prompts
    Returns:
        translated subtitle series
    Raises:
        ScinoephileError: if a language cannot be resolved or the pair is unsupported
    """
    resolved_source_language = _resolve_language(source, source_language)
    if target_language is None:
        raise ScinoephileError("--target-language is required")

    translator = get_translator(
        resolved_source_language,
        target_language,
        provider=provider,
        additional_context=additional_context,
    )
    return get_translated(
        source,
        resolved_source_language,
        target_language,
        translator=translator,
    )


def translate_series_gapped(
    source: Series,
    target: Series,
    *,
    source_language: Language | None = None,
    target_language: Language | None = None,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
) -> Series:
    """Translate a subtitle series using target-language gaps.

    Arguments:
        source: source-language subtitle series
        target: target-language gapped subtitle series
        source_language: explicit source language, or None to detect it
        target_language: explicit target language, or None to detect it
        provider: LLM provider to use
        additional_context: additional context to include in prompts
    Returns:
        translated subtitle series
    Raises:
        ScinoephileError: if a language cannot be resolved or the pair is unsupported
    """
    resolved_source_language = _resolve_language(source, source_language)
    resolved_target_language = _resolve_language(target, target_language)

    translator = get_gap_translator(
        resolved_source_language,
        resolved_target_language,
        provider=provider,
        additional_context=additional_context,
    )
    return get_gap_translated(
        source,
        target,
        resolved_source_language,
        resolved_target_language,
        translator=translator,
    )


def translate_series_guided(
    source: Series,
    target: Series,
    *,
    source_language: Language | None = None,
    target_language: Language | None = None,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
) -> Series:
    """Translate a subtitle series using target-language guidance.

    Arguments:
        source: source-language subtitle series
        target: target-language guide subtitle series
        source_language: explicit source language, or None to detect it
        target_language: explicit target language, or None to detect it
        provider: LLM provider to use
        additional_context: additional context to include in prompts
    Returns:
        translated subtitle series
    Raises:
        ScinoephileError: if a language cannot be resolved or the pair is unsupported
    """
    resolved_source_language = _resolve_language(source, source_language)
    resolved_target_language = _resolve_language(target, target_language)

    translator = get_guided_translator(
        resolved_source_language,
        resolved_target_language,
        provider=provider,
        additional_context=additional_context,
    )
    return get_guided_translated(
        source,
        target,
        resolved_source_language,
        resolved_target_language,
        translator=translator,
    )


def _resolve_language(
    series: Series,
    explicit_language: Language | None,
) -> Language:
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
            logger.warning(
                f"Explicit language {explicit_language.tag} does not "
                f"match detected language {detected_language.tag}; "
                f"using {explicit_language.tag}"
            )
        return explicit_language
    if detected_language is None:
        raise ScinoephileError("Unable to determine language")
    return detected_language
