#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to punctuation using LLMs.

Package hierarchy (modules may import from any above):
* prompt
* manager
"""

from __future__ import annotations

from scinoephile.core.llms import OperationSpec

from .manager import PunctuationManager
from .prompt import PunctuationPrompt

__all__ = [
    "PUNCTUATION_OPERATION_SPEC",
    "PunctuationManager",
    "PunctuationPrompt",
]

PUNCTUATION_OPERATION_SPEC = OperationSpec(
    operation="punctuation",
    test_case_table_name="test_cases__punctuation",
    manager_cls=PunctuationManager,
    prompt_cls=PunctuationPrompt,
    list_fields={f"query.{PunctuationPrompt.src_1}": 10},
)
"""Operation specification for punctuation."""
