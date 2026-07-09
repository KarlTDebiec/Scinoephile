#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for translating subtitles across supported language pairs."""

from __future__ import annotations

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.llms.gap_translation import GapTranslationProcessor
from scinoephile.llms.guided_translation import GuidedTranslationProcessor
from scinoephile.llms.translation import TranslationProcessor
from scinoephile.multilang.translation.gap import get_gap_translator
from scinoephile.multilang.translation.guided import get_guided_translator
from scinoephile.multilang.translation.standard import get_translator

from .helpers import resolve_series_language

__all__ = [
    "translate_series",
    "translate_series_gaps",
    "translate_series_guided",
]


def translate_series(
    source: Series,
    *,
    target_language: Language,
    source_language: Language | None = None,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
    translator: TranslationProcessor | None = None,
) -> Series:
    """Translate a subtitle series between supported languages.

    Arguments:
        source: source-language subtitle series
        source_language: explicit source language, or None to detect it
        target_language: target language
        provider: LLM provider to use
        additional_context: additional context to include in prompts
        translator: translator to use, or None to construct one
    Returns:
        translated subtitle series
    Raises:
        ScinoephileError: if a language cannot be resolved or the pair is unsupported
    """
    resolved_source_language = resolve_series_language(source, source_language)

    if translator is None:
        translator = get_translator(
            resolved_source_language,
            target_language,
            provider=provider,
            additional_context=additional_context,
        )
    return translator.process(source)


def translate_series_gaps(
    source: Series,
    target: Series,
    *,
    source_language: Language | None = None,
    target_language: Language | None = None,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
    translator: GapTranslationProcessor | None = None,
) -> Series:
    """Translate a subtitle series using target-language gaps.

    Arguments:
        source: source-language subtitle series
        target: target-language gapped subtitle series
        source_language: explicit source language, or None to detect it
        target_language: explicit target language, or None to detect it
        provider: LLM provider to use
        additional_context: additional context to include in prompts
        translator: translator to use, or None to construct one
    Returns:
        translated subtitle series
    Raises:
        ScinoephileError: if a language cannot be resolved or the pair is unsupported
    """
    resolved_source_language = resolve_series_language(source, source_language)
    resolved_target_language = resolve_series_language(target, target_language)

    if translator is None:
        translator = get_gap_translator(
            resolved_source_language,
            resolved_target_language,
            provider=provider,
            additional_context=additional_context,
        )
    return translator.process(target, source)


def translate_series_guided(
    source: Series,
    guide: Series,
    *,
    source_language: Language | None = None,
    target_language: Language | None = None,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
    translator: GuidedTranslationProcessor | None = None,
) -> Series:
    """Translate a subtitle series using target-language guidance.

    Arguments:
        source: source-language subtitle series
        guide: target-language guide subtitle series
        source_language: explicit source language, or None to detect it
        target_language: explicit target language, or None to detect it
        provider: LLM provider to use
        additional_context: additional context to include in prompts
        translator: translator to use, or None to construct one
    Returns:
        translated subtitle series
    Raises:
        ScinoephileError: if a language cannot be resolved or the pair is unsupported
    """
    resolved_source_language = resolve_series_language(source, source_language)
    resolved_target_language = resolve_series_language(guide, target_language)

    if translator is None:
        translator = get_guided_translator(
            resolved_source_language,
            resolved_target_language,
            provider=provider,
            additional_context=additional_context,
        )
    return translator.process(source, guide)
