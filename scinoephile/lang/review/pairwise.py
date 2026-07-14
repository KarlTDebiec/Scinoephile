#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pairwise review helpers."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Unpack

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider, ProcessorKwargs, TestCase
from scinoephile.lang.eng_yue.review import EngYuePairwiseReviewPrompt
from scinoephile.lang.eng_zho.review import EngZhoPairwiseReviewPrompt
from scinoephile.lang.yue_eng.review import (
    YueEngPairwiseReviewPromptYueHans,
    YueEngPairwiseReviewPromptYueHant,
)
from scinoephile.lang.yue_zho.review import (
    YueZhoPairwiseReviewPromptYueHans,
    YueZhoPairwiseReviewPromptYueHant,
)
from scinoephile.lang.zho_eng.review import (
    ZhoEngPairwiseReviewPromptZhoHans,
    ZhoEngPairwiseReviewPromptZhoHant,
)
from scinoephile.lang.zho_yue.review import (
    ZhoYuePairwiseReviewPromptZhoHans,
    ZhoYuePairwiseReviewPromptZhoHant,
)
from scinoephile.llms import load_default_test_cases
from scinoephile.llms.pairwise_review import (
    PairwiseReviewManager,
    PairwiseReviewProcessor,
    PairwiseReviewPrompt,
)
from scinoephile.llms.providers.registry import get_provider

__all__ = [
    "DEFAULT_PROMPTS",
    "get_pairwise_reviewer",
]

_YUE_ZHO_JSON_PATHS = (
    Path("mlamd/output/yue-Hans_transcribe/lang/yue_zho/pairwise_review/cuda.json"),
    Path("mlamd/output/yue-Hans_transcribe/lang/yue_zho/pairwise_review/cpu.json"),
    Path("mlamd/output/yue-Hans_transcribe/lang/yue_zho/pairwise_review/mps.json"),
)
"""Default written Cantonese/Chinese pairwise-review JSON paths."""

DEFAULT_PROMPTS: Mapping[tuple[Language, Language], PairwiseReviewPrompt] = (
    MappingProxyType(
        {
            (Language.eng, Language.yue_hans): EngYuePairwiseReviewPrompt,
            (Language.eng, Language.yue_hant): EngYuePairwiseReviewPrompt,
            (Language.eng, Language.zho_hans): EngZhoPairwiseReviewPrompt,
            (Language.eng, Language.zho_hant): EngZhoPairwiseReviewPrompt,
            (Language.yue_hans, Language.eng): YueEngPairwiseReviewPromptYueHans,
            (Language.yue_hans, Language.zho_hans): YueZhoPairwiseReviewPromptYueHans,
            (Language.yue_hans, Language.zho_hant): YueZhoPairwiseReviewPromptYueHans,
            (Language.yue_hant, Language.eng): YueEngPairwiseReviewPromptYueHant,
            (Language.yue_hant, Language.zho_hans): YueZhoPairwiseReviewPromptYueHant,
            (Language.yue_hant, Language.zho_hant): YueZhoPairwiseReviewPromptYueHant,
            (Language.zho_hans, Language.eng): ZhoEngPairwiseReviewPromptZhoHans,
            (Language.zho_hans, Language.yue_hans): ZhoYuePairwiseReviewPromptZhoHans,
            (Language.zho_hans, Language.yue_hant): ZhoYuePairwiseReviewPromptZhoHans,
            (Language.zho_hant, Language.eng): ZhoEngPairwiseReviewPromptZhoHant,
            (Language.zho_hant, Language.yue_hans): ZhoYuePairwiseReviewPromptZhoHant,
            (Language.zho_hant, Language.yue_hant): ZhoYuePairwiseReviewPromptZhoHant,
        }
    )
)
"""Pairwise review prompts keyed by reviewed and reference languages."""

_JSON_PATHS: dict[tuple[Language, Language], tuple[Path, ...]] = {
    (Language.eng, Language.yue_hans): (),
    (Language.eng, Language.yue_hant): (),
    (Language.eng, Language.zho_hans): (),
    (Language.eng, Language.zho_hant): (),
    (Language.yue_hans, Language.eng): (),
    (Language.yue_hans, Language.zho_hans): _YUE_ZHO_JSON_PATHS,
    (Language.yue_hans, Language.zho_hant): _YUE_ZHO_JSON_PATHS,
    (Language.yue_hant, Language.eng): (),
    (Language.yue_hant, Language.zho_hans): _YUE_ZHO_JSON_PATHS,
    (Language.yue_hant, Language.zho_hant): _YUE_ZHO_JSON_PATHS,
    (Language.zho_hans, Language.eng): (),
    (Language.zho_hans, Language.yue_hans): (),
    (Language.zho_hans, Language.yue_hant): (),
    (Language.zho_hant, Language.eng): (),
    (Language.zho_hant, Language.yue_hans): (),
    (Language.zho_hant, Language.yue_hant): (),
}
"""Pairwise review JSON paths keyed by reviewed and reference languages."""


def get_pairwise_reviewer(
    language: Language,
    reference_language: Language,
    prompt: PairwiseReviewPrompt | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> PairwiseReviewProcessor:
    """Get a pairwise reviewer for a supported language pair.

    Arguments:
        language: language of subtitles to review
        reference_language: language of reference subtitles
        prompt: text for LLM correspondence
        test_cases: test cases
        provider: provider to use for queries
        **kwargs: additional processor keyword arguments
    Returns:
        configured pairwise review processor
    Raises:
        ScinoephileError: if pairwise review does not support the language pair
    """
    key = (language, reference_language)
    if key not in DEFAULT_PROMPTS:
        raise ScinoephileError(
            "Pairwise review does not support language pair "
            f"{language.tag} <- {reference_language.tag}"
        )
    if prompt is None:
        prompt = DEFAULT_PROMPTS[key]
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(PairwiseReviewManager, prompt, _JSON_PATHS[key])
        )
    if provider is None:
        provider = get_provider()
    return PairwiseReviewProcessor(prompt, test_cases, provider=provider, **kwargs)
