#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for core text helpers."""

from __future__ import annotations

import pytest

from scinoephile.core import ScinoephileError
from scinoephile.core.text import get_char_type, sanitize_text


def test_get_char_type_handles_unnamed_control_char() -> None:
    """Unnamed control characters raise a ScinoephileError."""
    with pytest.raises(ScinoephileError, match="<unnamed>"):
        get_char_type("\x00")


def test_sanitize_text_replaces_control_chars() -> None:
    """Control characters that are not text whitespace are replaced."""
    assert sanitize_text("好呀！\x00\x00你") == "好呀！  你"


def test_sanitize_text_preserves_text_whitespace() -> None:
    """Line and tab whitespace are preserved."""
    assert sanitize_text("one\ntwo\tthree\r") == "one\ntwo\tthree\r"
