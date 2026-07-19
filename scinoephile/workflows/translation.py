#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for translating subtitles across supported language pairs."""

from __future__ import annotations

from typing import Unpack

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, ProcessorKwargs, TestCase
from scinoephile.core.subtitles import Series
from scinoephile.lang.translation.gap import get_gap_translator
from scinoephile.lang.translation.guided import get_guided_translator
from scinoephile.lang.translation.standard import get_translator
from scinoephile.llms.gap_translation import (
    GapTranslationProcessor,
    GapTranslationPrompt,
)
from scinoephile.llms.guided_translation import (
    GuidedTranslationProcessor,
    GuidedTranslationPrompt,
)
from scinoephile.llms.translation import TranslationProcessor, TranslationPrompt

from .helpers import resolve_language

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
    prompt: TranslationPrompt | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    translator: TranslationProcessor | None = None,
    start_at_idx: int = 0,
    stop_at_idx: int | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> Series:
    """Translate a subtitle series between supported languages.

    Arguments:
        source: source-language subtitle series
        source_language: explicit source language, or None to detect it
        target_language: target language
        prompt: prompt override
        test_cases: test cases
        provider: LLM provider to use
        translator: translator to use, or None to construct one
        start_at_idx: inclusive block index at which to start processing
        stop_at_idx: exclusive block index at which to stop processing
        **kwargs: additional keyword arguments for TranslationProcessor
    Returns:
        translated subtitle series
    Raises:
        ScinoephileError: if a language cannot be resolved or the pair is unsupported
    """
    resolved_source_language = resolve_language(source, source_language)

    if translator is None:
        translator = get_translator(
            resolved_source_language,
            target_language,
            prompt,
            test_cases,
            provider,
            **kwargs,
        )
    return translator.process(
        source,
        stop_at_idx=stop_at_idx,
        start_at_idx=start_at_idx,
    )


def translate_series_gaps(
    source: Series,
    target: Series,
    *,
    source_language: Language | None = None,
    target_language: Language | None = None,
    prompt: GapTranslationPrompt | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    translator: GapTranslationProcessor | None = None,
    start_at_idx: int = 0,
    stop_at_idx: int | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> Series:
    """Translate a subtitle series using target-language gaps.

    Arguments:
        source: source-language subtitle series
        target: target-language gapped subtitle series
        source_language: explicit source language, or None to detect it
        target_language: explicit target language, or None to detect it
        prompt: prompt override
        test_cases: test cases
        provider: LLM provider to use
        translator: translator to use, or None to construct one
        start_at_idx: inclusive block index at which to start processing
        stop_at_idx: exclusive block index at which to stop processing
        **kwargs: additional keyword arguments for GapTranslationProcessor
    Returns:
        translated subtitle series
    Raises:
        ScinoephileError: if a language cannot be resolved or the pair is unsupported
    """
    resolved_source_language = resolve_language(source, source_language)
    resolved_target_language = resolve_language(target, target_language)

    if translator is None:
        translator = get_gap_translator(
            resolved_source_language,
            resolved_target_language,
            prompt,
            test_cases,
            provider,
            **kwargs,
        )
    return translator.process(
        target,
        source,
        stop_at_idx=stop_at_idx,
        start_at_idx=start_at_idx,
    )


def translate_series_guided(
    source: Series,
    guide: Series,
    *,
    source_language: Language | None = None,
    target_language: Language | None = None,
    prompt: GuidedTranslationPrompt | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    translator: GuidedTranslationProcessor | None = None,
    start_at_idx: int = 0,
    stop_at_idx: int | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> Series:
    """Translate a subtitle series using target-language guidance.

    Arguments:
        source: source-language subtitle series
        guide: target-language guide subtitle series
        source_language: explicit source language, or None to detect it
        target_language: explicit target language, or None to detect it
        prompt: prompt override
        test_cases: test cases
        provider: LLM provider to use
        translator: translator to use, or None to construct one
        start_at_idx: inclusive block index at which to start processing
        stop_at_idx: exclusive block index at which to stop processing
        **kwargs: additional keyword arguments for GuidedTranslationProcessor
    Returns:
        translated subtitle series
    Raises:
        ScinoephileError: if a language cannot be resolved or the pair is unsupported
    """
    resolved_source_language = resolve_language(source, source_language)
    resolved_target_language = resolve_language(guide, target_language)

    if translator is None:
        translator = get_guided_translator(
            resolved_source_language,
            resolved_target_language,
            prompt,
            test_cases,
            provider,
            **kwargs,
        )
    return translator.process(
        source,
        guide,
        stop_at_idx=stop_at_idx,
        start_at_idx=start_at_idx,
    )
