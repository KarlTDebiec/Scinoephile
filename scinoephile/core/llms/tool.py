#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""One LLM-callable tool."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

__all__ = ["Tool"]


@dataclass(frozen=True)
class Tool:
    """One LLM-callable tool definition and its local handler."""

    spec: dict[str, object]
    """Tool schema exposed to the model."""

    handler: Callable[[dict[str, Any]], object]
    """Local handler for executing the tool."""

    @property
    def name(self) -> str:
        """Tool name."""
        return cast(str, self.spec["name"])
