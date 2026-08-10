#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Language-specific aligned transcription merger configuration."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Unpack

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider, ProcessorKwargs, TestCase
from scinoephile.llms.aligned_transcription_merge import (
    AlignedTranscriptionMergeProcessor,
    AlignedTranscriptionMergePrompt,
)
from scinoephile.llms.providers.registry import get_provider

from ..yue.aligned_transcription_merge import (
    AlignedTranscriptionMergePromptYueHans,
    AlignedTranscriptionMergePromptYueHant,
)

__all__ = ["DEFAULT_PROMPTS", "get_aligned_transcription_merger"]


DEFAULT_PROMPTS: Mapping[Language, AlignedTranscriptionMergePrompt] = MappingProxyType(
    {
        Language.yue_hans: AlignedTranscriptionMergePromptYueHans,
        Language.yue_hant: AlignedTranscriptionMergePromptYueHant,
    }
)
"""Aligned transcription merge prompts keyed by output language."""


def get_aligned_transcription_merger(
    language: Language,
    prompt: AlignedTranscriptionMergePrompt | None = None,
    shared_test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> AlignedTranscriptionMergeProcessor:
    """Get an aligned transcription merger for a supported language.

    Arguments:
        language: language of ASR sources and consensus output
        prompt: text for LLM correspondence
        shared_test_cases: shared verified test cases
        provider: provider to use for queries
        **kwargs: additional processor keyword arguments
    Returns:
        configured aligned transcription merge processor
    Raises:
        ScinoephileError: if aligned merging does not support the language
    """
    if language not in DEFAULT_PROMPTS:
        raise ScinoephileError(
            f"Aligned transcription merging does not support {language.code}."
        )
    if prompt is None:
        prompt = DEFAULT_PROMPTS[language]
    if provider is None:
        provider = get_provider()
    return AlignedTranscriptionMergeProcessor(
        prompt, shared_test_cases or [], provider=provider, **kwargs
    )
