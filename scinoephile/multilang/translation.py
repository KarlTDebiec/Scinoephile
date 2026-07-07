#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Unified translation routing across supported language pairs."""

from __future__ import annotations

from typing import Literal, NoReturn

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms.llm_provider import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.multilang.eng_yue.gapped_translation import (
    get_eng_gapped_translated_vs_yue,
    get_eng_vs_yue_gapped_translator,
)
from scinoephile.multilang.eng_yue.guided_translation import (
    get_eng_translated_from_yue_with_eng_guidance,
    get_eng_yue_guided_translator,
)
from scinoephile.multilang.eng_yue.translation import (
    get_eng_translated_from_yue,
    get_eng_yue_translator,
)
from scinoephile.multilang.eng_zho.gapped_translation import (
    get_eng_gapped_translated_vs_zho,
    get_eng_vs_zho_gapped_translator,
)
from scinoephile.multilang.eng_zho.guided_translation import (
    get_eng_translated_from_zho_with_eng_guidance,
    get_eng_zho_guided_translator,
)
from scinoephile.multilang.eng_zho.translation import (
    get_eng_translated_from_zho,
    get_eng_zho_translator,
)
from scinoephile.multilang.yue_eng.gapped_translation import (
    YueGappedTranslationVsEngPromptYueHans,
    YueGappedTranslationVsEngPromptYueHant,
    get_yue_gapped_translated_vs_eng,
    get_yue_vs_eng_gapped_translator,
)
from scinoephile.multilang.yue_eng.guided_translation import (
    YueGuidedTranslationVsEngPromptYueHans,
    YueGuidedTranslationVsEngPromptYueHant,
    get_yue_eng_guided_translator,
    get_yue_translated_from_eng_with_yue_guidance,
)
from scinoephile.multilang.yue_eng.translation import (
    YueTranslationVsEngPromptYueHans,
    YueTranslationVsEngPromptYueHant,
    get_yue_eng_translator,
    get_yue_translated_from_eng,
)
from scinoephile.multilang.yue_zho.gapped_translation import (
    YueGappedTranslationVsZhoPromptYueHans,
    YueGappedTranslationVsZhoPromptYueHant,
    get_yue_gapped_translated_vs_zho,
    get_yue_vs_zho_gapped_translator,
)
from scinoephile.multilang.yue_zho.guided_translation import (
    YueGuidedTranslationVsZhoPromptYueHans,
    YueGuidedTranslationVsZhoPromptYueHant,
    get_yue_translated_from_zho_with_yue_guidance,
    get_yue_zho_guided_translator,
)
from scinoephile.multilang.yue_zho.translation import (
    YueTranslationVsZhoPromptYueHans,
    YueTranslationVsZhoPromptYueHant,
    get_yue_translated_from_zho,
    get_yue_zho_translator,
)
from scinoephile.multilang.zho_eng.gapped_translation import (
    ZhoGappedTranslationVsEngPromptZhoHans,
    ZhoGappedTranslationVsEngPromptZhoHant,
    get_zho_gapped_translated_vs_eng,
    get_zho_vs_eng_gapped_translator,
)
from scinoephile.multilang.zho_eng.guided_translation import (
    ZhoGuidedTranslationVsEngPromptZhoHans,
    ZhoGuidedTranslationVsEngPromptZhoHant,
    get_zho_eng_guided_translator,
    get_zho_translated_from_eng_with_zho_guidance,
)
from scinoephile.multilang.zho_eng.translation import (
    ZhoTranslationVsEngPromptZhoHans,
    ZhoTranslationVsEngPromptZhoHant,
    get_zho_eng_translator,
    get_zho_translated_from_eng,
)
from scinoephile.multilang.zho_yue.gapped_translation import (
    ZhoGappedTranslationVsYuePromptZhoHans,
    ZhoGappedTranslationVsYuePromptZhoHant,
    get_zho_gapped_translated_vs_yue,
    get_zho_vs_yue_gapped_translator,
)
from scinoephile.multilang.zho_yue.guided_translation import (
    ZhoGuidedTranslationVsYuePromptZhoHans,
    ZhoGuidedTranslationVsYuePromptZhoHant,
    get_zho_translated_from_yue_with_zho_guidance,
    get_zho_yue_guided_translator,
)
from scinoephile.multilang.zho_yue.translation import (
    ZhoTranslationVsYuePromptZhoHans,
    ZhoTranslationVsYuePromptZhoHant,
    get_zho_translated_from_yue,
    get_zho_yue_translator,
)

__all__ = [
    "TranslationMode",
    "translate_series",
]

TranslationMode = Literal["regular", "gapped", "guided"]
"""Supported translation mode identifier."""

_YUE_LANGUAGES = (Language.yue_hans, Language.yue_hant)
"""Written Cantonese language tags."""
_ZHO_LANGUAGES = (Language.zho_hans, Language.zho_hant)
"""Standard Chinese language tags."""


def translate_series(
    *,
    source: Series,
    source_language: Language,
    target_language: Language,
    mode: TranslationMode = "regular",
    target: Series | None = None,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
) -> Series:
    """Translate a subtitle series between supported languages.

    Arguments:
        source: source-language subtitle series
        source_language: detected or explicit source language
        target_language: resolved target language
        mode: translation mode to run
        target: target-language guide or gapped subtitle series
        provider: LLM provider to use
        additional_context: additional context to include in prompts
    Returns:
        translated subtitle series
    Raises:
        ScinoephileError: if the language pair or mode is unsupported
    """
    if target_language is Language.eng:
        return _translate_to_eng(
            source=source,
            source_language=source_language,
            mode=mode,
            target=target,
            provider=provider,
            additional_context=additional_context,
        )
    if target_language in _YUE_LANGUAGES:
        return _translate_to_yue(
            source=source,
            source_language=source_language,
            target_language=target_language,
            mode=mode,
            target=target,
            provider=provider,
            additional_context=additional_context,
        )
    if target_language in _ZHO_LANGUAGES:
        return _translate_to_zho(
            source=source,
            source_language=source_language,
            target_language=target_language,
            mode=mode,
            target=target,
            provider=provider,
            additional_context=additional_context,
        )
    _raise_unsupported_pair(source_language, target_language)


def _raise_unsupported_pair(
    source_language: Language,
    target_language: Language,
) -> NoReturn:
    """Raise an unsupported language-pair error.

    Arguments:
        source_language: source language
        target_language: target language
    Raises:
        ScinoephileError: always
    """
    raise ScinoephileError(
        f"Unsupported translation pair: {source_language.tag} to {target_language.tag}"
    )


def _require_target(mode: TranslationMode, target: Series | None) -> Series:
    """Require target-language input for guided and gapped modes.

    Arguments:
        mode: translation mode
        target: target-language guide or gapped subtitle series
    Returns:
        target-language subtitle series
    Raises:
        ScinoephileError: if target input is missing
    """
    if target is None:
        raise ScinoephileError(f"{mode} translation requires target subtitles")
    return target


def _translate_eng_from_yue(
    *,
    source: Series,
    mode: TranslationMode,
    target: Series | None,
    provider: LLMProvider | None,
    additional_context: str | None,
) -> Series:
    """Translate written Cantonese subtitles to English.

    Arguments:
        source: written Cantonese subtitle series
        mode: translation mode to run
        target: English guide or gapped subtitle series
        provider: LLM provider to use
        additional_context: additional context to include in prompts
    Returns:
        English subtitle series
    """
    if mode == "regular":
        translator = get_eng_yue_translator(
            provider=provider,
            additional_context=additional_context,
        )
        return get_eng_translated_from_yue(yuewen=source, translator=translator)

    target = _require_target(mode, target)
    if mode == "gapped":
        translator = get_eng_vs_yue_gapped_translator(
            provider=provider,
            additional_context=additional_context,
        )
        return get_eng_gapped_translated_vs_yue(
            eng=target,
            yuewen=source,
            translator=translator,
        )
    if mode == "guided":
        translator = get_eng_yue_guided_translator(
            provider=provider,
            additional_context=additional_context,
        )
        return get_eng_translated_from_yue_with_eng_guidance(
            yuewen=source,
            eng=target,
            translator=translator,
        )
    raise ScinoephileError(f"Unsupported translation mode: {mode}")


def _translate_eng_from_zho(
    *,
    source: Series,
    mode: TranslationMode,
    target: Series | None,
    provider: LLMProvider | None,
    additional_context: str | None,
) -> Series:
    """Translate standard Chinese subtitles to English.

    Arguments:
        source: standard Chinese subtitle series
        mode: translation mode to run
        target: English guide or gapped subtitle series
        provider: LLM provider to use
        additional_context: additional context to include in prompts
    Returns:
        English subtitle series
    """
    if mode == "regular":
        translator = get_eng_zho_translator(
            provider=provider,
            additional_context=additional_context,
        )
        return get_eng_translated_from_zho(zho=source, translator=translator)

    target = _require_target(mode, target)
    if mode == "gapped":
        translator = get_eng_vs_zho_gapped_translator(
            provider=provider,
            additional_context=additional_context,
        )
        return get_eng_gapped_translated_vs_zho(
            eng=target,
            zho=source,
            translator=translator,
        )
    if mode == "guided":
        translator = get_eng_zho_guided_translator(
            provider=provider,
            additional_context=additional_context,
        )
        return get_eng_translated_from_zho_with_eng_guidance(
            zho=source,
            eng=target,
            translator=translator,
        )
    raise ScinoephileError(f"Unsupported translation mode: {mode}")


def _translate_to_eng(
    *,
    source: Series,
    source_language: Language,
    mode: TranslationMode,
    target: Series | None,
    provider: LLMProvider | None,
    additional_context: str | None,
) -> Series:
    """Translate subtitles to English.

    Arguments:
        source: source-language subtitle series
        source_language: detected or explicit source language
        mode: translation mode to run
        target: English guide or gapped subtitle series
        provider: LLM provider to use
        additional_context: additional context to include in prompts
    Returns:
        English subtitle series
    Raises:
        ScinoephileError: if the source language is unsupported
    """
    if source_language in _YUE_LANGUAGES:
        return _translate_eng_from_yue(
            source=source,
            mode=mode,
            target=target,
            provider=provider,
            additional_context=additional_context,
        )
    if source_language in _ZHO_LANGUAGES:
        return _translate_eng_from_zho(
            source=source,
            mode=mode,
            target=target,
            provider=provider,
            additional_context=additional_context,
        )
    _raise_unsupported_pair(source_language, Language.eng)


def _translate_to_yue(
    *,
    source: Series,
    source_language: Language,
    target_language: Language,
    mode: TranslationMode,
    target: Series | None,
    provider: LLMProvider | None,
    additional_context: str | None,
) -> Series:
    """Translate subtitles to written Cantonese.

    Arguments:
        source: source-language subtitle series
        source_language: detected or explicit source language
        target_language: written Cantonese target language
        mode: translation mode to run
        target: written Cantonese guide or gapped subtitle series
        provider: LLM provider to use
        additional_context: additional context to include in prompts
    Returns:
        written Cantonese subtitle series
    Raises:
        ScinoephileError: if the source language is unsupported
    """
    if source_language is Language.eng:
        return _translate_yue_from_eng(
            source=source,
            target_language=target_language,
            mode=mode,
            target=target,
            provider=provider,
            additional_context=additional_context,
        )
    if source_language in _ZHO_LANGUAGES:
        return _translate_yue_from_zho(
            source=source,
            target_language=target_language,
            mode=mode,
            target=target,
            provider=provider,
            additional_context=additional_context,
        )
    _raise_unsupported_pair(source_language, target_language)


def _translate_to_zho(
    *,
    source: Series,
    source_language: Language,
    target_language: Language,
    mode: TranslationMode,
    target: Series | None,
    provider: LLMProvider | None,
    additional_context: str | None,
) -> Series:
    """Translate subtitles to standard Chinese.

    Arguments:
        source: source-language subtitle series
        source_language: detected or explicit source language
        target_language: standard Chinese target language
        mode: translation mode to run
        target: standard Chinese guide or gapped subtitle series
        provider: LLM provider to use
        additional_context: additional context to include in prompts
    Returns:
        standard Chinese subtitle series
    Raises:
        ScinoephileError: if the source language is unsupported
    """
    if source_language is Language.eng:
        return _translate_zho_from_eng(
            source=source,
            target_language=target_language,
            mode=mode,
            target=target,
            provider=provider,
            additional_context=additional_context,
        )
    if source_language in _YUE_LANGUAGES:
        return _translate_zho_from_yue(
            source=source,
            target_language=target_language,
            mode=mode,
            target=target,
            provider=provider,
            additional_context=additional_context,
        )
    _raise_unsupported_pair(source_language, target_language)


def _translate_yue_from_eng(
    *,
    source: Series,
    target_language: Language,
    mode: TranslationMode,
    target: Series | None,
    provider: LLMProvider | None,
    additional_context: str | None,
) -> Series:
    """Translate English subtitles to written Cantonese.

    Arguments:
        source: English subtitle series
        target_language: written Cantonese target language
        mode: translation mode to run
        target: written Cantonese guide or gapped subtitle series
        provider: LLM provider to use
        additional_context: additional context to include in prompts
    Returns:
        written Cantonese subtitle series
    """
    if mode == "regular":
        if target_language is Language.yue_hant:
            translator = get_yue_eng_translator(
                prompt_cls=YueTranslationVsEngPromptYueHant,
                provider=provider,
                additional_context=additional_context,
            )
        else:
            translator = get_yue_eng_translator(
                prompt_cls=YueTranslationVsEngPromptYueHans,
                provider=provider,
                additional_context=additional_context,
            )
        return get_yue_translated_from_eng(eng=source, translator=translator)

    target = _require_target(mode, target)
    if mode == "gapped":
        if target_language is Language.yue_hant:
            translator = get_yue_vs_eng_gapped_translator(
                prompt_cls=YueGappedTranslationVsEngPromptYueHant,
                provider=provider,
                additional_context=additional_context,
            )
        else:
            translator = get_yue_vs_eng_gapped_translator(
                prompt_cls=YueGappedTranslationVsEngPromptYueHans,
                provider=provider,
                additional_context=additional_context,
            )
        return get_yue_gapped_translated_vs_eng(
            yuewen=target,
            eng=source,
            translator=translator,
        )
    if mode == "guided":
        if target_language is Language.yue_hant:
            translator = get_yue_eng_guided_translator(
                prompt_cls=YueGuidedTranslationVsEngPromptYueHant,
                provider=provider,
                additional_context=additional_context,
            )
        else:
            translator = get_yue_eng_guided_translator(
                prompt_cls=YueGuidedTranslationVsEngPromptYueHans,
                provider=provider,
                additional_context=additional_context,
            )
        return get_yue_translated_from_eng_with_yue_guidance(
            eng=source,
            yuewen=target,
            translator=translator,
        )
    raise ScinoephileError(f"Unsupported translation mode: {mode}")


def _translate_yue_from_zho(
    *,
    source: Series,
    target_language: Language,
    mode: TranslationMode,
    target: Series | None,
    provider: LLMProvider | None,
    additional_context: str | None,
) -> Series:
    """Translate standard Chinese subtitles to written Cantonese.

    Arguments:
        source: standard Chinese subtitle series
        target_language: written Cantonese target language
        mode: translation mode to run
        target: written Cantonese guide or gapped subtitle series
        provider: LLM provider to use
        additional_context: additional context to include in prompts
    Returns:
        written Cantonese subtitle series
    """
    if mode == "regular":
        if target_language is Language.yue_hant:
            translator = get_yue_zho_translator(
                prompt_cls=YueTranslationVsZhoPromptYueHant,
                provider=provider,
                additional_context=additional_context,
            )
        else:
            translator = get_yue_zho_translator(
                prompt_cls=YueTranslationVsZhoPromptYueHans,
                provider=provider,
                additional_context=additional_context,
            )
        return get_yue_translated_from_zho(zhongwen=source, translator=translator)

    target = _require_target(mode, target)
    if mode == "gapped":
        if target_language is Language.yue_hant:
            translator = get_yue_vs_zho_gapped_translator(
                prompt_cls=YueGappedTranslationVsZhoPromptYueHant,
                provider=provider,
                additional_context=additional_context,
            )
        else:
            translator = get_yue_vs_zho_gapped_translator(
                prompt_cls=YueGappedTranslationVsZhoPromptYueHans,
                provider=provider,
                additional_context=additional_context,
            )
        return get_yue_gapped_translated_vs_zho(
            yuewen=target,
            zhongwen=source,
            translator=translator,
        )
    if mode == "guided":
        if target_language is Language.yue_hant:
            translator = get_yue_zho_guided_translator(
                prompt_cls=YueGuidedTranslationVsZhoPromptYueHant,
                provider=provider,
                additional_context=additional_context,
            )
        else:
            translator = get_yue_zho_guided_translator(
                prompt_cls=YueGuidedTranslationVsZhoPromptYueHans,
                provider=provider,
                additional_context=additional_context,
            )
        return get_yue_translated_from_zho_with_yue_guidance(
            zhongwen=source,
            yuewen=target,
            translator=translator,
        )
    raise ScinoephileError(f"Unsupported translation mode: {mode}")


def _translate_zho_from_eng(
    *,
    source: Series,
    target_language: Language,
    mode: TranslationMode,
    target: Series | None,
    provider: LLMProvider | None,
    additional_context: str | None,
) -> Series:
    """Translate English subtitles to standard Chinese.

    Arguments:
        source: English subtitle series
        target_language: standard Chinese target language
        mode: translation mode to run
        target: standard Chinese guide or gapped subtitle series
        provider: LLM provider to use
        additional_context: additional context to include in prompts
    Returns:
        standard Chinese subtitle series
    """
    if mode == "regular":
        if target_language is Language.zho_hant:
            translator = get_zho_eng_translator(
                prompt_cls=ZhoTranslationVsEngPromptZhoHant,
                provider=provider,
                additional_context=additional_context,
            )
        else:
            translator = get_zho_eng_translator(
                prompt_cls=ZhoTranslationVsEngPromptZhoHans,
                provider=provider,
                additional_context=additional_context,
            )
        return get_zho_translated_from_eng(eng=source, translator=translator)

    target = _require_target(mode, target)
    if mode == "gapped":
        if target_language is Language.zho_hant:
            translator = get_zho_vs_eng_gapped_translator(
                prompt_cls=ZhoGappedTranslationVsEngPromptZhoHant,
                provider=provider,
                additional_context=additional_context,
            )
        else:
            translator = get_zho_vs_eng_gapped_translator(
                prompt_cls=ZhoGappedTranslationVsEngPromptZhoHans,
                provider=provider,
                additional_context=additional_context,
            )
        return get_zho_gapped_translated_vs_eng(
            zhongwen=target,
            eng=source,
            translator=translator,
        )
    if mode == "guided":
        if target_language is Language.zho_hant:
            translator = get_zho_eng_guided_translator(
                prompt_cls=ZhoGuidedTranslationVsEngPromptZhoHant,
                provider=provider,
                additional_context=additional_context,
            )
        else:
            translator = get_zho_eng_guided_translator(
                prompt_cls=ZhoGuidedTranslationVsEngPromptZhoHans,
                provider=provider,
                additional_context=additional_context,
            )
        return get_zho_translated_from_eng_with_zho_guidance(
            eng=source,
            zhongwen=target,
            translator=translator,
        )
    raise ScinoephileError(f"Unsupported translation mode: {mode}")


def _translate_zho_from_yue(
    *,
    source: Series,
    target_language: Language,
    mode: TranslationMode,
    target: Series | None,
    provider: LLMProvider | None,
    additional_context: str | None,
) -> Series:
    """Translate written Cantonese subtitles to standard Chinese.

    Arguments:
        source: written Cantonese subtitle series
        target_language: standard Chinese target language
        mode: translation mode to run
        target: standard Chinese guide or gapped subtitle series
        provider: LLM provider to use
        additional_context: additional context to include in prompts
    Returns:
        standard Chinese subtitle series
    """
    if mode == "regular":
        if target_language is Language.zho_hant:
            translator = get_zho_yue_translator(
                prompt_cls=ZhoTranslationVsYuePromptZhoHant,
                provider=provider,
                additional_context=additional_context,
            )
        else:
            translator = get_zho_yue_translator(
                prompt_cls=ZhoTranslationVsYuePromptZhoHans,
                provider=provider,
                additional_context=additional_context,
            )
        return get_zho_translated_from_yue(yuewen=source, translator=translator)

    target = _require_target(mode, target)
    if mode == "gapped":
        if target_language is Language.zho_hant:
            translator = get_zho_vs_yue_gapped_translator(
                prompt_cls=ZhoGappedTranslationVsYuePromptZhoHant,
                provider=provider,
                additional_context=additional_context,
            )
        else:
            translator = get_zho_vs_yue_gapped_translator(
                prompt_cls=ZhoGappedTranslationVsYuePromptZhoHans,
                provider=provider,
                additional_context=additional_context,
            )
        return get_zho_gapped_translated_vs_yue(
            zhongwen=target,
            yuewen=source,
            translator=translator,
        )
    if mode == "guided":
        if target_language is Language.zho_hant:
            translator = get_zho_yue_guided_translator(
                prompt_cls=ZhoGuidedTranslationVsYuePromptZhoHant,
                provider=provider,
                additional_context=additional_context,
            )
        else:
            translator = get_zho_yue_guided_translator(
                prompt_cls=ZhoGuidedTranslationVsYuePromptZhoHans,
                provider=provider,
                additional_context=additional_context,
            )
        return get_zho_translated_from_yue_with_zho_guidance(
            yuewen=source,
            zhongwen=target,
            translator=translator,
        )
    raise ScinoephileError(f"Unsupported translation mode: {mode}")
