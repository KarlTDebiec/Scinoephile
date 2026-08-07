#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared diagnostics for LLM text-preservation validation."""

from __future__ import annotations

from typing import TypedDict

__all__ = ["TextMismatchDetails", "get_text_mismatch_details"]


class TextMismatchDetails(TypedDict):
    """Details of the first mismatch between two strings."""

    offset: int
    """Zero-based mismatch character offset."""
    expected_character: str
    """Expected character and Unicode code point, or end-of-text marker."""
    received_character: str
    """Received character and Unicode code point, or end-of-text marker."""
    expected_context: str
    """Expected text surrounding the mismatch."""
    received_context: str
    """Received text surrounding the mismatch."""


def get_text_mismatch_details(
    expected: str, received: str, *, context_radius: int = 12
) -> TextMismatchDetails:
    """Get actionable details of the first mismatch between two strings.

    Arguments:
        expected: expected text
        received: received text
        context_radius: characters to show on either side of the mismatch
    Returns:
        mismatch offset, characters, and nearby context
    """
    offset = next(
        (
            index
            for index, (expected_char, received_char) in enumerate(
                zip(expected, received, strict=False)
            )
            if expected_char != received_char
        ),
        min(len(expected), len(received)),
    )
    start = max(0, offset - context_radius)
    expected_end = min(len(expected), offset + context_radius + 1)
    received_end = min(len(received), offset + context_radius + 1)
    return {
        "offset": offset,
        "expected_character": _format_character(expected, offset),
        "received_character": _format_character(received, offset),
        "expected_context": repr(expected[start:expected_end]),
        "received_context": repr(received[start:received_end]),
    }


def _format_character(text: str, offset: int) -> str:
    """Format one character with its Unicode code point."""
    if offset >= len(text):
        return "<end of text>"
    character = text[offset]
    return f"{character!r} (U+{ord(character):04X})"
