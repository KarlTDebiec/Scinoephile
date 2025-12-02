#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English proofreading."""

from __future__ import annotations

from typing import Any

from scinoephile.core.english.proofreading.english_proofreader import EnglishProofreader
from scinoephile.core.english.proofreading.english_proofreading_answer import (
    EnglishProofreadingAnswer,
)
from scinoephile.core.english.proofreading.english_proofreading_llm_queryer import (
    EnglishProofreadingLLMQueryer,
)
from scinoephile.core.english.proofreading.english_proofreading_llm_text import (
    EnglishProofreadingLLMText,
)
from scinoephile.core.english.proofreading.english_proofreading_query import (
    EnglishProofreadingQuery,
)
from scinoephile.core.english.proofreading.english_proofreading_test_case import (
    EnglishProofreadingTestCase,
)
from scinoephile.core.series import Series


def get_english_proofread(
    series: Series, proofreader: EnglishProofreader | None = None, **kwargs: Any
) -> Series:
    """Get English series proofread.

    Arguments:
        series: Series to proofread
        proofreader: EnglishProofreader to use
        kwargs: additional keyword arguments for EnglishProofreader.proofread
    Returns:
        proofread Series
    """
    if proofreader is None:
        proofreader = EnglishProofreader()

    proofread = proofreader.proofread(series, **kwargs)

    return proofread


__all__ = [
    "EnglishProofreader",
    "EnglishProofreadingAnswer",
    "EnglishProofreadingLLMQueryer",
    "EnglishProofreadingLLMText",
    "EnglishProofreadingQuery",
    "EnglishProofreadingTestCase",
    "get_english_proofread",
]
