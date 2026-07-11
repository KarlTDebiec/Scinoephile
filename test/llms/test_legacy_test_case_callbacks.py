#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for legacy manager-defined test-case callbacks."""

from __future__ import annotations

from pydantic import ValidationError
from pytest import raises

from scinoephile.llms.delineation import DelineationManager
from scinoephile.llms.ocr_fusion import OcrFusionManager
from scinoephile.llms.pairwise_review import PairwiseReviewManager
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YuePunctuationVsZhoPromptYueHans,
    YueZhoPunctuationManager,
)


def test_pairwise_review_retains_validation_and_minimum_difficulty():
    """Pairwise review should normalize unchanged output and score revisions."""
    test_case_cls = PairwiseReviewManager.get_test_case_cls(
        PairwiseReviewManager.base_prompt
    )
    unchanged = test_case_cls.model_validate(
        {
            "query": {"target": "original", "reference": "reference"},
            "answer": {"output": "original", "note": "legacy"},
        }
    )
    revised = test_case_cls.model_validate(
        {
            "query": {"target": "original", "reference": "reference"},
            "answer": {"output": "corrected", "note": "typo"},
        }
    )

    assert unchanged.answer is not None
    assert unchanged.answer.model_dump() == {"output": "", "note": ""}
    assert unchanged.difficulty == 0
    assert revised.difficulty == 1
    with raises(ValidationError, match="no note is provided"):
        test_case_cls.model_validate(
            {
                "query": {"target": "original", "reference": "reference"},
                "answer": {"output": "corrected", "note": ""},
            }
        )


def test_ocr_fusion_retains_auto_verification_and_minimum_difficulty():
    """OCR fusion should retain its legacy difficulty and verification rules."""
    test_case_cls = OcrFusionManager.get_test_case_cls(OcrFusionManager.base_prompt)
    simple = test_case_cls.model_validate(
        {
            "query": {"one": "source one", "two": "source two"},
            "answer": {"output": "source one", "note": "selected source one"},
        }
    )
    complex_case = test_case_cls.model_validate(
        {
            "query": {"one": "source-one", "two": "source two"},
            "answer": {"output": "source-one", "note": "selected source one"},
        }
    )

    assert simple.difficulty == 1
    assert simple.get_auto_verified()
    assert complex_case.difficulty == 2
    assert not complex_case.get_auto_verified()


def test_punctuation_retains_validation_and_minimum_difficulty():
    """Localized punctuation should retain its manager-defined test-case rules."""
    prompt = YuePunctuationVsZhoPromptYueHans
    test_case_cls = YueZhoPunctuationManager.get_test_case_cls(prompt)
    test_case = test_case_cls.model_validate(
        {
            "query": {prompt.src_1: ["你好"], prompt.src_2: "你好"},
            "answer": {prompt.output: "你，好"},
        }
    )

    assert test_case.difficulty == 2
    with raises(ValidationError, match="does not match"):
        test_case_cls.model_validate(
            {
                "query": {prompt.src_1: ["你好"], prompt.src_2: "你好"},
                "answer": {prompt.output: "你壞"},
            }
        )


def test_delineation_retains_validation_and_minimum_difficulty():
    """Delineation should retain shifted-boundary validation and scoring."""
    test_case_cls = DelineationManager.get_test_case_cls(DelineationManager.base_prompt)
    query = {
        "src_1_sub_1": "source one first",
        "src_1_sub_2": "source one second",
        "src_2_sub_1": "ab",
        "src_2_sub_2": "cd",
    }
    shifted = test_case_cls.model_validate(
        {
            "query": query,
            "answer": {
                "src_2_sub_1_shifted": "abc",
                "src_2_sub_2_shifted": "d",
            },
        }
    )

    assert shifted.difficulty == 1
    with raises(ValidationError, match="are equal to query"):
        test_case_cls.model_validate(
            {
                "query": query,
                "answer": {
                    "src_2_sub_1_shifted": "ab",
                    "src_2_sub_2_shifted": "cd",
                },
            }
        )
