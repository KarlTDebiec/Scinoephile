#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for operation-specific no-op LLM answers."""

from __future__ import annotations

from scinoephile.llms.delineation import DelineationQuery, DelineationTestCase
from scinoephile.llms.gap_translation import GapTranslationQuery, GapTranslationTestCase
from scinoephile.llms.guided_review import GuidedReviewQuery, GuidedReviewTestCase
from scinoephile.llms.guided_translation import (
    GuidedTranslationQuery,
    GuidedTranslationTestCase,
)
from scinoephile.llms.multi_review import MultiReviewQuery, MultiReviewTestCase
from scinoephile.llms.ocr_fusion import OcrFusionQuery, OcrFusionTestCase
from scinoephile.llms.punctuation import PunctuationQuery, PunctuationTestCase
from scinoephile.llms.review import ReviewQuery, ReviewTestCase
from scinoephile.llms.translation import TranslationQuery, TranslationTestCase


def test_delineation_no_op_leaves_boundary_unchanged():
    """Delineation no-op answers should request no boundary shift."""
    test_case = DelineationTestCase(
        query=DelineationQuery(
            reference_one="Reference one",
            reference_two="Reference two",
            target_one="Target one",
            target_two="Target two",
        )
    )

    output = DelineationTestCase(
        query=test_case.query, answer=test_case.get_no_op_answer()
    )

    assert output.answer is not None
    assert output.answer.output_one == ""
    assert output.answer.output_two == ""


def test_gap_translation_no_op_leaves_missing_outputs_empty():
    """Gap-translation no-op answers should retain blank target gaps."""
    test_case = GapTranslationTestCase(
        query=GapTranslationQuery(
            targets=[{"index": 1, "text": "Existing"}],
            guides=[
                {"index": 1, "text": "Guide one"},
                {"index": 2, "text": "Guide two"},
            ],
        )
    )

    output = GapTranslationTestCase(
        query=test_case.query, answer=test_case.get_no_op_answer()
    )

    assert output.answer is not None
    assert [(item.index, item.text) for item in output.answer.outputs] == [(2, "")]


def test_guided_review_no_op_has_no_revisions():
    """Guided-review no-op answers should contain no revisions."""
    test_case = GuidedReviewTestCase(
        query=GuidedReviewQuery(
            targets=[{"index": 1, "text": "Target"}],
            guides=[{"index": 1, "text": "Guide"}],
        )
    )

    output = GuidedReviewTestCase(
        query=test_case.query, answer=test_case.get_no_op_answer()
    )

    assert output.answer is not None
    assert output.answer.revisions == []


def test_guided_translation_no_op_copies_source_text():
    """Guided-translation no-op answers should copy source subtitles."""
    test_case = GuidedTranslationTestCase(
        query=GuidedTranslationQuery(
            subtitles=[{"index": 1, "text": "Source"}],
            guides=[{"index": 1, "text": "Guide"}],
        )
    )

    output = GuidedTranslationTestCase(
        query=test_case.query, answer=test_case.get_no_op_answer()
    )

    assert output.answer is not None
    assert [(item.index, item.text) for item in output.answer.outputs] == [
        (1, "Source")
    ]


def test_ocr_fusion_no_op_selects_first_source():
    """OCR-fusion no-op answers should select the first source."""
    test_case = OcrFusionTestCase(
        query=OcrFusionQuery(source_one="Lens", source_two="Tesseract")
    )

    output = OcrFusionTestCase(
        query=test_case.query, answer=test_case.get_no_op_answer()
    )

    assert output.answer is not None
    assert output.answer.output == "Lens"
    assert output.answer.note == "No-op."


def test_multi_review_no_op_selects_first_available_source():
    """Multi-review no-op answers should avoid synthesizing missing text."""
    test_case = MultiReviewTestCase(
        query=MultiReviewQuery(
            sources=[
                {"name": "one", "subtitles": [{"index": 1, "text": "Source one"}]},
                {"name": "two", "subtitles": [{"index": 2, "text": "Source two"}]},
            ],
            guides=[
                {"index": 1, "text": "Guide one"},
                {"index": 2, "text": "Guide two"},
                {"index": 3, "text": "Guide three"},
            ],
        )
    )

    output = MultiReviewTestCase(
        query=test_case.query, answer=test_case.get_no_op_answer()
    )

    assert output.answer is not None
    assert [(item.index, item.text) for item in output.answer.outputs] == [
        (1, "Source one"),
        (2, "Source two"),
        (3, ""),
    ]


def test_punctuation_no_op_concatenates_source_text():
    """Punctuation no-op answers should concatenate source text unchanged."""
    test_case = PunctuationTestCase(
        query=PunctuationQuery(guide="Guide.", subtitles=["Source", " text"])
    )

    output = PunctuationTestCase(
        query=test_case.query, answer=test_case.get_no_op_answer()
    )

    assert output.answer is not None
    assert output.answer.output == "Source text"


def test_review_no_op_has_no_revisions():
    """Review no-op answers should contain no revisions."""
    test_case = ReviewTestCase(
        query=ReviewQuery(subtitles=[{"index": 1, "text": "Subtitle"}])
    )

    output = ReviewTestCase(query=test_case.query, answer=test_case.get_no_op_answer())

    assert output.answer is not None
    assert output.answer.revisions == []


def test_translation_no_op_copies_source_text():
    """Translation no-op answers should copy source subtitles."""
    test_case = TranslationTestCase(
        query=TranslationQuery(subtitles=[{"index": 1, "text": "Source"}])
    )

    output = TranslationTestCase(
        query=test_case.query, answer=test_case.get_no_op_answer()
    )

    assert output.answer is not None
    assert [(item.index, item.text) for item in output.answer.outputs] == [
        (1, "Source")
    ]
