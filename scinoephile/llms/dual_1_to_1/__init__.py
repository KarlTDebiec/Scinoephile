#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to dual 1 to 1 matters using LLMs.

Package hierarchy (modules may import from any above):
* prompt
* manager
"""

from __future__ import annotations

from .manager import Dual1To1Manager
from .prompt import Dual1To1Prompt

__all__ = [
    "Dual1To1Manager",
    "Dual1To1Prompt",
]
