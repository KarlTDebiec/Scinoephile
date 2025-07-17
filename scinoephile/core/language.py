# Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Language constants used throughout scinoephile."""

from __future__ import annotations

from typing import Literal

type Language = Literal[
    "English",
    "Simplified Chinese",
    "Traditional Chinese",
    "yue",
    "zhongwen",
    "yuewen",
]
"""Supported languages."""

__all__ = ["Language"]
