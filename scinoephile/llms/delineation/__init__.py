#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to delineation using LLMs.

Package hierarchy (modules may import from any above):
* prompt
* manager
"""

from __future__ import annotations

from scinoephile.core.llms import OperationSpec

from .manager import DelineationManager
from .prompt import DelineationPrompt

__all__ = [
    "DELINEATION_OPERATION_SPEC",
    "DelineationManager",
    "DelineationPrompt",
]

DELINEATION_OPERATION_SPEC = OperationSpec(
    operation="delineation",
    manager_cls=DelineationManager,
    prompt_cls=DelineationPrompt,
)
"""Operation specification for delineation."""
