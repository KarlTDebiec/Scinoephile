#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Monolingual block review helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Unpack

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider, OperationSpec, ProcessorKwargs, TestCase
from scinoephile.lang.eng.block_review import BlockReviewPromptEng
from scinoephile.lang.yue.block_review import (
    BlockReviewPromptYueHans,
    BlockReviewPromptYueHant,
)
from scinoephile.lang.zho.block_review import (
    BlockReviewPromptZhoHans,
    BlockReviewPromptZhoHant,
)
from scinoephile.llms import load_default_test_cases
from scinoephile.llms.block_review import (
    BlockReviewManager,
    BlockReviewProcessor,
    BlockReviewPrompt,
)
from scinoephile.llms.providers.registry import get_provider

__all__ = [
    "BLOCK_REVIEW_OPERATION_SPEC",
    "get_block_reviewer",
]

_ENG_BLOCK_REVIEW_JSON_PATHS = (
    Path("kob/output/eng_ocr/lang/eng/block_review.json"),
    Path("kob/output/eng/lang/eng/block_review.json"),
    Path("mlamd/output/eng_ocr/lang/eng/block_review.json"),
    Path("mnt/output/eng_ocr/lang/eng/block_review.json"),
    Path("t/output/eng_ocr/lang/eng/block_review.json"),
)
"""Default English block review JSON paths."""

_YUE_HANS_BLOCK_REVIEW_JSON_PATHS = (
    Path("acopopb/output/yue-Hans_ocr/lang/yue/block_review.json"),
    Path("acoptc/output/yue-Hans_ocr/lang/yue/block_review.json"),
    Path("kob/output/yue-Hans/lang/yue/block_review.json"),
    Path("tmm/output/yue-Hans_ocr/lang/yue/block_review.json"),
)
"""Default simplified written Cantonese block review JSON paths."""

_YUE_HANT_BLOCK_REVIEW_JSON_PATHS = (
    Path("acopopb/output/yue-Hant_ocr/lang/yue/block_review.json"),
    Path("acoptc/output/yue-Hant_ocr/lang/yue/block_review.json"),
    Path("kob/output/yue-Hant/lang/yue/block_review.json"),
    Path("tmm/output/yue-Hant_ocr/lang/yue/block_review.json"),
)
"""Default traditional written Cantonese block review JSON paths."""

_ZHO_HANS_BLOCK_REVIEW_JSON_PATHS = (
    Path("mlamd/output/zho-Hans_ocr/lang/zho/block_review.json"),
    Path("mnt/output/zho-Hans_ocr/lang/zho/block_review.json"),
    Path("t/output/zho-Hans_ocr/lang/zho/block_review.json"),
)
"""Default simplified standard Chinese block review JSON paths."""

_ZHO_HANT_BLOCK_REVIEW_JSON_PATHS = (
    Path("kob/output/zho-Hant_ocr/lang/zho/block_review.json"),
    Path("mlamd/output/zho-Hant_ocr/lang/zho/block_review.json"),
    Path("mnt/output/zho-Hant_ocr/lang/zho/block_review.json"),
    Path("t/output/zho-Hant_ocr/lang/zho/block_review.json"),
)
"""Default traditional standard Chinese block review JSON paths."""

BLOCK_REVIEW_OPERATION_SPEC = OperationSpec(
    operation="block-review",
    test_case_table_name="test_cases__block_review",
    manager_cls=BlockReviewManager,
    prompt_cls=BlockReviewPrompt,
)
"""Operation specification for monolingual block review."""

_JSON_PATHS: dict[Language, tuple[Path, ...]] = {
    Language.eng: _ENG_BLOCK_REVIEW_JSON_PATHS,
    Language.yue_hans: _YUE_HANS_BLOCK_REVIEW_JSON_PATHS,
    Language.yue_hant: _YUE_HANT_BLOCK_REVIEW_JSON_PATHS,
    Language.zho_hans: _ZHO_HANS_BLOCK_REVIEW_JSON_PATHS,
    Language.zho_hant: _ZHO_HANT_BLOCK_REVIEW_JSON_PATHS,
}
"""Block review JSON paths keyed by language."""

_PROMPTS: dict[Language, type[BlockReviewPrompt]] = {
    Language.eng: BlockReviewPromptEng,
    Language.yue_hans: BlockReviewPromptYueHans,
    Language.yue_hant: BlockReviewPromptYueHant,
    Language.zho_hans: BlockReviewPromptZhoHans,
    Language.zho_hant: BlockReviewPromptZhoHant,
}
"""Block review prompts keyed by language."""


def get_block_reviewer(
    language: Language,
    prompt_cls: type[BlockReviewPrompt] | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> BlockReviewProcessor:
    """Get a block review processor for a supported language.

    Arguments:
        language: subtitle language
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        provider: provider to use for queries
        **kwargs: additional keyword arguments for BlockReviewProcessor
    Returns:
        configured block review processor
    Raises:
        ScinoephileError: if block review does not support the language
    """
    if language not in _PROMPTS:
        raise ScinoephileError(f"Block review does not support language {language.tag}")

    if prompt_cls is None:
        prompt_cls = _PROMPTS[language]
    if test_cases is None:
        json_paths = _JSON_PATHS[language]
        test_cases = list(
            load_default_test_cases(BlockReviewManager, prompt_cls, json_paths)
        )
    if provider is None:
        provider = get_provider()
    return BlockReviewProcessor(prompt_cls, test_cases, provider=provider, **kwargs)
