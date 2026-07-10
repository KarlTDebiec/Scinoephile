#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for language-agnostic transcription operation specifications."""

from __future__ import annotations

from scinoephile.llms.delineation import DelineationManager, DelineationPrompt
from scinoephile.llms.punctuation import PunctuationManager, PunctuationPrompt
from scinoephile.multilang.transcription.delineation import (
    DELINEATION_OPERATION_SPEC,
)
from scinoephile.multilang.transcription.punctuation import (
    PUNCTUATION_OPERATION_SPEC,
)
from scinoephile.optimization.operations import OPERATIONS


def test_delineation_operation_spec_is_language_agnostic():
    """Delineation operation metadata should not name a language pair."""
    assert DELINEATION_OPERATION_SPEC.operation == "delineation"
    assert DELINEATION_OPERATION_SPEC.test_case_table_name == "test_cases__delineation"
    assert DELINEATION_OPERATION_SPEC.manager_cls is DelineationManager
    assert DELINEATION_OPERATION_SPEC.prompt_cls is DelineationPrompt
    assert OPERATIONS["delineation"] is DELINEATION_OPERATION_SPEC


def test_punctuation_operation_spec_is_language_agnostic():
    """Punctuation operation metadata should not name a language pair."""
    assert PUNCTUATION_OPERATION_SPEC.operation == "punctuation"
    assert PUNCTUATION_OPERATION_SPEC.test_case_table_name == "test_cases__punctuation"
    assert PUNCTUATION_OPERATION_SPEC.manager_cls is PunctuationManager
    assert PUNCTUATION_OPERATION_SPEC.prompt_cls is PunctuationPrompt
    assert PUNCTUATION_OPERATION_SPEC.list_fields == {"query.one": 10}
    assert OPERATIONS["punctuation"] is PUNCTUATION_OPERATION_SPEC
