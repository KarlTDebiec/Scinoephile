#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Monolingual review helpers."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Unpack

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider, ProcessorKwargs, TestCase
from scinoephile.llms import load_default_test_cases
from scinoephile.llms.providers.registry import get_provider
from scinoephile.llms.review import ReviewManager, ReviewProcessor, ReviewPrompt

from .eng.review import ReviewPromptEng
from .yue.review import ReviewPromptYueHans, ReviewPromptYueHant
from .zho.review import ReviewPromptZhoHans, ReviewPromptZhoHant

__all__ = [
    "DEFAULT_PROMPTS",
    "get_reviewer",
]

_ENG_REVIEW_JSON_PATHS = (
    Path("kob/output/eng_ocr/lang/eng/review.json"),
    Path("kob/output/eng/lang/eng/review.json"),
    Path("mlamd/output/eng_ocr/lang/eng/review.json"),
    Path("mnt/output/eng_ocr/lang/eng/review.json"),
    Path("t/output/eng_ocr/lang/eng/review.json"),
)
"""Default English review JSON paths."""

_YUE_HANS_REVIEW_JSON_PATHS = (
    Path("acopopb/output/yue-Hans_ocr/lang/yue/review.json"),
    Path("acoptc/output/yue-Hans_ocr/lang/yue/review.json"),
    Path("kob/output/yue-Hans/lang/yue/review.json"),
    Path("tmm/output/yue-Hans_ocr/lang/yue/review.json"),
)
"""Default simplified written Cantonese review JSON paths."""

_YUE_HANT_REVIEW_JSON_PATHS = (
    Path("acopopb/output/yue-Hant_ocr/lang/yue/review.json"),
    Path("acoptc/output/yue-Hant_ocr/lang/yue/review.json"),
    Path("kob/output/yue-Hant/lang/yue/review.json"),
    Path("tmm/output/yue-Hant_ocr/lang/yue/review.json"),
)
"""Default traditional written Cantonese review JSON paths."""

_ZHO_HANS_REVIEW_JSON_PATHS = (
    Path("mlamd/output/zho-Hans_ocr/lang/zho/review.json"),
    Path("mnt/output/zho-Hans_ocr/lang/zho/review.json"),
    Path("t/output/zho-Hans_ocr/lang/zho/review.json"),
)
"""Default simplified standard Chinese review JSON paths."""

_ZHO_HANT_REVIEW_JSON_PATHS = (
    Path("kob/output/zho-Hant_ocr/lang/zho/review.json"),
    Path("mlamd/output/zho-Hant_ocr/lang/zho/review.json"),
    Path("mnt/output/zho-Hant_ocr/lang/zho/review.json"),
    Path("t/output/zho-Hant_ocr/lang/zho/review.json"),
)
"""Default traditional standard Chinese review JSON paths."""

_JSON_PATHS: dict[Language, tuple[Path, ...]] = {
    Language.eng: _ENG_REVIEW_JSON_PATHS,
    Language.yue_hans: _YUE_HANS_REVIEW_JSON_PATHS,
    Language.yue_hant: _YUE_HANT_REVIEW_JSON_PATHS,
    Language.zho_hans: _ZHO_HANS_REVIEW_JSON_PATHS,
    Language.zho_hant: _ZHO_HANT_REVIEW_JSON_PATHS,
}
"""Review JSON paths keyed by language."""

DEFAULT_PROMPTS: Mapping[Language, ReviewPrompt] = MappingProxyType(
    {
        Language.eng: ReviewPromptEng,
        Language.yue_hans: ReviewPromptYueHans,
        Language.yue_hant: ReviewPromptYueHant,
        Language.zho_hans: ReviewPromptZhoHans,
        Language.zho_hant: ReviewPromptZhoHant,
    }
)
"""Review prompts keyed by language."""


def get_reviewer(
    language: Language,
    prompt: ReviewPrompt | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> ReviewProcessor:
    """Get a review processor for a supported language.

    Arguments:
        language: subtitle language
        prompt: text for LLM correspondence
        test_cases: test cases
        provider: provider to use for queries
        **kwargs: additional keyword arguments for ReviewProcessor
    Returns:
        configured review processor
    Raises:
        ScinoephileError: if review does not support the language
    """
    if language not in DEFAULT_PROMPTS:
        raise ScinoephileError(f"Review does not support language {language.tag}")

    if prompt is None:
        prompt = DEFAULT_PROMPTS[language]
    if test_cases is None:
        json_paths = _JSON_PATHS[language]
        test_cases = list(load_default_test_cases(ReviewManager, prompt, json_paths))
    if provider is None:
        provider = get_provider()
    return ReviewProcessor(prompt, test_cases, provider=provider, **kwargs)
