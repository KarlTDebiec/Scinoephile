#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code.

Module hierarchy (within scinoephile):
This module may import from: common

Package hierarchy (within core, modules may import from any above):
* exceptions / text
* subtitles
* timing / pairs
* synchronization
"""

from __future__ import annotations

from .exceptions import ScinoephileError

__all__ = [
    "ScinoephileError",
]
