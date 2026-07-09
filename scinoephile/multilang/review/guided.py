#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Guided review helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Unpack, cast

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.dictionaries import DictionaryToolPrompt
from scinoephile.core.llms import LLMProvider, OperationSpec, ProcessorKwargs, TestCase
from scinoephile.dictionaries.dictionary_tools import get_dictionary_tools
from scinoephile.llms import load_default_test_cases
from scinoephile.llms.guided_review import (
    GuidedReviewManager,
    GuidedReviewProcessor,
    GuidedReviewPrompt,
)
from scinoephile.llms.providers.registry import get_provider
from scinoephile.multilang.eng_yue.review import EngYueGuidedReviewPrompt
from scinoephile.multilang.eng_zho.review import EngZhoGuidedReviewPrompt
from scinoephile.multilang.yue_eng.review import (
    YueEngGuidedReviewPromptYueHans,
    YueEngGuidedReviewPromptYueHant,
)
from scinoephile.multilang.yue_zho.review import (
    YueZhoGuidedReviewPromptYueHans,
    YueZhoGuidedReviewPromptYueHant,
)
from scinoephile.multilang.zho_eng.review import (
    ZhoEngGuidedReviewPromptZhoHans,
    ZhoEngGuidedReviewPromptZhoHant,
)
from scinoephile.multilang.zho_yue.review import (
    ZhoYueGuidedReviewPromptZhoHans,
    ZhoYueGuidedReviewPromptZhoHant,
)

__all__ = [
    "GUIDED_REVIEW_OPERATION_SPEC",
    "get_guided_reviewer",
]

GUIDED_REVIEW_OPERATION_SPEC = OperationSpec(
    operation="guided-review",
    test_case_table_name="test_cases__guided_review",
    manager_cls=GuidedReviewManager,
    prompt_cls=GuidedReviewPrompt,
)
"""Operation specification for guided review."""

_YUE_ZHO_JSON_PATHS = (
    Path("mlamd/output/yue-Hans_transcribe/multilang/yue_zho/guided_review/cuda.json"),
    Path("mlamd/output/yue-Hans_transcribe/multilang/yue_zho/guided_review/cpu.json"),
    Path("mlamd/output/yue-Hans_transcribe/multilang/yue_zho/guided_review/mps.json"),
)
"""Default written Cantonese/Chinese guided-review JSON paths."""

_PROMPTS: dict[tuple[Language, Language], type[GuidedReviewPrompt]] = {
    (Language.eng, Language.yue_hans): EngYueGuidedReviewPrompt,
    (Language.eng, Language.yue_hant): EngYueGuidedReviewPrompt,
    (Language.eng, Language.zho_hans): EngZhoGuidedReviewPrompt,
    (Language.eng, Language.zho_hant): EngZhoGuidedReviewPrompt,
    (Language.yue_hans, Language.eng): YueEngGuidedReviewPromptYueHans,
    (Language.yue_hans, Language.zho_hans): YueZhoGuidedReviewPromptYueHans,
    (Language.yue_hans, Language.zho_hant): YueZhoGuidedReviewPromptYueHans,
    (Language.yue_hant, Language.eng): YueEngGuidedReviewPromptYueHant,
    (Language.yue_hant, Language.zho_hans): YueZhoGuidedReviewPromptYueHant,
    (Language.yue_hant, Language.zho_hant): YueZhoGuidedReviewPromptYueHant,
    (Language.zho_hans, Language.eng): ZhoEngGuidedReviewPromptZhoHans,
    (Language.zho_hans, Language.yue_hans): ZhoYueGuidedReviewPromptZhoHans,
    (Language.zho_hans, Language.yue_hant): ZhoYueGuidedReviewPromptZhoHans,
    (Language.zho_hant, Language.eng): ZhoEngGuidedReviewPromptZhoHant,
    (Language.zho_hant, Language.yue_hans): ZhoYueGuidedReviewPromptZhoHant,
    (Language.zho_hant, Language.yue_hant): ZhoYueGuidedReviewPromptZhoHant,
}
"""Guided review prompts keyed by reviewed and guide languages."""

_JSON_PATHS: dict[tuple[Language, Language], tuple[Path, ...]] = {
    key: (
        _YUE_ZHO_JSON_PATHS
        if key[0] in (Language.yue_hans, Language.yue_hant)
        and key[1] in (Language.zho_hans, Language.zho_hant)
        else ()
    )
    for key in _PROMPTS
}
"""Guided review JSON paths keyed by reviewed and guide languages."""


def get_guided_reviewer(
    language: Language,
    guide_language: Language,
    prompt_cls: type[GuidedReviewPrompt] | None = None,
    test_cases: list[TestCase] | None = None,
    use_dictionary_tool: bool = True,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> GuidedReviewProcessor:
    """Get a guided reviewer for a supported language pair.

    Arguments:
        language: language of subtitles to review
        guide_language: language of guide subtitles
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        use_dictionary_tool: whether to wire the dictionary lookup tool
        provider: provider to use for queries
        **kwargs: additional processor keyword arguments
    Returns:
        configured guided review processor
    Raises:
        ScinoephileError: if guided review does not support the language pair
    """
    key = (language, guide_language)
    if key not in _PROMPTS:
        raise ScinoephileError(
            "Guided review does not support language pair "
            f"{language.tag} <- {guide_language.tag}"
        )
    if prompt_cls is None:
        prompt_cls = _PROMPTS[key]
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(
                GuidedReviewManager,
                prompt_cls,
                _JSON_PATHS[key],
            )
        )
    tool_box = kwargs.pop("tool_box", None)
    if tool_box is None and use_dictionary_tool:
        dictionary_prompt_cls = cast(type[DictionaryToolPrompt], prompt_cls)
        tool_box = get_dictionary_tools(dictionary_prompt_cls)
    if provider is None:
        provider = get_provider()
    kwargs["tool_box"] = tool_box
    return GuidedReviewProcessor(
        prompt_cls,
        test_cases,
        provider=provider,
        **kwargs,
    )
