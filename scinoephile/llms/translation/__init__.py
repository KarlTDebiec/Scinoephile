#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to translation matters using LLMs.

Package hierarchy (modules may import from any above):
* prompt
* manager
* processor
"""

from __future__ import annotations

from scinoephile.core.llms import OperationSpec

from .manager import TranslationManager
from .processor import TranslationProcessor
from .prompt import TranslationPrompt

__all__ = [
    "TRANSLATION_OPERATION_SPEC",
    "TranslationManager",
    "TranslationPrompt",
    "TranslationProcessor",
]

TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="translation",
    manager_cls=TranslationManager,
    prompt_cls=TranslationPrompt,
)
"""Operation specification for regular translation."""
