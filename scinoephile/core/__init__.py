#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code.

Package hierarchy (modules may import from any above):
* exceptions / text
* llms
* blockwise / pairwise / many_to_many_blockwise
"""

from __future__ import annotations

from .exceptions import ScinoephileError

__all__ = [
    "ScinoephileError",
]
