#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to dual n to n matters using LLMs.

Package hierarchy (modules may import from any above):
* prompt
* manager
* processor
"""

from __future__ import annotations

from .manager import DualNToNManager
from .processor import DualNToNProcessor
from .prompt import DualNToNPrompt

__all__ = [
    "DualNToNManager",
    "DualNToNProcessor",
    "DualNToNPrompt",
]
