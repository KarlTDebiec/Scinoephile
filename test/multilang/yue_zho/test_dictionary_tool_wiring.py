#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of dictionary tool wiring for 粤文/中文 workflows."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from scinoephile.core.llms import Processor
from scinoephile.multilang.cmn_yue.dictionary_tools import LOOKUP_TOOL_NAME
from scinoephile.multilang.yue_zho.proofreading import (
    YueZhoHansProofreadingPrompt,
    get_yue_vs_zho_proofreader,
)
from scinoephile.multilang.yue_zho.review import (
    YueHansReviewPrompt,
    get_yue_vs_zho_processor,
)
from scinoephile.multilang.yue_zho.translation import (
    YueHansFromZhoTranslationPrompt,
    get_yue_from_zho_translator,
)


@pytest.mark.parametrize(
    ("factory", "prompt_cls"),
    [
        (get_yue_from_zho_translator, YueHansFromZhoTranslationPrompt),
        (get_yue_vs_zho_processor, YueHansReviewPrompt),
        (get_yue_vs_zho_proofreader, YueZhoHansProofreadingPrompt),
    ],
)
def test_dictionary_tool_wiring_uses_generic_lookup_tool(
    factory: Callable[..., Processor],
    prompt_cls: type[Any],
):
    """Test processors wire the generic dictionary lookup tool and prompt text."""
    processor = factory(
        prompt_cls=prompt_cls,
        test_cases=[],
        use_dictionary_tool=True,
    )

    assert [tool["name"] for tool in processor.queryer.tools] == [LOOKUP_TOOL_NAME]
    assert sorted(processor.queryer.tool_handlers) == [LOOKUP_TOOL_NAME]
    assert LOOKUP_TOOL_NAME in prompt_cls.base_system_prompt
