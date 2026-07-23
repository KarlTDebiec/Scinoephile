#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Operation registry for optimization workflows."""

from __future__ import annotations

from scinoephile.core.llms import Manager
from scinoephile.llms.delineation import DelineationManager
from scinoephile.llms.gap_translation import GapTranslationManager
from scinoephile.llms.guided_review import GuidedReviewManager
from scinoephile.llms.guided_translation import GuidedTranslationManager
from scinoephile.llms.ocr_fusion import OcrFusionManager
from scinoephile.llms.punctuation import PunctuationManager
from scinoephile.llms.review import ReviewManager
from scinoephile.llms.translation import TranslationManager

__all__ = ["OPERATIONS"]


OPERATIONS: dict[str, type[Manager]] = {
    manager_cls.operation: manager_cls
    for manager_cls in sorted(
        (
            DelineationManager,
            GapTranslationManager,
            GuidedReviewManager,
            GuidedTranslationManager,
            OcrFusionManager,
            PunctuationManager,
            ReviewManager,
            TranslationManager,
        ),
        key=lambda manager_cls: manager_cls.operation,
    )
}
"""Optimization manager classes keyed by operation name."""
