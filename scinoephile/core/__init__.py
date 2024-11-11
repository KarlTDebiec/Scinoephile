#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code for scinoephile.

Code within this module may import only from scinoephile.common.

Most functions herein follow the naming convention:
    get_(english|hanzi|cantonese_pinyin|mandarin_pinyin)_(character|text|series)_(description)
"""
from __future__ import annotations

from scinoephile.core.exceptions import ScinoephileException
from scinoephile.core.series import Series
from scinoephile.core.subtitle import Subtitle

__all__ = [
    "ScinoephileException",
    "Series",
    "Subtitle",
]
