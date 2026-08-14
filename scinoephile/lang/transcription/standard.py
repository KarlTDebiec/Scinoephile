#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Language-specific LLM transcription configuration."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Unpack

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider, ProcessorKwargs, TestCase
from scinoephile.lang.yue.transcription import (
    YueTranscriptionAlignmentScorer,
    YueTranscriptionPromptYueHans,
    YueTranscriptionPromptYueHant,
)
from scinoephile.llms import load_shared_test_cases
from scinoephile.llms.providers.registry import get_provider
from scinoephile.llms.transcription import (
    TranscriptionManager,
    TranscriptionProcessor,
    TranscriptionPrompt,
)

__all__ = ["DEFAULT_PROMPTS", "YueTranscriptionManager", "get_transcriber"]

_YUE_HANS_TRANSCRIPTION_JSON_PATHS: tuple[Path, ...] = ()
"""Default simplified Yue transcription JSON paths."""

_YUE_HANT_TRANSCRIPTION_JSON_PATHS: tuple[Path, ...] = ()
"""Default traditional Yue transcription JSON paths."""

_JSON_PATHS: dict[Language, tuple[Path, ...]] = {
    Language.yue_hans: _YUE_HANS_TRANSCRIPTION_JSON_PATHS,
    Language.yue_hant: _YUE_HANT_TRANSCRIPTION_JSON_PATHS,
}
"""Transcription JSON paths keyed by language."""


class YueTranscriptionManager(TranscriptionManager):
    """Transcription models using Yue evidence scoring."""

    alignment_scorer = YueTranscriptionAlignmentScorer()
    """Yue scorer assigned to generated test-case classes."""


class _YueTranscriptionProcessor(TranscriptionProcessor):
    """Transcription processor using Yue evidence scoring."""

    manager_cls = YueTranscriptionManager
    """Manager used to construct Yue-aware test-case models."""


DEFAULT_PROMPTS: Mapping[Language, TranscriptionPrompt] = MappingProxyType(
    {
        Language.yue_hans: YueTranscriptionPromptYueHans,
        Language.yue_hant: YueTranscriptionPromptYueHant,
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
    if shared_test_cases is None:
        shared_test_cases = list(
            load_shared_test_cases(
                YueTranscriptionManager, prompt, _JSON_PATHS[language]
            )
        )
    if provider is None:
        provider = get_provider()
    return _YueTranscriptionProcessor(
        prompt, shared_test_cases, provider=provider, **kwargs
    )
