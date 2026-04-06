#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Lookup-direction enum for dictionary queries."""

from __future__ import annotations

from enum import StrEnum

__all__ = [
    "LookupDirection",
]


class LookupDirection(StrEnum):
    """Lookup direction for dictionary queries."""

    CMN_TO_YUE = "cmn_to_yue"
    YUE_TO_CMN = "yue_to_cmn"
