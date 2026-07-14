#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Generic prompt specification for optimization operations."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Manager, Prompt

__all__ = ["PromptSpec"]


@dataclass(frozen=True, slots=True)
class PromptSpec:
    """A prompt and the manager defining its operation."""

    manager_cls: type[Manager]
    """Manager defining the prompt's operation and base contract."""
    prompt: Prompt
    """Concrete prompt."""
