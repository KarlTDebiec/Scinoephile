#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Registry of prompts available to optimization workflows."""

from __future__ import annotations

from dataclasses import dataclass

import scinoephile.multilang.review.guided as guided_review
import scinoephile.multilang.review.pairwise as pairwise_review
import scinoephile.multilang.translation.gap as gap_translation
import scinoephile.multilang.translation.guided as guided_translation
import scinoephile.multilang.translation.standard as translation
from scinoephile.core import Language
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
    """A registered prompt and its manager."""

    manager_cls: type[Manager]
    """Manager defining the prompt's operation and base contract."""
    prompt: Prompt
    """Concrete prompt."""


PROMPT_SPECS: dict[str, PromptSpec] = {
    "review-eng": PromptSpec(
        manager_cls=ReviewManager,
        prompt=review._PROMPTS[Language.eng],
    ),
    "review-yue-hans": PromptSpec(
        manager_cls=ReviewManager,
        prompt=review._PROMPTS[Language.yue_hans],
    ),
    "review-yue-hant": PromptSpec(
        manager_cls=ReviewManager,
        prompt=review._PROMPTS[Language.yue_hant],
    ),
    "review-zho-hans": PromptSpec(
        manager_cls=ReviewManager,
        prompt=review._PROMPTS[Language.zho_hans],
    ),
    "review-zho-hant": PromptSpec(
        manager_cls=ReviewManager,
        prompt=review._PROMPTS[Language.zho_hant],
    ),
    "ocr-fusion-eng": PromptSpec(
        manager_cls=OcrFusionManager,
        prompt=ocr_fusion._PROMPTS[Language.eng],
    ),
    "ocr-fusion-yue-hans": PromptSpec(
        manager_cls=OcrFusionManager,
        prompt=ocr_fusion._PROMPTS[Language.yue_hans],
    ),
    "ocr-fusion-yue-hant": PromptSpec(
        manager_cls=OcrFusionManager,
        prompt=ocr_fusion._PROMPTS[Language.yue_hant],
    ),
    "ocr-fusion-zho-hans": PromptSpec(
        manager_cls=OcrFusionManager,
        prompt=ocr_fusion._PROMPTS[Language.zho_hans],
    ),
    "ocr-fusion-zho-hant": PromptSpec(
        manager_cls=OcrFusionManager,
        prompt=ocr_fusion._PROMPTS[Language.zho_hant],
    ),
    "guided-review-eng-vs-yue-hans": PromptSpec(
        manager_cls=GuidedReviewManager,
        prompt=guided_review._PROMPTS[(Language.eng, Language.yue_hans)],
    ),
    "guided-review-eng-vs-yue-hant": PromptSpec(
        manager_cls=GuidedReviewManager,
        prompt=guided_review._PROMPTS[(Language.eng, Language.yue_hant)],
    ),
    "guided-review-eng-vs-zho-hans": PromptSpec(
        manager_cls=GuidedReviewManager,
        prompt=guided_review._PROMPTS[(Language.eng, Language.zho_hans)],
    ),
    "guided-review-eng-vs-zho-hant": PromptSpec(
        manager_cls=GuidedReviewManager,
        prompt=guided_review._PROMPTS[(Language.eng, Language.zho_hant)],
    ),
    "guided-review-yue-hans-vs-eng": PromptSpec(
        manager_cls=GuidedReviewManager,
        prompt=guided_review._PROMPTS[(Language.yue_hans, Language.eng)],
    ),
    "guided-review-yue-hans-vs-zho-hans": PromptSpec(
        manager_cls=GuidedReviewManager,
        prompt=guided_review._PROMPTS[(Language.yue_hans, Language.zho_hans)],
    ),
    "guided-review-yue-hans-vs-zho-hant": PromptSpec(
        manager_cls=GuidedReviewManager,
        prompt=guided_review._PROMPTS[(Language.yue_hans, Language.zho_hant)],
    ),
    "guided-review-yue-hant-vs-eng": PromptSpec(
        manager_cls=GuidedReviewManager,
        prompt=guided_review._PROMPTS[(Language.yue_hant, Language.eng)],
    ),
    "guided-review-yue-hant-vs-zho-hans": PromptSpec(
        manager_cls=GuidedReviewManager,
        prompt=guided_review._PROMPTS[(Language.yue_hant, Language.zho_hans)],
    ),
    "guided-review-yue-hant-vs-zho-hant": PromptSpec(
        manager_cls=GuidedReviewManager,
        prompt=guided_review._PROMPTS[(Language.yue_hant, Language.zho_hant)],
    ),
    "guided-review-zho-hans-vs-eng": PromptSpec(
        manager_cls=GuidedReviewManager,
        prompt=guided_review._PROMPTS[(Language.zho_hans, Language.eng)],
    ),
    "guided-review-zho-hans-vs-yue-hans": PromptSpec(
        manager_cls=GuidedReviewManager,
        prompt=guided_review._PROMPTS[(Language.zho_hans, Language.yue_hans)],
    ),
    "guided-review-zho-hans-vs-yue-hant": PromptSpec(
        manager_cls=GuidedReviewManager,
        prompt=guided_review._PROMPTS[(Language.zho_hans, Language.yue_hant)],
    ),
    "guided-review-zho-hant-vs-eng": PromptSpec(
        manager_cls=GuidedReviewManager,
        prompt=guided_review._PROMPTS[(Language.zho_hant, Language.eng)],
    ),
    "guided-review-zho-hant-vs-yue-hans": PromptSpec(
        manager_cls=GuidedReviewManager,
        prompt=guided_review._PROMPTS[(Language.zho_hant, Language.yue_hans)],
    ),
    "guided-review-zho-hant-vs-yue-hant": PromptSpec(
        manager_cls=GuidedReviewManager,
        prompt=guided_review._PROMPTS[(Language.zho_hant, Language.yue_hant)],
    ),
    "pairwise-review-eng-vs-yue-hans": PromptSpec(
        manager_cls=PairwiseReviewManager,
        prompt=pairwise_review._PROMPTS[(Language.eng, Language.yue_hans)],
    ),
    "pairwise-review-eng-vs-yue-hant": PromptSpec(
        manager_cls=PairwiseReviewManager,
        prompt=pairwise_review._PROMPTS[(Language.eng, Language.yue_hant)],
    ),
    "pairwise-review-eng-vs-zho-hans": PromptSpec(
        manager_cls=PairwiseReviewManager,
        prompt=pairwise_review._PROMPTS[(Language.eng, Language.zho_hans)],
    ),
    "pairwise-review-eng-vs-zho-hant": PromptSpec(
        manager_cls=PairwiseReviewManager,
        prompt=pairwise_review._PROMPTS[(Language.eng, Language.zho_hant)],
    ),
    "pairwise-review-yue-hans-vs-eng": PromptSpec(
        manager_cls=PairwiseReviewManager,
        prompt=pairwise_review._PROMPTS[(Language.yue_hans, Language.eng)],
    ),
    "pairwise-review-yue-hans-vs-zho-hans": PromptSpec(
        manager_cls=PairwiseReviewManager,
        prompt=pairwise_review._PROMPTS[(Language.yue_hans, Language.zho_hans)],
    ),
    "pairwise-review-yue-hans-vs-zho-hant": PromptSpec(
        manager_cls=PairwiseReviewManager,
        prompt=pairwise_review._PROMPTS[(Language.yue_hans, Language.zho_hant)],
    ),
    "pairwise-review-yue-hant-vs-eng": PromptSpec(
        manager_cls=PairwiseReviewManager,
        prompt=pairwise_review._PROMPTS[(Language.yue_hant, Language.eng)],
    ),
    "pairwise-review-yue-hant-vs-zho-hans": PromptSpec(
        manager_cls=PairwiseReviewManager,
        prompt=pairwise_review._PROMPTS[(Language.yue_hant, Language.zho_hans)],
    ),
    "pairwise-review-yue-hant-vs-zho-hant": PromptSpec(
        manager_cls=PairwiseReviewManager,
        prompt=pairwise_review._PROMPTS[(Language.yue_hant, Language.zho_hant)],
    ),
    "pairwise-review-zho-hans-vs-eng": PromptSpec(
        manager_cls=PairwiseReviewManager,
        prompt=pairwise_review._PROMPTS[(Language.zho_hans, Language.eng)],
    ),
    "pairwise-review-zho-hans-vs-yue-hans": PromptSpec(
        manager_cls=PairwiseReviewManager,
        prompt=pairwise_review._PROMPTS[(Language.zho_hans, Language.yue_hans)],
    ),
    "pairwise-review-zho-hans-vs-yue-hant": PromptSpec(
        manager_cls=PairwiseReviewManager,
        prompt=pairwise_review._PROMPTS[(Language.zho_hans, Language.yue_hant)],
    ),
    "pairwise-review-zho-hant-vs-eng": PromptSpec(
        manager_cls=PairwiseReviewManager,
        prompt=pairwise_review._PROMPTS[(Language.zho_hant, Language.eng)],
    ),
    "pairwise-review-zho-hant-vs-yue-hans": PromptSpec(
        manager_cls=PairwiseReviewManager,
        prompt=pairwise_review._PROMPTS[(Language.zho_hant, Language.yue_hans)],
    ),
    "pairwise-review-zho-hant-vs-yue-hant": PromptSpec(
        manager_cls=PairwiseReviewManager,
        prompt=pairwise_review._PROMPTS[(Language.zho_hant, Language.yue_hant)],
    ),
    "translation-yue-hans-to-eng": PromptSpec(
        manager_cls=TranslationManager,
        prompt=translation._PROMPTS[(Language.yue_hans, Language.eng)],
    ),
    "translation-yue-hant-to-eng": PromptSpec(
        manager_cls=TranslationManager,
        prompt=translation._PROMPTS[(Language.yue_hant, Language.eng)],
    ),
    "translation-zho-hans-to-eng": PromptSpec(
        manager_cls=TranslationManager,
        prompt=translation._PROMPTS[(Language.zho_hans, Language.eng)],
    ),
    "translation-zho-hant-to-eng": PromptSpec(
        manager_cls=TranslationManager,
        prompt=translation._PROMPTS[(Language.zho_hant, Language.eng)],
    ),
    "translation-eng-to-yue-hans": PromptSpec(
        manager_cls=TranslationManager,
        prompt=translation._PROMPTS[(Language.eng, Language.yue_hans)],
    ),
    "translation-eng-to-yue-hant": PromptSpec(
        manager_cls=TranslationManager,
        prompt=translation._PROMPTS[(Language.eng, Language.yue_hant)],
    ),
    "translation-zho-hans-to-yue-hans": PromptSpec(
        manager_cls=TranslationManager,
        prompt=translation._PROMPTS[(Language.zho_hans, Language.yue_hans)],
    ),
    "translation-zho-hant-to-yue-hans": PromptSpec(
        manager_cls=TranslationManager,
        prompt=translation._PROMPTS[(Language.zho_hant, Language.yue_hans)],
    ),
    "translation-zho-hans-to-yue-hant": PromptSpec(
        manager_cls=TranslationManager,
        prompt=translation._PROMPTS[(Language.zho_hans, Language.yue_hant)],
    ),
    "translation-zho-hant-to-yue-hant": PromptSpec(
        manager_cls=TranslationManager,
        prompt=translation._PROMPTS[(Language.zho_hant, Language.yue_hant)],
    ),
    "translation-eng-to-zho-hans": PromptSpec(
        manager_cls=TranslationManager,
        prompt=translation._PROMPTS[(Language.eng, Language.zho_hans)],
    ),
    "translation-eng-to-zho-hant": PromptSpec(
        manager_cls=TranslationManager,
        prompt=translation._PROMPTS[(Language.eng, Language.zho_hant)],
    ),
    "translation-yue-hans-to-zho-hans": PromptSpec(
        manager_cls=TranslationManager,
        prompt=translation._PROMPTS[(Language.yue_hans, Language.zho_hans)],
    ),
    "translation-yue-hant-to-zho-hans": PromptSpec(
        manager_cls=TranslationManager,
        prompt=translation._PROMPTS[(Language.yue_hant, Language.zho_hans)],
    ),
    "translation-yue-hans-to-zho-hant": PromptSpec(
        manager_cls=TranslationManager,
        prompt=translation._PROMPTS[(Language.yue_hans, Language.zho_hant)],
    ),
    "translation-yue-hant-to-zho-hant": PromptSpec(
        manager_cls=TranslationManager,
        prompt=translation._PROMPTS[(Language.yue_hant, Language.zho_hant)],
    ),
    "gap-translation-yue-hans-to-eng": PromptSpec(
        manager_cls=GapTranslationManager,
        prompt=gap_translation._PROMPTS[(Language.yue_hans, Language.eng)],
    ),
    "gap-translation-yue-hant-to-eng": PromptSpec(
        manager_cls=GapTranslationManager,
        prompt=gap_translation._PROMPTS[(Language.yue_hant, Language.eng)],
    ),
    "gap-translation-zho-hans-to-eng": PromptSpec(
        manager_cls=GapTranslationManager,
        prompt=gap_translation._PROMPTS[(Language.zho_hans, Language.eng)],
    ),
    "gap-translation-zho-hant-to-eng": PromptSpec(
        manager_cls=GapTranslationManager,
        prompt=gap_translation._PROMPTS[(Language.zho_hant, Language.eng)],
    ),
    "gap-translation-eng-to-yue-hans": PromptSpec(
        manager_cls=GapTranslationManager,
        prompt=gap_translation._PROMPTS[(Language.eng, Language.yue_hans)],
    ),
    "gap-translation-eng-to-yue-hant": PromptSpec(
        manager_cls=GapTranslationManager,
        prompt=gap_translation._PROMPTS[(Language.eng, Language.yue_hant)],
    ),
    "gap-translation-zho-hans-to-yue-hans": PromptSpec(
        manager_cls=GapTranslationManager,
        prompt=gap_translation._PROMPTS[(Language.zho_hans, Language.yue_hans)],
    ),
    "gap-translation-zho-hant-to-yue-hans": PromptSpec(
        manager_cls=GapTranslationManager,
        prompt=gap_translation._PROMPTS[(Language.zho_hant, Language.yue_hans)],
    ),
    "gap-translation-zho-hans-to-yue-hant": PromptSpec(
        manager_cls=GapTranslationManager,
        prompt=gap_translation._PROMPTS[(Language.zho_hans, Language.yue_hant)],
    ),
    "gap-translation-zho-hant-to-yue-hant": PromptSpec(
        manager_cls=GapTranslationManager,
        prompt=gap_translation._PROMPTS[(Language.zho_hant, Language.yue_hant)],
    ),
    "gap-translation-eng-to-zho-hans": PromptSpec(
        manager_cls=GapTranslationManager,
        prompt=gap_translation._PROMPTS[(Language.eng, Language.zho_hans)],
    ),
    "gap-translation-eng-to-zho-hant": PromptSpec(
        manager_cls=GapTranslationManager,
        prompt=gap_translation._PROMPTS[(Language.eng, Language.zho_hant)],
    ),
    "gap-translation-yue-hans-to-zho-hans": PromptSpec(
        manager_cls=GapTranslationManager,
        prompt=gap_translation._PROMPTS[(Language.yue_hans, Language.zho_hans)],
    ),
    "gap-translation-yue-hant-to-zho-hans": PromptSpec(
        manager_cls=GapTranslationManager,
        prompt=gap_translation._PROMPTS[(Language.yue_hant, Language.zho_hans)],
    ),
    "gap-translation-yue-hans-to-zho-hant": PromptSpec(
        manager_cls=GapTranslationManager,
        prompt=gap_translation._PROMPTS[(Language.yue_hans, Language.zho_hant)],
    ),
    "gap-translation-yue-hant-to-zho-hant": PromptSpec(
        manager_cls=GapTranslationManager,
        prompt=gap_translation._PROMPTS[(Language.yue_hant, Language.zho_hant)],
    ),
    "guided-translation-yue-hans-to-eng": PromptSpec(
        manager_cls=GuidedTranslationManager,
        prompt=guided_translation._PROMPTS[(Language.yue_hans, Language.eng)],
    ),
    "guided-translation-yue-hant-to-eng": PromptSpec(
        manager_cls=GuidedTranslationManager,
        prompt=guided_translation._PROMPTS[(Language.yue_hant, Language.eng)],
    ),
    "guided-translation-zho-hans-to-eng": PromptSpec(
        manager_cls=GuidedTranslationManager,
        prompt=guided_translation._PROMPTS[(Language.zho_hans, Language.eng)],
    ),
    "guided-translation-zho-hant-to-eng": PromptSpec(
        manager_cls=GuidedTranslationManager,
        prompt=guided_translation._PROMPTS[(Language.zho_hant, Language.eng)],
    ),
    "guided-translation-eng-to-yue-hans": PromptSpec(
        manager_cls=GuidedTranslationManager,
        prompt=guided_translation._PROMPTS[(Language.eng, Language.yue_hans)],
    ),
    "guided-translation-eng-to-yue-hant": PromptSpec(
        manager_cls=GuidedTranslationManager,
        prompt=guided_translation._PROMPTS[(Language.eng, Language.yue_hant)],
    ),
    "guided-translation-zho-hans-to-yue-hans": PromptSpec(
        manager_cls=GuidedTranslationManager,
        prompt=guided_translation._PROMPTS[(Language.zho_hans, Language.yue_hans)],
    ),
    "guided-translation-zho-hant-to-yue-hans": PromptSpec(
        manager_cls=GuidedTranslationManager,
        prompt=guided_translation._PROMPTS[(Language.zho_hant, Language.yue_hans)],
    ),
    "guided-translation-zho-hans-to-yue-hant": PromptSpec(
        manager_cls=GuidedTranslationManager,
        prompt=guided_translation._PROMPTS[(Language.zho_hans, Language.yue_hant)],
    ),
    "guided-translation-zho-hant-to-yue-hant": PromptSpec(
        manager_cls=GuidedTranslationManager,
        prompt=guided_translation._PROMPTS[(Language.zho_hant, Language.yue_hant)],
    ),
    "guided-translation-eng-to-zho-hans": PromptSpec(
        manager_cls=GuidedTranslationManager,
        prompt=guided_translation._PROMPTS[(Language.eng, Language.zho_hans)],
    ),
    "guided-translation-eng-to-zho-hant": PromptSpec(
        manager_cls=GuidedTranslationManager,
        prompt=guided_translation._PROMPTS[(Language.eng, Language.zho_hant)],
    ),
    "guided-translation-yue-hans-to-zho-hans": PromptSpec(
        manager_cls=GuidedTranslationManager,
        prompt=guided_translation._PROMPTS[(Language.yue_hans, Language.zho_hans)],
    ),
    "guided-translation-yue-hant-to-zho-hans": PromptSpec(
        manager_cls=GuidedTranslationManager,
        prompt=guided_translation._PROMPTS[(Language.yue_hant, Language.zho_hans)],
    ),
    "guided-translation-yue-hans-to-zho-hant": PromptSpec(
        manager_cls=GuidedTranslationManager,
        prompt=guided_translation._PROMPTS[(Language.yue_hans, Language.zho_hant)],
    ),
    "guided-translation-yue-hant-to-zho-hant": PromptSpec(
        manager_cls=GuidedTranslationManager,
        prompt=guided_translation._PROMPTS[(Language.yue_hant, Language.zho_hant)],
    ),
    "delineation-yue-hans-vs-zho": PromptSpec(
        manager_cls=DelineationManager,
        prompt=YueDelineationVsZhoPromptYueHans,
    ),
    "delineation-yue-hant-vs-zho": PromptSpec(
        manager_cls=DelineationManager,
        prompt=YueDelineationVsZhoPromptYueHant,
    ),
    "punctuation-yue-hans-vs-zho": PromptSpec(
        manager_cls=PunctuationManager,
        prompt=YuePunctuationVsZhoPromptYueHans,
    ),
    "punctuation-yue-hant-vs-zho": PromptSpec(
        manager_cls=PunctuationManager,
        prompt=YuePunctuationVsZhoPromptYueHant,
    ),
}
"""Registered prompts keyed by stable alias."""
