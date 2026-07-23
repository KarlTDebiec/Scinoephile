#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.file.open_atomic_text_file."""

from __future__ import annotations

from pathlib import Path

from pytest import raises

from scinoephile.common.file import open_atomic_text_file


def test_open_atomic_text_file_replaces_output_on_success(tmp_path: Path):
    """Test output is replaced only after the context exits successfully."""
    output_path = tmp_path / "output.txt"
    output_path.write_text("original", encoding="utf-8")

    with open_atomic_text_file(output_path) as temp_file:
        temp_file.write("replacement")
        assert output_path.read_text(encoding="utf-8") == "original"

    assert output_path.read_text(encoding="utf-8") == "replacement"
    assert list(tmp_path.glob(".output.txt.*.tmp")) == []


def test_open_atomic_text_file_preserves_output_on_failure(tmp_path: Path):
    """Test failed writes preserve output and remove the temporary file."""
    output_path = tmp_path / "output.txt"
    output_path.write_text("original", encoding="utf-8")

    with raises(OSError, match="write failed"):
        with open_atomic_text_file(output_path) as temp_file:
            temp_file.write("incomplete")
            raise OSError("write failed")

    assert output_path.read_text(encoding="utf-8") == "original"
    assert list(tmp_path.glob(".output.txt.*.tmp")) == []
