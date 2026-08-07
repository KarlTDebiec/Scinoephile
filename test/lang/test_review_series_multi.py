#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for the multi-source review workflow."""

from __future__ import annotations

from unittest.mock import Mock

from scinoephile.core import Language
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.review.multi import get_multi_reviewer
from scinoephile.lang.yue_zho.review import (
    YueZhoMultiReviewPromptYueHant,
    YueZhoMultiReviewPromptYueHantBlockGlobal,
)
from scinoephile.llms.multi_review import MultiReviewProcessor
from scinoephile.workflows.review import review_series_multi


def test_review_series_multi_delegates_named_sources_and_block_range():
    """Workflow should resolve languages and delegate named sources unchanged."""
    sources = {
        "whisper": Series(events=[Subtitle(start=0, end=1000, text="一")]),
        "mimo": Series(events=[Subtitle(start=0, end=1000, text="二")]),
        "qwen": Series(events=[Subtitle(start=0, end=1000, text="三")]),
    }
    guide = Series(events=[Subtitle(start=0, end=1000, text="指引")])
    expected = Series(events=[Subtitle(start=0, end=1000, text="輸出")])
    reviewer = Mock(spec=MultiReviewProcessor)
    reviewer.process.return_value = expected

    output = review_series_multi(
        sources,
        guide,
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        reviewer=reviewer,
        start_at_idx=2,
        stop_at_idx=4,
    )

    assert output is expected
    reviewer.process.assert_called_once_with(
        sources, guide, stop_at_idx=4, start_at_idx=2
    )


def test_get_multi_reviewer_selects_boundary_aware_prompt_only_when_enabled():
    """The alternative prompt should be opt-in and leave the default unchanged."""
    default = get_multi_reviewer(
        Language.yue_hant, Language.zho_hant, shared_test_cases=[], provider=Mock()
    )
    boundary_aware = get_multi_reviewer(
        Language.yue_hant,
        Language.zho_hant,
        shared_test_cases=[],
        provider=Mock(),
        boundary_aware=True,
    )

    assert default.prompt is YueZhoMultiReviewPromptYueHant
    assert boundary_aware.prompt is YueZhoMultiReviewPromptYueHantBlockGlobal
