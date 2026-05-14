#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code.

This module may import from: common

Hierarchy within module (lower may import from higher):
* dictionaries / exceptions / ml / optimization / paths
* cache / llms / subtitles / text
* cli / pairs / timing
* media / synchronization
"""

from __future__ import annotations

from .exceptions import ScinoephileError, UnsupportedCharacterError

__all__ = [
    "ScinoephileError",
    "UnsupportedCharacterError",
]
