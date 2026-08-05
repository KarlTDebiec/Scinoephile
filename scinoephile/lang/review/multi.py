#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Multi-source review helpers."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Unpack

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider, ProcessorKwargs, TestCase
from scinoephile.lang.yue_zho.review import (
    YueZhoMultiReviewPromptYueHant,
    YueZhoMultiReviewPromptYueHantBlockGlobal,
)
from scinoephile.llms import load_shared_test_cases
from scinoephile.llms.multi_review import (
    MultiReviewManager,
    MultiReviewProcessor,
    MultiReviewPrompt,
)
from scinoephile.llms.providers.registry import get_provider

__all__ = ["DEFAULT_PROMPTS", "get_multi_reviewer"]

_YUE_ZHO_JSON_PATHS = (
    Path("kob/output/yue-Hant_transcribe/vad-auto/json/multi_review.json"),
)
"""Default written Cantonese/Chinese multi-review JSON paths."""

DEFAULT_PROMPTS: Mapping[tuple[Language, Language], MultiReviewPrompt] = (
    MappingProxyType(
        {(Language.yue_hant, Language.zho_hant): YueZhoMultiReviewPromptYueHant}
    )
)
"""Multi-review prompts keyed by output and guide languages."""

_JSON_PATHS: Mapping[tuple[Language, Language], tuple[Path, ...]] = MappingProxyType(
    {(Language.yue_hant, Language.zho_hant): _YUE_ZHO_JSON_PATHS}
)
"""Multi-review JSON paths keyed by output and guide languages."""

_BOUNDARY_AWARE_PROMPTS: Mapping[tuple[Language, Language], MultiReviewPrompt] = (
    MappingProxyType(
        {
            (Language.yue_hant, Language.zho_hant): (
                YueZhoMultiReviewPromptYueHantBlockGlobal
            )
        }
    )
)
"""Boundary-aware block-global prompts keyed by output and guide languages."""


def get_multi_reviewer(
    language: Language,
    guide_language: Language,
    prompt: MultiReviewPrompt | None = None,
    shared_test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    *,
    boundary_aware: bool = False,
    **kwargs: Unpack[ProcessorKwargs],
) -> MultiReviewProcessor:
    """Get a multi-source reviewer for a supported language pair.

    Arguments:
        language: language of subtitle sources and output
        guide_language: language of guide subtitles
        prompt: text for LLM correspondence
        shared_test_cases: shared test cases
        provider: provider to use for queries
        boundary_aware: whether to use block-global boundary reconciliation when
            `prompt` is None
        **kwargs: additional processor keyword arguments
    Returns:
        configured multi-review processor
    Raises:
        ScinoephileError: if multi-review does not support the language pair
    """
    key = (language, guide_language)
    if key not in DEFAULT_PROMPTS:
        raise ScinoephileError(
            "Multi-review does not support language pair "
            f"{language.code} <- {guide_language.code}"
        )
    if prompt is None:
        if boundary_aware:
            prompt = _BOUNDARY_AWARE_PROMPTS[key]
        else:
            prompt = DEFAULT_PROMPTS[key]
    if shared_test_cases is None:
        if prompt.boundary_aware:
            shared_test_cases = []
        else:
            shared_test_cases = list(
                load_shared_test_cases(MultiReviewManager, prompt, _JSON_PATHS[key])
            )
    if provider is None:
        provider = get_provider()
    return MultiReviewProcessor(prompt, shared_test_cases, provider=provider, **kwargs)
