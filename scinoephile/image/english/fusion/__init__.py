#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English OCR fusion."""

from __future__ import annotations

from typing import Any

from scinoephile.core import Series

from .answer import EnglishFusionAnswer
from .answer2 import EnglishFusionAnswer2
from .fuser import EnglishFuser
from .fuser2 import EnglishFuser2
from .prompt import EnglishFusionPrompt
from .prompt2 import EnglishFusionPrompt2
from .query import EnglishFusionQuery
from .query2 import EnglishFusionQuery2
from .queryer import EnglishFusionLLMQueryer
from .test_case import EnglishFusionTestCase
from .test_case2 import EnglishFusionTestCase2

__all__ = [
    "EnglishFuser",
    "EnglishFuser2",
    "EnglishFusionAnswer",
    "EnglishFusionAnswer2",
    "EnglishFusionLLMQueryer",
    "EnglishFusionPrompt",
    "EnglishFusionPrompt2",
    "EnglishFusionQuery",
    "EnglishFusionQuery2",
    "EnglishFusionTestCase",
    "EnglishFusionTestCase2",
    "get_english_ocr_fused",
    "get_english_ocr_fused2",
]


def get_english_ocr_fused(
    lens: Series,
    tesseract: Series,
    fuser: EnglishFuser | None = None,
    **kwargs: Any,
) -> Series:
    """Get OCRed English series fused from Google Lens and Tesseract outputs.

    Arguments:
        lens: subtitles OCRed using Google Lens
        tesseract: subtitles OCRed using Tesseract
        fuser: EnglishFuser to use
        kwargs: additional keyword arguments for EnglishFuser.fuse
    Returns:
        Fused series
    """
    if fuser is None:
        fuser = EnglishFuser()
    fused = fuser.fuse(lens, tesseract, **kwargs)
    return fused


def get_english_ocr_fused2(
    lens: Series,
    tesseract: Series,
    fuser: EnglishFuser2 | None = None,
    **kwargs: Any,
) -> Series:
    """Get OCRed English series fused from Google Lens and Tesseract outputs.

    Arguments:
        lens: subtitles OCRed using Google Lens
        tesseract: subtitles OCRed using Tesseract
        fuser: EnglishFuser to use
        kwargs: additional keyword arguments for EnglishFuser.fuse
    Returns:
        Fused series
    """
    if fuser is None:
        fuser = EnglishFuser2()
    fused = fuser.fuse(lens, tesseract, **kwargs)
    return fused


def migrate_english_ocr_fusion_v1_to_v2(
    test_cases: list[EnglishFusionTestCase],
) -> list[EnglishFusionTestCase2]:
    """Migrate English OCR fusion from v1 to v2.

    Arguments:
        test_cases: list of EnglishFusionTestCase to migrate
    Returns:
        list of EnglishFusionTestCase2
    """
    test_case_2_cls = EnglishFusionTestCase2.get_test_case_cls()
    query_2_cls = test_case_2_cls.query_cls
    answer_2_cls = test_case_2_cls.answer_cls

    test_case_2s: list[EnglishFusionTestCase2] = []
    for test_case in test_cases:
        query_2 = query_2_cls(lens=test_case.lens, tesseract=test_case.tesseract)
        answer_2 = answer_2_cls(fused=test_case.fused, note=test_case.note)
        test_case_2 = test_case_2_cls(
            query=query_2,
            answer=answer_2,
            difficulty=test_case.difficulty,
            prompt=test_case.prompt,
            verified=test_case.verified,
        )
        test_case_2s.append(test_case_2)

    return test_case_2s
