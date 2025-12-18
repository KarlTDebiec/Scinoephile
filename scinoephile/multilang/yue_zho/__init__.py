#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 粤文/中文 text."""

from __future__ import annotations

from .review import get_yue_vs_zho_reviewed
from .translation import get_yue_from_zho_translated

__all__ = [
    "get_yue_vs_zho_reviewed",
    "get_yue_from_zho_translated",
]
