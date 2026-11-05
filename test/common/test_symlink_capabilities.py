#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of capability-aware symbolic link setup."""

from __future__ import annotations

from errno import EACCES, EEXIST, EINVAL, EIO, ENOENT, ENOSYS, ENOTSUP, EPERM
from pathlib import Path
from unittest.mock import patch

from common_test_support import create_symlink_or_skip
from pytest import MonkeyPatch, mark, raises, skip


@mark.parametrize("target_is_directory", [False, True])
def test_create_symlink_or_skip_preserves_creation_arguments(
    tmp_path: Path, target_is_directory: bool
):
    """Pass file and directory links through to the platform without changing targets.

    Arguments:
        tmp_path: directory for the hypothetical link and target
        target_is_directory: whether the link points to a directory
    """
    symlink_path = tmp_path / "link"
    target_path = tmp_path / "missing-target"
    with patch.object(Path, "symlink_to") as mock_create:
        create_symlink_or_skip(
            symlink_path, target_path, target_is_directory=target_is_directory
        )
    mock_create.assert_called_once_with(
        target_path, target_is_directory=target_is_directory
    )


@mark.parametrize("error_number", [EACCES, EEXIST, EINVAL, EIO, ENOENT, EPERM])
def test_create_symlink_or_skip_propagates_filesystem_errors(
    tmp_path: Path, error_number: int
):
    """Keep invalid setup, access failures, and I/O errors visible as test failures.

    Arguments:
        tmp_path: directory for the hypothetical link and target
        error_number: ordinary filesystem failure that must not cause a skip
    """
    error = OSError(error_number, "link setup failed")
    with patch.object(Path, "symlink_to", side_effect=error):
        with raises(OSError) as excinfo:
            create_symlink_or_skip(tmp_path / "link", tmp_path / "target")
    assert excinfo.value is error


@mark.parametrize(
    "error",
    [
        NotImplementedError(),
        OSError(ENOSYS, "unsupported"),
        OSError(ENOTSUP, "unsupported"),
    ],
)
def test_create_symlink_or_skip_skips_unsupported_operation(
    tmp_path: Path, error: Exception
):
    """Skip when the runtime or filesystem explicitly lacks symbolic link support.

    Arguments:
        tmp_path: directory for the hypothetical link and target
        error: capability failure raised by the platform
    """
    with patch.object(Path, "symlink_to", side_effect=error):
        with raises(skip.Exception, match="[Ss]ymbolic link creation"):
            create_symlink_or_skip(tmp_path / "link", tmp_path / "target")


@mark.parametrize("winerror", [50, 1314])
def test_create_symlink_or_skip_skips_windows_capability_errors(
    tmp_path: Path, monkeypatch: MonkeyPatch, winerror: int
):
    """Skip explicit Windows unsupported-filesystem and privilege failures.

    Arguments:
        tmp_path: directory for the hypothetical link and target
        monkeypatch: fixture providing Windows error details on every test platform
        winerror: native Windows capability error code
    """
    error = OSError(EACCES, "Windows symbolic link capability unavailable")
    monkeypatch.setattr(error, "winerror", winerror, raising=False)
    with patch.object(Path, "symlink_to", side_effect=error):
        with raises(skip.Exception, match="Symbolic link creation is unavailable"):
            create_symlink_or_skip(tmp_path / "link", tmp_path / "target")
