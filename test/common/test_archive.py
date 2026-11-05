#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for portable ZIP member path validation."""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest
from common.archive import ZipMemberPaths


def test_normalization_and_shared_directories():
    """Normalize redundant separators while allowing files to share directories."""
    paths = ZipMemberPaths()
    assert paths.add("./nested//image.one.png") == PurePosixPath("nested/image.one.png")
    assert paths.add("nested/image.two.png") == PurePosixPath("nested/image.two.png")


@pytest.mark.parametrize(
    ("first", "second"),
    [
        ("a.png", "a.png"),
        ("a.png", "A.PNG"),
        ("a.png", "./a.png"),
        ("a", "a/b.png"),
        ("a/b.png", "a"),
        ("A", "a/b.png"),
    ],
)
def test_member_collisions(first: str, second: str):
    """Reject duplicate files and conflicts between files and directories.

    Arguments:
        first: initial member name
        second: conflicting member name
    """
    paths = ZipMemberPaths()
    paths.add(first)
    with pytest.raises(ValueError, match="Conflicting ZIP member"):
        paths.add(second)


@pytest.mark.parametrize(
    "member_name",
    [
        "",
        ".",
        "../escape",
        "a/../escape",
        "/absolute",
        "C:/drive",
        "a\\b",
        "a\x00b",
        "a:stream",
        "CON.png",
        "nested/NUL",
        "name.",
        "name ",
        "a?b",
    ],
)
def test_unsafe_member_names(member_name: str):
    """Reject traversal and names that alias other files on supported platforms.

    Arguments:
        member_name: unsafe file member name
    """
    with pytest.raises(ValueError, match="Unsafe ZIP member"):
        ZipMemberPaths().add(member_name)
