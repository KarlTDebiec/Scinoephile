#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Delineation operation configuration."""

from __future__ import annotations

from scinoephile.core.llms import OperationSpec

from .manager import DelineationManager
from .prompt import DelineationPrompt

__all__ = ["DELINEATION_OPERATION_SPEC"]


DELINEATION_OPERATION_SPEC = OperationSpec(
    operation="delineation",
    test_case_table_name="test_cases__delineation",
    manager_cls=DelineationManager,
    prompt_cls=DelineationPrompt,
)
"""Operation specification for delineation."""
