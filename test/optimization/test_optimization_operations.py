#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for optimization operation registration."""

from __future__ import annotations

from scinoephile.core.llms import TestCase
from scinoephile.llms.delineation import DelineationManager
from scinoephile.llms.gap_translation import GapTranslationManager
from scinoephile.llms.guided_review import GuidedReviewManager
from scinoephile.llms.guided_translation import GuidedTranslationManager
from scinoephile.llms.ocr_fusion import OcrFusionManager
from scinoephile.llms.punctuation import PunctuationManager
from scinoephile.llms.review import ReviewManager
from scinoephile.llms.translation import TranslationManager
from scinoephile.optimization.operations import OPERATIONS


def test_operations_are_keyed_by_stable_manager_identifiers():
    """Operation registry keys should match their manager identifiers."""
    assert OPERATIONS == {
        "delineation": DelineationManager,
        "gap-translation": GapTranslationManager,
        "guided-review": GuidedReviewManager,
        "guided-translation": GuidedTranslationManager,
        "ocr-fusion": OcrFusionManager,
        "punctuation": PunctuationManager,
        "review": ReviewManager,
        "translation": TranslationManager,
    }


def test_concrete_managers_declare_static_test_case_bases():
    """Every production manager should explicitly declare its semantic model."""
    for manager_cls in OPERATIONS.values():
        assert "test_case_base_cls" in manager_cls.__dict__
        assert manager_cls.test_case_base_cls is not TestCase
