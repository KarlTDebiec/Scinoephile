#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to dual 2 to 2 matters using LLMs."""

from __future__ import annotations

from .manager import Dual2To2Manager
from .prompt import Dual2To2Prompt

__all__ = [
    "Dual2To2Manager",
    "Dual2To2Prompt",
]
