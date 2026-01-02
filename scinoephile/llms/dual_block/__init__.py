#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to dual track / block matters using LLMs."""

from __future__ import annotations

from .manager import DualBlockManager
from .processor import DualBlockProcessor
from .prompt import DualBlockPrompt

__all__ = [
    "DualBlockManager",
    "DualBlockProcessor",
    "DualBlockPrompt",
]
