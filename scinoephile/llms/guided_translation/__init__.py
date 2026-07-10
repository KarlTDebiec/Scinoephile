#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to guided translation using LLMs.

Package hierarchy (modules may import from any above):
* prompt
* manager
* processor
"""

from __future__ import annotations

from scinoephile.core.llms import OperationSpec

from .manager import GuidedTranslationManager
from .processor import GuidedTranslationProcessor
from .prompt import GuidedTranslationPrompt

__all__ = [
    "GUIDED_TRANSLATION_OPERATION_SPEC",
    "GuidedTranslationManager",
    "GuidedTranslationProcessor",
    "GuidedTranslationPrompt",
]

GUIDED_TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="guided-translation",
    manager_cls=GuidedTranslationManager,
    prompt_cls=GuidedTranslationPrompt,
)
"""Operation specification for guided translation."""
