#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Registry of zero-shot prompts available to optimization workflows."""

from __future__ import annotations

from dataclasses import dataclass

import scinoephile.multilang.review.guided as guided_review
import scinoephile.multilang.review.pairwise as pairwise_review
import scinoephile.multilang.translation.gap as gap_translation
import scinoephile.multilang.translation.guided as guided_translation
import scinoephile.multilang.translation.standard as translation
from scinoephile.core.llms import Manager, Prompt
from scinoephile.lang import ocr_fusion, review
from scinoephile.llms.delineation import DelineationManager
from scinoephile.llms.gap_translation import GapTranslationManager
from scinoephile.llms.guided_review import GuidedReviewManager
from scinoephile.llms.guided_translation import GuidedTranslationManager
from scinoephile.llms.ocr_fusion import OcrFusionManager
from scinoephile.llms.pairwise_review import PairwiseReviewManager
from scinoephile.llms.punctuation import PunctuationManager
from scinoephile.llms.review import ReviewManager
from scinoephile.llms.translation import TranslationManager
from scinoephile.multilang.yue_zho.transcription.delineation import (
    YueDelineationVsZhoPromptYueHans,
    YueDelineationVsZhoPromptYueHant,
)
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YuePunctuationVsZhoPromptYueHans,
    YuePunctuationVsZhoPromptYueHant,
)

__all__ = [
    "PROMPT_SPECS",
    "PromptSpec",
]


@dataclass(frozen=True, slots=True)
class PromptSpec:
    """A registered zero-shot prompt and its stable alias."""

    alias: str
    """Stable workflow-facing alias."""
    manager_cls: type[Manager]
    """Manager defining the prompt's operation and base contract."""
    prompt: Prompt
    """Concrete zero-shot prompt."""


_PROMPT_SPECS = {
    **{
        f"review-{language.tag.lower()}": PromptSpec(
            alias=f"review-{language.tag.lower()}",
            manager_cls=ReviewManager,
            prompt=prompt,
        )
        for language, prompt in review._PROMPTS.items()
    },
    **{
        f"ocr-fusion-{language.tag.lower()}": PromptSpec(
            alias=f"ocr-fusion-{language.tag.lower()}",
            manager_cls=OcrFusionManager,
            prompt=prompt,
        )
        for language, prompt in ocr_fusion._PROMPTS.items()
    },
    **{
        f"guided-review-{language.tag.lower()}-vs-{guide_language.tag.lower()}": (
            PromptSpec(
                alias=(
                    f"guided-review-{language.tag.lower()}-vs-"
                    f"{guide_language.tag.lower()}"
                ),
                manager_cls=GuidedReviewManager,
                prompt=prompt,
            )
        )
        for (language, guide_language), prompt in guided_review._PROMPTS.items()
    },
    **{
        f"pairwise-review-{language.tag.lower()}-vs-"
        f"{reference_language.tag.lower()}": PromptSpec(
            alias=(
                f"pairwise-review-{language.tag.lower()}-vs-"
                f"{reference_language.tag.lower()}"
            ),
            manager_cls=PairwiseReviewManager,
            prompt=prompt,
        )
        for (
            language,
            reference_language,
        ), prompt in pairwise_review._PROMPTS.items()
    },
    **{
        f"translation-{source_language.tag.lower()}-to-"
        f"{target_language.tag.lower()}": PromptSpec(
            alias=(
                f"translation-{source_language.tag.lower()}-to-"
                f"{target_language.tag.lower()}"
            ),
            manager_cls=TranslationManager,
            prompt=prompt,
        )
        for (
            source_language,
            target_language,
        ), prompt in translation._PROMPTS.items()
    },
    **{
        f"gap-translation-{source_language.tag.lower()}-to-"
        f"{target_language.tag.lower()}": PromptSpec(
            alias=(
                f"gap-translation-{source_language.tag.lower()}-to-"
                f"{target_language.tag.lower()}"
            ),
            manager_cls=GapTranslationManager,
            prompt=prompt,
        )
        for (
            source_language,
            target_language,
        ), prompt in gap_translation._PROMPTS.items()
    },
    **{
        f"guided-translation-{source_language.tag.lower()}-to-"
        f"{target_language.tag.lower()}": PromptSpec(
            alias=(
                f"guided-translation-{source_language.tag.lower()}-to-"
                f"{target_language.tag.lower()}"
            ),
            manager_cls=GuidedTranslationManager,
            prompt=prompt,
        )
        for (
            source_language,
            target_language,
        ), prompt in guided_translation._PROMPTS.items()
    },
    "delineation-yue-hans-vs-zho": PromptSpec(
        alias="delineation-yue-hans-vs-zho",
        manager_cls=DelineationManager,
        prompt=YueDelineationVsZhoPromptYueHans,
    ),
    "delineation-yue-hant-vs-zho": PromptSpec(
        alias="delineation-yue-hant-vs-zho",
        manager_cls=DelineationManager,
        prompt=YueDelineationVsZhoPromptYueHant,
    ),
    "punctuation-yue-hans-vs-zho": PromptSpec(
        alias="punctuation-yue-hans-vs-zho",
        manager_cls=PunctuationManager,
        prompt=YuePunctuationVsZhoPromptYueHans,
    ),
    "punctuation-yue-hant-vs-zho": PromptSpec(
        alias="punctuation-yue-hant-vs-zho",
        manager_cls=PunctuationManager,
        prompt=YuePunctuationVsZhoPromptYueHant,
    ),
}
"""Registered prompt specifications before canonical alias ordering."""

PROMPT_SPECS: dict[str, PromptSpec] = dict(sorted(_PROMPT_SPECS.items()))
"""Registered zero-shot prompts keyed by stable alias."""
