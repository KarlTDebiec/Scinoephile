#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processor for delineation LLM queries."""

from __future__ import annotations

from scinoephile.core.llms import Processor

from .manager import DelineationManager
from .prompt import DelineationPrompt

__all__ = ["DelineationProcessor"]


class DelineationProcessor(Processor):
    """Processor for delineation LLM queries."""

    prompt: DelineationPrompt
    """Text for LLM correspondence."""

    manager_cls = DelineationManager
    """Manager class used to construct test case models."""
