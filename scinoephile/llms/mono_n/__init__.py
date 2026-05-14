#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to mono n matters using LLMs.

Package hierarchy (modules may import from any above):
* prompt
* manager
* processor
"""

from __future__ import annotations

from .manager import MonoNManager
from .processor import MonoNProcessor
from .prompt import MonoNPrompt

__all__ = [
    "MonoNManager",
    "MonoNPrompt",
    "MonoNProcessor",
]
