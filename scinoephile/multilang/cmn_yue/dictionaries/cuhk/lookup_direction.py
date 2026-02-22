#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Lookup-direction enum for CUHK dictionary queries."""

from __future__ import annotations

from enum import StrEnum

__all__ = [
    "LookupDirection",
]


class LookupDirection(StrEnum):
    """Lookup direction for CUHK dictionary queries."""

    MANDARIN_TO_CANTONESE = "mandarin_to_cantonese"
    CANTONESE_TO_MANDARIN = "cantonese_to_mandarin"
