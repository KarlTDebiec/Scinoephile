#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Application catalog of prompts available to optimization workflows."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

import scinoephile.lang.review.guided as guided_review
import scinoephile.lang.review.standard as review
import scinoephile.lang.transcription.guided as guided_transcription
import scinoephile.lang.translation.gap as gap_translation
import scinoephile.lang.translation.guided as guided_translation
import scinoephile.lang.translation.standard as translation
from scinoephile.core import Language
from scinoephile.core.llms import Manager, Prompt
from scinoephile.lang import ocr_fusion
from scinoephile.llms.delineation import DelineationManager
from scinoephile.llms.gap_translation import GapTranslationManager
from scinoephile.llms.guided_review import GuidedReviewManager
from scinoephile.llms.guided_translation import GuidedTranslationManager
from scinoephile.llms.ocr_fusion import OcrFusionManager
from scinoephile.llms.punctuation import PunctuationManager
from scinoephile.llms.review import ReviewManager
from scinoephile.llms.translation import TranslationManager
from scinoephile.optimization.prompt_spec import PromptSpec

__all__ = ["PROMPT_SPECS"]


def _build_prompt_specs() -> Mapping[str, PromptSpec]:
    """Build the application prompt catalog and reject duplicate aliases.

    Returns:
        read-only prompt specifications keyed by stable alias
    """
    prompt_spec_groups = (
        _build_monolingual_prompt_specs(ReviewManager, review.DEFAULT_PROMPTS),
        _build_monolingual_prompt_specs(OcrFusionManager, ocr_fusion.DEFAULT_PROMPTS),
        _build_pair_prompt_specs(
            GuidedReviewManager,
            guided_review.DEFAULT_PROMPTS,
            separator="vs",
        ),
        _build_pair_prompt_specs(
            TranslationManager,
            translation.DEFAULT_PROMPTS,
            separator="to",
        ),
        _build_pair_prompt_specs(
            GapTranslationManager,
            gap_translation.DEFAULT_PROMPTS,
            separator="to",
        ),
        _build_pair_prompt_specs(
            GuidedTranslationManager,
            guided_translation.DEFAULT_PROMPTS,
            separator="to",
        ),
        _build_transcription_prompt_specs(guided_transcription.DEFAULT_SPECS),
    )

    prompt_specs: dict[str, PromptSpec] = {}
    for prompt_spec_group in prompt_spec_groups:
        duplicate_aliases = prompt_specs.keys() & prompt_spec_group.keys()
        if duplicate_aliases:
            aliases = ", ".join(sorted(duplicate_aliases))
            raise ValueError(f"Duplicate prompt aliases: {aliases}")
        prompt_specs.update(prompt_spec_group)
    return MappingProxyType(dict(sorted(prompt_specs.items())))


def _build_monolingual_prompt_specs(
    manager_cls: type[Manager],
    prompts: Mapping[Language, Prompt],
) -> dict[str, PromptSpec]:
    """Build prompt specifications for a monolingual operation.

    Arguments:
        manager_cls: manager defining the operation
        prompts: default prompts keyed by language
    Returns:
        prompt specifications keyed by stable alias
    """
    return {
        f"{manager_cls.operation}-{language.code.lower()}": PromptSpec(
            manager_cls=manager_cls,
            prompt=prompt,
        )
        for language, prompt in prompts.items()
    }


def _build_pair_prompt_specs(
    manager_cls: type[Manager],
    prompts: Mapping[tuple[Language, Language], Prompt],
    *,
    separator: str,
) -> dict[str, PromptSpec]:
    """Build prompt specifications for a language-pair operation.

    Arguments:
        manager_cls: manager defining the operation
        prompts: default prompts keyed by language pair
        separator: alias separator between the two language tags
    Returns:
        prompt specifications keyed by stable alias
    """
    return {
        (
            f"{manager_cls.operation}-{first_language.code.lower()}-"
            f"{separator}-{second_language.code.lower()}"
        ): PromptSpec(
            manager_cls=manager_cls,
            prompt=prompt,
        )
        for (first_language, second_language), prompt in prompts.items()
    }


def _build_transcription_prompt_specs(
    specs: Mapping[
        tuple[Language, Language],
        guided_transcription.GuidedTranscriptionSpec,
    ],
) -> dict[str, PromptSpec]:
    """Build prompt specifications for guided transcription.

    Reference-script variants that share a prompt use one stable language-code alias.

    Arguments:
        specs: guided transcription specifications keyed by language pair
    Returns:
        prompt specifications keyed by stable alias
    Raises:
        ValueError: if one alias resolves to conflicting prompts
    """
    prompt_specs: dict[str, PromptSpec] = {}
    for (language, reference_language), spec in specs.items():
        reference_code = reference_language.language.lower()
        for manager_cls, prompt in (
            (DelineationManager, spec.delineation_prompt),
            (PunctuationManager, spec.punctuation_prompt),
        ):
            alias = (
                f"{manager_cls.operation}-{language.code.lower()}-vs-{reference_code}"
            )
            prompt_spec = PromptSpec(manager_cls=manager_cls, prompt=prompt)
            if alias in prompt_specs and prompt_specs[alias] != prompt_spec:
                raise ValueError(
                    f"Conflicting guided transcription prompt alias: {alias}"
                )
            prompt_specs[alias] = prompt_spec
    return prompt_specs


PROMPT_SPECS: Mapping[str, PromptSpec] = _build_prompt_specs()
"""Registered prompts keyed by stable alias."""
