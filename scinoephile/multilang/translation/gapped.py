#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Gapped translation helpers."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core import Language
from scinoephile.core.llms import (
    LLMProvider,
    OperationSpec,
    ProcessorKwargs,
    TestCase,
)
from scinoephile.core.subtitles import Series
from scinoephile.llms import load_default_test_cases
from scinoephile.llms.dual_n_minus_m_to_n import (
    DualNMinusMToNManager,
    DualNMinusMToNProcessor,
    DualNMinusMToNPrompt,
)
from scinoephile.llms.providers.registry import get_provider
from scinoephile.multilang.eng_yue.translation import EngYueGappedTranslationPrompt
from scinoephile.multilang.eng_zho.translation import EngZhoGappedTranslationPrompt
from scinoephile.multilang.yue_eng.translation import (
    YueEngGappedTranslationPromptYueHans,
    YueEngGappedTranslationPromptYueHant,
)
from scinoephile.multilang.yue_zho.translation import (
    YueZhoGappedTranslationPromptYueHans,
    YueZhoGappedTranslationPromptYueHant,
)
from scinoephile.multilang.zho_eng.translation import (
    ZhoEngGappedTranslationPromptZhoHans,
    ZhoEngGappedTranslationPromptZhoHant,
)
from scinoephile.multilang.zho_yue.translation import (
    ZhoYueGappedTranslationPromptZhoHans,
    ZhoYueGappedTranslationPromptZhoHant,
)

from .shared import DualNMinusMToNTranslationProcessorKwargs

__all__ = [
    "GAPPED_TRANSLATION_OPERATION_SPEC",
    "GappedTranslationProcessKwargs",
    "GappedTranslationProcessorKwargs",
    "get_gap_translated",
    "get_gap_translator",
]

GAPPED_TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="gapped-translation",
    test_case_table_name="test_cases__gapped_translation",
    manager_cls=DualNMinusMToNManager,
    prompt_cls=DualNMinusMToNPrompt,
)
"""Operation specification for gapped translation."""

_ENG_YUE_GAPPED_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
_ENG_ZHO_GAPPED_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
_YUE_ENG_GAPPED_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
_YUE_ZHO_GAPPED_TRANSLATION_JSON_PATHS = (
    Path(
        "mlamd/output/yue-Hans_transcribe/multilang/yue_zho/gap_translation/cuda.json"
    ),
    Path("mlamd/output/yue-Hans_transcribe/multilang/yue_zho/gap_translation/cpu.json"),
    Path("mlamd/output/yue-Hans_transcribe/multilang/yue_zho/gap_translation/mps.json"),
)
_ZHO_ENG_GAPPED_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()
_ZHO_YUE_GAPPED_TRANSLATION_JSON_PATHS: tuple[Path, ...] = ()

_JSON_PATHS: dict[tuple[Language, Language], tuple[Path, ...]] = {
    (Language.yue_hans, Language.eng): _ENG_YUE_GAPPED_TRANSLATION_JSON_PATHS,
    (Language.yue_hant, Language.eng): _ENG_YUE_GAPPED_TRANSLATION_JSON_PATHS,
    (Language.zho_hans, Language.eng): _ENG_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
    (Language.zho_hant, Language.eng): _ENG_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.yue_hans): _YUE_ENG_GAPPED_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.yue_hant): _YUE_ENG_GAPPED_TRANSLATION_JSON_PATHS,
    (Language.zho_hans, Language.yue_hans): _YUE_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
    (Language.zho_hant, Language.yue_hans): _YUE_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
    (Language.zho_hans, Language.yue_hant): _YUE_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
    (Language.zho_hant, Language.yue_hant): _YUE_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.zho_hans): _ZHO_ENG_GAPPED_TRANSLATION_JSON_PATHS,
    (Language.eng, Language.zho_hant): _ZHO_ENG_GAPPED_TRANSLATION_JSON_PATHS,
    (Language.yue_hans, Language.zho_hans): _ZHO_YUE_GAPPED_TRANSLATION_JSON_PATHS,
    (Language.yue_hant, Language.zho_hans): _ZHO_YUE_GAPPED_TRANSLATION_JSON_PATHS,
    (Language.yue_hans, Language.zho_hant): _ZHO_YUE_GAPPED_TRANSLATION_JSON_PATHS,
    (Language.yue_hant, Language.zho_hant): _ZHO_YUE_GAPPED_TRANSLATION_JSON_PATHS,
}
"""Gapped translation JSON paths keyed by exact source and target languages."""

_PROMPTS: dict[tuple[Language, Language], type[DualNMinusMToNPrompt]] = {
    (Language.yue_hans, Language.eng): EngYueGappedTranslationPrompt,
    (Language.yue_hant, Language.eng): EngYueGappedTranslationPrompt,
    (Language.zho_hans, Language.eng): EngZhoGappedTranslationPrompt,
    (Language.zho_hant, Language.eng): EngZhoGappedTranslationPrompt,
    (Language.eng, Language.yue_hans): YueEngGappedTranslationPromptYueHans,
    (Language.eng, Language.yue_hant): YueEngGappedTranslationPromptYueHant,
    (Language.zho_hans, Language.yue_hans): YueZhoGappedTranslationPromptYueHans,
    (Language.zho_hant, Language.yue_hans): YueZhoGappedTranslationPromptYueHans,
    (Language.zho_hans, Language.yue_hant): YueZhoGappedTranslationPromptYueHant,
    (Language.zho_hant, Language.yue_hant): YueZhoGappedTranslationPromptYueHant,
    (Language.eng, Language.zho_hans): ZhoEngGappedTranslationPromptZhoHans,
    (Language.eng, Language.zho_hant): ZhoEngGappedTranslationPromptZhoHant,
    (Language.yue_hans, Language.zho_hans): ZhoYueGappedTranslationPromptZhoHans,
    (Language.yue_hant, Language.zho_hans): ZhoYueGappedTranslationPromptZhoHans,
    (Language.yue_hans, Language.zho_hant): ZhoYueGappedTranslationPromptZhoHant,
    (Language.yue_hant, Language.zho_hant): ZhoYueGappedTranslationPromptZhoHant,
}
"""Gapped translation prompts keyed by exact source and target languages."""


class GappedTranslationProcessorKwargs(
    DualNMinusMToNTranslationProcessorKwargs,
    total=False,
):
    """Keyword arguments for gapped translation processor initialization."""


class GappedTranslationProcessKwargs(TypedDict, total=False):
    """Keyword arguments for gapped translation processing."""

    stop_at_idx: int | None
    """Exclusive block index at which to stop processing."""


def get_gap_translated(
    source: Series,
    target: Series,
    source_language: Language,
    target_language: Language,
    translator: DualNMinusMToNProcessor | None = None,
    **kwargs: Unpack[GappedTranslationProcessKwargs],
) -> Series:
    """Translate target-language subtitle gaps from source-language subtitles.

    Arguments:
        source: source-language reference subtitles
        target: target-language subtitles that may contain gaps
        source_language: source language
        target_language: target language
        translator: processor to use, or None to construct one
        **kwargs: translation process keyword arguments
    Returns:
        target-language subtitles with gaps translated
    """
    if translator is None:
        translator = get_gap_translator(source_language, target_language)
    return translator.process(target, source, **kwargs)


def get_gap_translator(
    source_language: Language,
    target_language: Language,
    prompt_cls: type[DualNMinusMToNPrompt] | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> DualNMinusMToNProcessor:
    """Get a gap translation processor for a supported language pair.

    Arguments:
        source_language: source language
        target_language: target language
        prompt_cls: prompt class override
        test_cases: test cases
        provider: provider to use for queries
        **kwargs: processor initialization keyword arguments
    Returns:
        configured gapped translation processor
    """
    if prompt_cls is None:
        prompt_cls = _PROMPTS[source_language, target_language]
    if test_cases is None:
        json_paths = _JSON_PATHS[source_language, target_language]
        test_cases = list(
            load_default_test_cases(DualNMinusMToNManager, prompt_cls, json_paths)
        )
    if provider is None:
        provider = get_provider()

    return DualNMinusMToNProcessor(prompt_cls, test_cases, provider=provider, **kwargs)
