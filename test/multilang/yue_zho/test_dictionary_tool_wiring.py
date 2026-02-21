#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for CUHK dictionary tool wiring in 粤文/中文 workflows."""

from __future__ import annotations

from scinoephile.multilang.yue_zho.proofreading import get_yue_vs_zho_proofreader
from scinoephile.multilang.yue_zho.review import get_yue_vs_zho_processor
from scinoephile.multilang.yue_zho.translation import get_yue_from_zho_translator


def test_proofreading_uses_dictionary_tool_by_default():
    """Test proofreading processor enables dictionary tool by default."""
    processor = get_yue_vs_zho_proofreader(test_cases=[])

    assert len(processor.queryer.tools) == 1
    assert "lookup_cuhk_dictionary" in processor.queryer.tool_handlers


def test_translation_uses_dictionary_tool_by_default():
    """Test translation processor enables dictionary tool by default."""
    processor = get_yue_from_zho_translator(test_cases=[])

    assert len(processor.queryer.tools) == 1
    assert "lookup_cuhk_dictionary" in processor.queryer.tool_handlers


def test_review_uses_dictionary_tool_by_default():
    """Test review processor enables dictionary tool by default."""
    processor = get_yue_vs_zho_processor(test_cases=[])

    assert len(processor.queryer.tools) == 1
    assert "lookup_cuhk_dictionary" in processor.queryer.tool_handlers


def test_workflows_can_disable_dictionary_tool():
    """Test workflow constructors allow disabling dictionary tool wiring."""
    proofreader = get_yue_vs_zho_proofreader(test_cases=[], use_dictionary_tool=False)
    translator = get_yue_from_zho_translator(test_cases=[], use_dictionary_tool=False)
    reviewer = get_yue_vs_zho_processor(test_cases=[], use_dictionary_tool=False)

    assert proofreader.queryer.tools == []
    assert translator.queryer.tools == []
    assert reviewer.queryer.tools == []
