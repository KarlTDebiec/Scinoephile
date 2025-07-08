#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code.

Code within this module may import only from scinoephile.common.

Many functions herein follow the naming convention:
    get_(english|hanzi|cantonese|mandarin)_(character|text|[series])_(description)
"""

from __future__ import annotations

from scinoephile.core.block import Block
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.series import Series
from scinoephile.core.subtitle import Subtitle

__all__ = [
    "Block",
    "ScinoephileError",
    "Series",
    "Subtitle",
]
