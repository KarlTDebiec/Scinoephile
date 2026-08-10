#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Language-specific LLM transcription configuration."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Unpack

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider, ProcessorKwargs, TestCase
from scinoephile.lang.yue.transcription import (
    TranscriptionPromptYueHans,
    TranscriptionPromptYueHant,
)
from scinoephile.llms.providers.registry import get_provider
from scinoephile.llms.transcription import TranscriptionProcessor, TranscriptionPrompt

__all__ = ["DEFAULT_PROMPTS", "get_transcriber"]


DEFAULT_PROMPTS: Mapping[Language, TranscriptionPrompt] = MappingProxyType(
    {
        Language.yue_hans: TranscriptionPromptYueHans,
        Language.yue_hant: TranscriptionPromptYueHant,
    }
)
"""Transcription prompts keyed by output language."""


def get_transcriber(
    language: Language,
    prompt: TranscriptionPrompt | None = None,
    shared_test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> TranscriptionProcessor:
    """Get a transcriber for a supported language.

    Arguments:
        language: language of ASR sources and consensus output
        prompt: text for LLM correspondence
        shared_test_cases: shared verified test cases
        provider: provider to use for queries
        **kwargs: additional processor keyword arguments
    Returns:
        configured transcription processor
    Raises:
        ScinoephileError: if transcription does not support the language
    """
    if language not in DEFAULT_PROMPTS:
        raise ScinoephileError(f"Transcription does not support {language.code}.")
    if prompt is None:
        prompt = DEFAULT_PROMPTS[language]
    if provider is None:
        provider = get_provider()
    return TranscriptionProcessor(
        prompt, shared_test_cases or [], provider=provider, **kwargs
    )
