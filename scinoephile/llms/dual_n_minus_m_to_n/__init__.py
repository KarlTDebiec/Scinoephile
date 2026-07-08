#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to dual n minus m to n matters using LLMs.

Dual n minus m to n matters take in two subtitle Series where each secondary
block has n subtitles and the corresponding primary block has n minus m
subtitles because m subtitles are missing. They process the paired blocks and
output a single completed Series.

Package hierarchy (modules may import from any above):
* prompt
* manager
* processor
"""

from __future__ import annotations

from .manager import DualNMinusMToNManager
from .processor import (
    DualNMinusMToNProcessor,
    DualNMinusMToNProcessorProcessKwargs,
)
from .prompt import DualNMinusMToNPrompt

__all__ = [
    "DualNMinusMToNManager",
    "DualNMinusMToNProcessor",
    "DualNMinusMToNProcessorProcessKwargs",
    "DualNMinusMToNPrompt",
]
