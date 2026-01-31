#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 中文 OCR fusion."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.subtitles import Series
from scinoephile.llms.base import TestCase
from scinoephile.llms.dual_single.ocr_fusion import (
    OcrFusionProcessor,
    OcrFusionPrompt,
)

from .prompts import ZhoHansOcrFusionPrompt, ZhoHantOcrFusionPrompt

__all__ = [
    "ZhoHansOcrFusionPrompt",
    "ZhoHantOcrFusionPrompt",
    "ZhoOcrFusionProcessKwargs",
    "ZhoOcrFusionProcessorKwargs",
    "get_default_zho_ocr_fusion_test_cases",
    "get_zho_ocr_fuser",
    "get_zho_ocr_fused",
]


logger = getLogger(__name__)


class ZhoOcrFusionProcessKwargs(TypedDict, total=False):
    """Keyword arguments for OcrFusionProcessor.process."""

    stop_at_idx: int | None


class ZhoOcrFusionProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for OcrFusionProcessor initialization."""

    test_case_path: Path | None
    auto_verify: bool


# noinspection PyUnusedImports
def get_default_zho_ocr_fusion_test_cases(
    prompt_cls: type[OcrFusionPrompt] = ZhoHansOcrFusionPrompt,
) -> list[TestCase]:
    """Get default 中文 OCR fusion test cases included with package.

    Arguments:
        prompt_cls: text for LLM correspondence
    Returns:
        default test cases
    """
    try:
        from test.data.kob import (  # noqa: PLC0415
            get_kob_zho_hant_ocr_fusion_test_cases,
        )
        from test.data.mlamd import (  # noqa: PLC0415
            get_mlamd_zho_hans_ocr_fusion_test_cases,
            get_mlamd_zho_hant_ocr_fusion_test_cases,
        )
        from test.data.mnt import (  # noqa: PLC0415
            get_mnt_zho_hans_ocr_fusion_test_cases,
            get_mnt_zho_hant_ocr_fusion_test_cases,
        )
        from test.data.t import (  # noqa: PLC0415
            get_t_zho_hans_ocr_fusion_test_cases,
            get_t_zho_hant_ocr_fusion_test_cases,
        )

        if prompt_cls is ZhoHantOcrFusionPrompt:
            return (
                get_kob_zho_hant_ocr_fusion_test_cases(prompt_cls)
                + get_mlamd_zho_hant_ocr_fusion_test_cases(prompt_cls)
                + get_mnt_zho_hant_ocr_fusion_test_cases(prompt_cls)
                + get_t_zho_hant_ocr_fusion_test_cases(prompt_cls)
            )

        return (
            get_mlamd_zho_hans_ocr_fusion_test_cases(prompt_cls)
            + get_mnt_zho_hans_ocr_fusion_test_cases(prompt_cls)
            + get_t_zho_hans_ocr_fusion_test_cases(prompt_cls)
        )
    except ImportError as exc:
        logger.warning(f"Default test cases not available:\n{exc}")
    return []


def get_zho_ocr_fused(
    lens: Series,
    paddle: Series,
    processor: OcrFusionProcessor | None = None,
    **kwargs: Unpack[ZhoOcrFusionProcessKwargs],
) -> Series:
    """Get 中文 series fused from Google Lens and PaddleOCR outputs.

    Arguments:
        lens: subtitles OCRed using Google Lens
        paddle: subtitles OCRed using PaddleOCR
        processor: OcrFusionProcessor to use
        **kwargs: additional keyword arguments for OcrFusionProcessor.process
    Returns:
        Fused series
    """
    if processor is None:
        processor = get_zho_ocr_fuser()
    return processor.process(lens, paddle, **kwargs)


def get_zho_ocr_fuser(
    prompt_cls: type[ZhoHansOcrFusionPrompt] = ZhoHansOcrFusionPrompt,
    test_cases: list[TestCase] | None = None,
    **kwargs: Unpack[ZhoOcrFusionProcessorKwargs],
) -> OcrFusionProcessor:
    """Get an OcrFusionProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        **kwargs: additional keyword arguments for OcrFusionProcessor
    Returns:
        OcrFusionProcessor with provided configuration
    """
    if test_cases is None:
        test_cases = get_default_zho_ocr_fusion_test_cases(prompt_cls)
    return OcrFusionProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        **kwargs,
    )
