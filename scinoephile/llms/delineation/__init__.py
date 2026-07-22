#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to delineation using LLMs.

Package hierarchy (modules may import from any above):
* prompt
* models
* manager
* processor
"""

from __future__ import annotations

from .manager import DelineationManager
from .models import DelineationAnswer, DelineationQuery, DelineationTestCase
from .processor import DelineationProcessor
from .prompt import DelineationPrompt

__all__ = [
    "DelineationAnswer",
    "DelineationManager",
    "DelineationProcessor",
    "DelineationPrompt",
    "DelineationQuery",
    "DelineationTestCase",
]
