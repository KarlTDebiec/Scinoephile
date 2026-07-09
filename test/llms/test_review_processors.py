#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cross-language review processor edge cases."""

from __future__ import annotations

from unittest.mock import Mock

from pytest import raises

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.guided_review import GuidedReviewManager
from scinoephile.multilang.eng_zho.review import EngZhoGuidedReviewPrompt
from scinoephile.multilang.review.guided import get_guided_reviewer
from scinoephile.multilang.review.pairwise import get_pairwise_reviewer
from test.helpers import assert_series_equal


def test_guided_review_supports_independent_block_sizes():
    """Review one target cue using a guide block containing multiple cues."""
    target = Series(events=[Subtitle(start=0, end=2000, text="Target")])
    guide = Series(
        events=[
            Subtitle(start=0, end=1000, text="Reference one"),
            Subtitle(start=1000, end=2000, text="Reference two"),
        ]
    )
    test_case_cls = GuidedReviewManager.get_test_case_cls(
        1,
        2,
        EngZhoGuidedReviewPrompt,
    )
    query_kwargs = {
        "english_1": "Target",
        "reference_1": "Reference one",
        "reference_2": "Reference two",
    }
    query = test_case_cls.query_cls(**query_kwargs)
    test_case = test_case_cls(
        query=query,
        answer=test_case_cls.answer_cls(),
        verified=True,
    )
    provider = Mock(spec=LLMProvider)
    reviewer = get_guided_reviewer(
        Language.eng,
        Language.zho_hans,
        prompt_cls=EngZhoGuidedReviewPrompt,
        test_cases=[test_case],
        use_dictionary_tool=False,
        provider=provider,
    )

    assert_series_equal(reviewer.process(target, guide), target)
    provider.chat_completion.assert_not_called()


def test_review_processors_preserve_target_without_reference_text():
    """Preserve target cues when a paired block has no reference or guide cues."""
    target = Series(events=[Subtitle(start=0, end=1000, text="Target")])
    empty = Series()
    provider = Mock(spec=LLMProvider)
    pairwise_reviewer = get_pairwise_reviewer(
        Language.eng,
        Language.zho_hans,
        test_cases=[],
        use_dictionary_tool=False,
        provider=provider,
    )
    guided_reviewer = get_guided_reviewer(
        Language.eng,
        Language.zho_hans,
        test_cases=[],
        use_dictionary_tool=False,
        provider=provider,
    )

    assert_series_equal(pairwise_reviewer.process(target, empty), target)
    assert_series_equal(guided_reviewer.process(target, empty), target)
    provider.chat_completion.assert_not_called()


def test_review_processors_honor_zero_stop_index():
    """Return an empty series when processing stops before the first block."""
    target = Series(events=[Subtitle(start=0, end=1000, text="Target")])
    reference = Series(events=[Subtitle(start=0, end=1000, text="Reference")])
    provider = Mock(spec=LLMProvider)
    pairwise_reviewer = get_pairwise_reviewer(
        Language.eng,
        Language.zho_hans,
        test_cases=[],
        use_dictionary_tool=False,
        provider=provider,
    )
    guided_reviewer = get_guided_reviewer(
        Language.eng,
        Language.zho_hans,
        test_cases=[],
        use_dictionary_tool=False,
        provider=provider,
    )

    assert not pairwise_reviewer.process(target, reference, stop_at_idx=0)
    assert not guided_reviewer.process(target, reference, stop_at_idx=0)
    provider.chat_completion.assert_not_called()


def test_review_processors_reject_negative_stop_index():
    """Reject negative exclusive block indices."""
    target = Series(events=[Subtitle(start=0, end=1000, text="Target")])
    reference = Series(events=[Subtitle(start=0, end=1000, text="Reference")])
    provider = Mock(spec=LLMProvider)
    pairwise_reviewer = get_pairwise_reviewer(
        Language.eng,
        Language.zho_hans,
        test_cases=[],
        use_dictionary_tool=False,
        provider=provider,
    )
    guided_reviewer = get_guided_reviewer(
        Language.eng,
        Language.zho_hans,
        test_cases=[],
        use_dictionary_tool=False,
        provider=provider,
    )

    with raises(ValueError, match="greater than or equal to 0"):
        pairwise_reviewer.process(target, reference, stop_at_idx=-1)
    with raises(ValueError, match="greater than or equal to 0"):
        guided_reviewer.process(target, reference, stop_at_idx=-1)
