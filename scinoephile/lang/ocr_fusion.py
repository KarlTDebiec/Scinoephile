#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Monolingual OCR fusion helpers."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Unpack

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider, ProcessorKwargs, TestCase
from scinoephile.llms import load_default_test_cases
from scinoephile.llms.ocr_fusion import (
    OcrFusionManager,
    OcrFusionProcessor,
    OcrFusionPrompt,
)
from scinoephile.llms.providers.registry import get_provider

from .eng.ocr_fusion import OcrFusionPromptEng
from .yue.ocr_fusion import OcrFusionPromptYueHans, OcrFusionPromptYueHant
from .zho.ocr_fusion import OcrFusionPromptZhoHans, OcrFusionPromptZhoHant

__all__ = [
    "DEFAULT_PROMPTS",
    "get_ocr_fuser",
]

_ENG_OCR_FUSION_JSON_PATHS = (
    Path("kob/output/eng_ocr/lang/eng/ocr_fusion.json"),
    Path("mlamd/output/eng_ocr/lang/eng/ocr_fusion.json"),
    Path("mnt/output/eng_ocr/lang/eng/ocr_fusion.json"),
    Path("t/output/eng_ocr/lang/eng/ocr_fusion.json"),
)
"""Default English OCR fusion JSON paths."""

_YUE_HANS_OCR_FUSION_JSON_PATHS = (
    Path("acopopb/output/yue-Hans_ocr/lang/yue/ocr_fusion.json"),
    Path("acoptc/output/yue-Hans_ocr/lang/yue/ocr_fusion.json"),
    Path("tmm/output/yue-Hans_ocr/lang/yue/ocr_fusion.json"),
)
"""Default simplified written Cantonese OCR fusion JSON paths."""

_YUE_HANT_OCR_FUSION_JSON_PATHS = (
    Path("acopopb/output/yue-Hant_ocr/lang/yue/ocr_fusion.json"),
    Path("acoptc/output/yue-Hant_ocr/lang/yue/ocr_fusion.json"),
    Path("tmm/output/yue-Hant_ocr/lang/yue/ocr_fusion.json"),
)
"""Default traditional written Cantonese OCR fusion JSON paths."""

_ZHO_HANS_OCR_FUSION_JSON_PATHS = (
    Path("mlamd/output/zho-Hans_ocr/lang/zho/ocr_fusion.json"),
    Path("mnt/output/zho-Hans_ocr/lang/zho/ocr_fusion.json"),
    Path("t/output/zho-Hans_ocr/lang/zho/ocr_fusion.json"),
)
"""Default simplified standard Chinese OCR fusion JSON paths."""

_ZHO_HANT_OCR_FUSION_JSON_PATHS = (
    Path("kob/output/zho-Hant_ocr/lang/zho/ocr_fusion.json"),
    Path("mlamd/output/zho-Hant_ocr/lang/zho/ocr_fusion.json"),
    Path("mnt/output/zho-Hant_ocr/lang/zho/ocr_fusion.json"),
    Path("t/output/zho-Hant_ocr/lang/zho/ocr_fusion.json"),
)
"""Default traditional standard Chinese OCR fusion JSON paths."""

_JSON_PATHS: dict[Language, tuple[Path, ...]] = {
    Language.eng: _ENG_OCR_FUSION_JSON_PATHS,
    Language.yue_hans: _YUE_HANS_OCR_FUSION_JSON_PATHS,
    Language.yue_hant: _YUE_HANT_OCR_FUSION_JSON_PATHS,
    Language.zho_hans: _ZHO_HANS_OCR_FUSION_JSON_PATHS,
    Language.zho_hant: _ZHO_HANT_OCR_FUSION_JSON_PATHS,
}
"""OCR fusion JSON paths keyed by language."""

DEFAULT_PROMPTS: Mapping[Language, OcrFusionPrompt] = MappingProxyType(
    {
        Language.eng: OcrFusionPromptEng,
        Language.yue_hans: OcrFusionPromptYueHans,
        Language.yue_hant: OcrFusionPromptYueHant,
        Language.zho_hans: OcrFusionPromptZhoHans,
        Language.zho_hant: OcrFusionPromptZhoHant,
    }
)
"""OCR fusion prompts keyed by language."""


def get_ocr_fuser(
    language: Language,
    prompt: OcrFusionPrompt | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> OcrFusionProcessor:
    """Get an OCR fusion processor for a supported language.

    Arguments:
        language: subtitle language
        prompt: text for LLM correspondence
        test_cases: test cases
        provider: provider to use for queries
        **kwargs: additional keyword arguments for OcrFusionProcessor
    Returns:
        configured OCR fusion processor
    Raises:
        ScinoephileError: if OCR fusion does not support the language
    """
    if language not in DEFAULT_PROMPTS:
        raise ScinoephileError(f"OCR fusion does not support language {language.code}")

    if prompt is None:
        prompt = DEFAULT_PROMPTS[language]
    if test_cases is None:
        json_paths = _JSON_PATHS[language]
        test_cases = list(load_default_test_cases(OcrFusionManager, prompt, json_paths))
    if provider is None:
        provider = get_provider()
    return OcrFusionProcessor(prompt, test_cases, provider=provider, **kwargs)
