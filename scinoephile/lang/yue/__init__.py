#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Cantonese (yue) text.

Package hierarchy (modules may import from any above):
* prompts
* romanization
"""

from __future__ import annotations

from .romanization import get_yue_romanized

__all__ = [
    "get_yue_romanized",
]
