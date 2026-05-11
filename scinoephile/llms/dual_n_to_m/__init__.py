#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to dual n to m transforms using LLMs."""

from __future__ import annotations

from .manager import DualNToMManager
from .processor import DualNToMProcessor
from .prompt import DualNToMPrompt

__all__ = [
    "DualNToMManager",
    "DualNToMProcessor",
    "DualNToMPrompt",
]
