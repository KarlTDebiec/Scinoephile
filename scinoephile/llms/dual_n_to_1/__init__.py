#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to dual n to 1 matters using LLMs.

Package hierarchy (modules may import from any above):
* prompt
* manager
"""

from __future__ import annotations

from .manager import DualNTo1Manager
from .prompt import DualNTo1Prompt

__all__ = [
    "DualNTo1Manager",
    "DualNTo1Prompt",
]
