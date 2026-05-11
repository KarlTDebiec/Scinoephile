#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Media helper functions."""

from __future__ import annotations

__all__ = ["normalize_language"]


def normalize_language(language: str) -> str:
    """Normalize a stream language tag.

    Arguments:
        language: language tag
    Returns:
        normalized language tag
    """
    parts = language.split("-")
    normalized_parts = [parts[0].lower()]
    for part in parts[1:]:
        if len(part) == 4 and part.isalpha():
            normalized_parts.append(part.title())
        elif part.lower() == "unknown":
            normalized_parts.append("Unknown")
        else:
            normalized_parts.append(part)
    return "-".join(normalized_parts)
