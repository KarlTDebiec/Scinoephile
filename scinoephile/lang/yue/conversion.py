#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to written Cantonese text conversion."""

from __future__ import annotations

from hkscs_unicode_converter.converter import convert_string

from scinoephile.core import UnsupportedCharacterError
from scinoephile.core.text import RE_PRIVATE_USE_AREA_BMP

__all__ = [
    "get_yue_converted",
]


def get_yue_converted(text: str) -> str:
    """Convert Cantonese text from HKSCS private-use characters to Unicode.

    Arguments:
        text: text to convert
    Returns:
        converted text
    Raises:
        UnsupportedCharacterError: if private-use area characters remain
    """
    converted = convert_string(text)
    if RE_PRIVATE_USE_AREA_BMP.search(converted):
        raise UnsupportedCharacterError(
            f"Unsupported Hanzi after HKSCS normalization: {text} -> {converted}"
        )
    return converted
