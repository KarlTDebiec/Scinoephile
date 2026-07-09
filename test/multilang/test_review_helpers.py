#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cross-language review helper selection."""

from __future__ import annotations

from unittest.mock import Mock

from pytest import param, raises

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider
from scinoephile.llms.guided_review import GuidedReviewPrompt
from scinoephile.llms.pairwise_review import PairwiseReviewPrompt
from scinoephile.multilang.eng_yue.review import (
    EngYueGuidedReviewPrompt,
    EngYuePairwiseReviewPrompt,
)
from scinoephile.multilang.eng_zho.review import (
    EngZhoGuidedReviewPrompt,
    EngZhoPairwiseReviewPrompt,
)
from scinoephile.multilang.review.guided import get_guided_reviewer
from scinoephile.multilang.review.pairwise import get_pairwise_reviewer
from scinoephile.multilang.yue_eng.review import (
    YueEngGuidedReviewPromptYueHans,
    YueEngGuidedReviewPromptYueHant,
    YueEngPairwiseReviewPromptYueHans,
    YueEngPairwiseReviewPromptYueHant,
)
from scinoephile.multilang.yue_zho.review import (
    YueZhoGuidedReviewPromptYueHans,
    YueZhoGuidedReviewPromptYueHant,
    YueZhoPairwiseReviewPromptYueHans,
    YueZhoPairwiseReviewPromptYueHant,
)
from scinoephile.multilang.zho_eng.review import (
    ZhoEngGuidedReviewPromptZhoHans,
    ZhoEngGuidedReviewPromptZhoHant,
    ZhoEngPairwiseReviewPromptZhoHans,
    ZhoEngPairwiseReviewPromptZhoHant,
)
from scinoephile.multilang.zho_yue.review import (
    ZhoYueGuidedReviewPromptZhoHans,
    ZhoYueGuidedReviewPromptZhoHant,
    ZhoYuePairwiseReviewPromptZhoHans,
    ZhoYuePairwiseReviewPromptZhoHant,
)
from test.helpers import parametrize


@parametrize(
    ("language", "reference_language", "pairwise_prompt_cls", "guided_prompt_cls"),
    [
        param(
            Language.eng,
            Language.yue_hans,
            EngYuePairwiseReviewPrompt,
            EngYueGuidedReviewPrompt,
            id="eng-yue-hans",
        ),
        param(
            Language.eng,
            Language.yue_hant,
            EngYuePairwiseReviewPrompt,
            EngYueGuidedReviewPrompt,
            id="eng-yue-hant",
        ),
        param(
            Language.eng,
            Language.zho_hans,
            EngZhoPairwiseReviewPrompt,
            EngZhoGuidedReviewPrompt,
            id="eng-zho-hans",
        ),
        param(
            Language.eng,
            Language.zho_hant,
            EngZhoPairwiseReviewPrompt,
            EngZhoGuidedReviewPrompt,
            id="eng-zho-hant",
        ),
        param(
            Language.yue_hans,
            Language.eng,
            YueEngPairwiseReviewPromptYueHans,
            YueEngGuidedReviewPromptYueHans,
            id="yue-hans-eng",
        ),
        param(
            Language.yue_hans,
            Language.zho_hans,
            YueZhoPairwiseReviewPromptYueHans,
            YueZhoGuidedReviewPromptYueHans,
            id="yue-hans-zho-hans",
        ),
        param(
            Language.yue_hans,
            Language.zho_hant,
            YueZhoPairwiseReviewPromptYueHans,
            YueZhoGuidedReviewPromptYueHans,
            id="yue-hans-zho-hant",
        ),
        param(
            Language.yue_hant,
            Language.eng,
            YueEngPairwiseReviewPromptYueHant,
            YueEngGuidedReviewPromptYueHant,
            id="yue-hant-eng",
        ),
        param(
            Language.yue_hant,
            Language.zho_hans,
            YueZhoPairwiseReviewPromptYueHant,
            YueZhoGuidedReviewPromptYueHant,
            id="yue-hant-zho-hans",
        ),
        param(
            Language.yue_hant,
            Language.zho_hant,
            YueZhoPairwiseReviewPromptYueHant,
            YueZhoGuidedReviewPromptYueHant,
            id="yue-hant-zho-hant",
        ),
        param(
            Language.zho_hans,
            Language.eng,
            ZhoEngPairwiseReviewPromptZhoHans,
            ZhoEngGuidedReviewPromptZhoHans,
            id="zho-hans-eng",
        ),
        param(
            Language.zho_hans,
            Language.yue_hans,
            ZhoYuePairwiseReviewPromptZhoHans,
            ZhoYueGuidedReviewPromptZhoHans,
            id="zho-hans-yue-hans",
        ),
        param(
            Language.zho_hans,
            Language.yue_hant,
            ZhoYuePairwiseReviewPromptZhoHans,
            ZhoYueGuidedReviewPromptZhoHans,
            id="zho-hans-yue-hant",
        ),
        param(
            Language.zho_hant,
            Language.eng,
            ZhoEngPairwiseReviewPromptZhoHant,
            ZhoEngGuidedReviewPromptZhoHant,
            id="zho-hant-eng",
        ),
        param(
            Language.zho_hant,
            Language.yue_hans,
            ZhoYuePairwiseReviewPromptZhoHant,
            ZhoYueGuidedReviewPromptZhoHant,
            id="zho-hant-yue-hans",
        ),
        param(
            Language.zho_hant,
            Language.yue_hant,
            ZhoYuePairwiseReviewPromptZhoHant,
            ZhoYueGuidedReviewPromptZhoHant,
            id="zho-hant-yue-hant",
        ),
    ],
)
def test_review_helpers_select_prompts(
    language: Language,
    reference_language: Language,
    pairwise_prompt_cls: type[PairwiseReviewPrompt],
    guided_prompt_cls: type[GuidedReviewPrompt],
):
    """Select script-aware prompts for each supported directed language pair."""
    provider = Mock(spec=LLMProvider)
    pairwise_reviewer = get_pairwise_reviewer(
        language,
        reference_language,
        test_cases=[],
        use_dictionary_tool=False,
        provider=provider,
    )
    guided_reviewer = get_guided_reviewer(
        language,
        reference_language,
        test_cases=[],
        use_dictionary_tool=False,
        provider=provider,
    )

    assert pairwise_reviewer.prompt_cls is pairwise_prompt_cls
    assert guided_reviewer.prompt_cls is guided_prompt_cls


def test_review_helpers_reject_same_language_pair():
    """Reject a language pair without a cross-language review prompt."""
    provider = Mock(spec=LLMProvider)
    with raises(ScinoephileError, match="does not support language pair"):
        get_pairwise_reviewer(
            Language.eng,
            Language.eng,
            test_cases=[],
            provider=provider,
        )
    with raises(ScinoephileError, match="does not support language pair"):
        get_guided_reviewer(
            Language.eng,
            Language.eng,
            test_cases=[],
            provider=provider,
        )
