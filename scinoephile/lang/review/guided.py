#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Guided review helpers."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Unpack

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider, ProcessorKwargs, TestCase
from scinoephile.lang.eng_yue.review import EngYueGuidedReviewPrompt
from scinoephile.lang.eng_zho.review import EngZhoGuidedReviewPrompt
from scinoephile.lang.yue_eng.review import (
    YueEngGuidedReviewPromptYueHans,
    YueEngGuidedReviewPromptYueHant,
)
from scinoephile.lang.yue_zho.review import (
    YueZhoGuidedReviewPromptYueHans,
    YueZhoGuidedReviewPromptYueHant,
)
from scinoephile.lang.zho_eng.review import (
    ZhoEngGuidedReviewPromptZhoHans,
    ZhoEngGuidedReviewPromptZhoHant,
)
from scinoephile.lang.zho_yue.review import (
    ZhoYueGuidedReviewPromptZhoHans,
    ZhoYueGuidedReviewPromptZhoHant,
)
from scinoephile.llms import load_default_test_cases
from scinoephile.llms.guided_review import (
    GuidedReviewManager,
    GuidedReviewProcessor,
    GuidedReviewPrompt,
)
from scinoephile.llms.providers.registry import get_provider

__all__ = [
    "DEFAULT_PROMPTS",
    "get_guided_reviewer",
]

_YUE_ZHO_JSON_PATHS = (
    Path("mlamd/output/yue-Hans_transcribe/lang/yue_zho/guided_review/cuda.json"),
    Path("mlamd/output/yue-Hans_transcribe/lang/yue_zho/guided_review/cpu.json"),
    Path("mlamd/output/yue-Hans_transcribe/lang/yue_zho/guided_review/mps.json"),
)
"""Default written Cantonese/Chinese guided-review JSON paths."""

DEFAULT_PROMPTS: Mapping[tuple[Language, Language], GuidedReviewPrompt] = (
    MappingProxyType(
        {
            (Language.eng, Language.yue_hans): EngYueGuidedReviewPrompt,
            (Language.eng, Language.yue_hant): EngYueGuidedReviewPrompt,
            (Language.eng, Language.zho_hans): EngZhoGuidedReviewPrompt,
            (Language.eng, Language.zho_hant): EngZhoGuidedReviewPrompt,
            (Language.yue_hans, Language.eng): YueEngGuidedReviewPromptYueHans,
            (Language.yue_hans, Language.zho_hans): YueZhoGuidedReviewPromptYueHans,
            (Language.yue_hans, Language.zho_hant): YueZhoGuidedReviewPromptYueHans,
            (Language.yue_hant, Language.eng): YueEngGuidedReviewPromptYueHant,
            (Language.yue_hant, Language.zho_hans): YueZhoGuidedReviewPromptYueHant,
            (Language.yue_hant, Language.zho_hant): YueZhoGuidedReviewPromptYueHant,
            (Language.zho_hans, Language.eng): ZhoEngGuidedReviewPromptZhoHans,
            (Language.zho_hans, Language.yue_hans): ZhoYueGuidedReviewPromptZhoHans,
            (Language.zho_hans, Language.yue_hant): ZhoYueGuidedReviewPromptZhoHans,
            (Language.zho_hant, Language.eng): ZhoEngGuidedReviewPromptZhoHant,
            (Language.zho_hant, Language.yue_hans): ZhoYueGuidedReviewPromptZhoHant,
            (Language.zho_hant, Language.yue_hant): ZhoYueGuidedReviewPromptZhoHant,
        }
    )
)
"""Guided review prompts keyed by reviewed and guide languages."""

_JSON_PATHS: dict[tuple[Language, Language], tuple[Path, ...]] = {
    key: (
        _YUE_ZHO_JSON_PATHS
        if key[0] in (Language.yue_hans, Language.yue_hant)
        and key[1] in (Language.zho_hans, Language.zho_hant)
        else ()
    )
    for key in DEFAULT_PROMPTS
}
"""Guided review JSON paths keyed by reviewed and guide languages."""


def get_guided_reviewer(
    language: Language,
    guide_language: Language,
    prompt: GuidedReviewPrompt | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> GuidedReviewProcessor:
    """Get a guided reviewer for a supported language pair.

    Arguments:
        language: language of subtitles to review
        guide_language: language of guide subtitles
        prompt: text for LLM correspondence
        test_cases: test cases
        provider: provider to use for queries
        **kwargs: additional processor keyword arguments
    Returns:
        configured guided review processor
    Raises:
        ScinoephileError: if guided review does not support the language pair
    """
    key = (language, guide_language)
    if key not in DEFAULT_PROMPTS:
        raise ScinoephileError(
            "Guided review does not support language pair "
            f"{language.tag} <- {guide_language.tag}"
        )
    if prompt is None:
        prompt = DEFAULT_PROMPTS[key]
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(GuidedReviewManager, prompt, _JSON_PATHS[key])
        )
    if provider is None:
        provider = get_provider()
    return GuidedReviewProcessor(prompt, test_cases, provider=provider, **kwargs)
