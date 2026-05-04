#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Operation specification for LLM-backed workflows."""

from __future__ import annotations

from dataclasses import dataclass, field

from .manager import Manager
from .prompt import Prompt

__all__ = ["OperationSpec"]


@dataclass(frozen=True, slots=True)
class OperationSpec:
    """Specification for an LLM-backed operation."""

    operation: str
    """Operation name exposed through CLIs and registries."""
    test_case_table_name: str
    """SQLite table name used to persist test cases for this operation."""
    manager_cls: type[Manager]
    """Manager class used to load and validate cases for this operation."""
    prompt_cls: type[Prompt]
    """Prompt class used to load and validate cases for this operation."""
    list_fields: dict[str, int] = field(default_factory=dict)
    """Payload fields to store as fixed-width scalar SQLite columns."""
