#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English proofreading."""

from __future__ import annotations

from typing import Any

from scinoephile.core.series import Series

from .answer import EnglishProofreadingAnswer
from .llm_queryer import EnglishProofreadingLLMQueryer
from .llm_text import EnglishProofreadingLLMText
from .proofreader import EnglishProofreader
from .query import EnglishProofreadingQuery
from .test_case import EnglishProofreadingTestCase


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
