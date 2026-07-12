#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for reusable LLM test-case subtitle models."""

from __future__ import annotations

from pydantic import ValidationError
from pytest import raises

from scinoephile.core.llms import (
    AnnotatedTestCaseSubtitle as AnnotatedSubtitle,
)
from scinoephile.core.llms import (
    TestCaseSubtitle as Subtitle,
)


def test_test_case_subtitle_requires_positive_index():
    """Test-case subtitle indexes should be one-based."""
    subtitle = Subtitle(index=1, text="subtitle")

    assert subtitle.model_dump() == {"index": 1, "text": "subtitle"}
    with raises(ValidationError, match="greater than or equal to 1"):
        Subtitle(index=0, text="subtitle")
    with raises(ValidationError, match="Extra inputs are not permitted"):
        Subtitle.model_validate({"index": 1, "text": "subtitle", "unexpected": True})


def test_annotated_test_case_subtitle_includes_note():
    """Annotated test-case subtitles should include explanatory notes."""
    subtitle = AnnotatedSubtitle(index=1, text="revision", note="typo")

    assert subtitle.model_dump() == {
        "index": 1,
        "text": "revision",
        "note": "typo",
    }
    with raises(ValidationError, match="at least 1 character"):
        AnnotatedSubtitle(index=1, text="revision", note="")
