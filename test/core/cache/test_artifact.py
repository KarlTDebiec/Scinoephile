#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cache artifact filesystem operations."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core.cache.artifact import remove_cache_artifact
from test.helpers import parametrize


@parametrize("artifact_type", ["directory", "symlink", "broken_symlink"])
def test_remove_cache_artifact_handles_wrong_filesystem_types(
    tmp_path: Path, artifact_type: str
):
    """Test malformed cache artifacts are removed without following links.

    Arguments:
        tmp_path: temporary directory provided by pytest
        artifact_type: malformed artifact type to create
    """
    artifact_path = tmp_path / "entry.json"
    target_path = tmp_path / "target.json"
    if artifact_type == "directory":
        artifact_path.mkdir()
        (artifact_path / "nested.txt").write_text("nested", encoding="utf-8")
    elif artifact_type == "symlink":
        target_path.write_text("target", encoding="utf-8")
        artifact_path.symlink_to(target_path)
    else:
        artifact_path.symlink_to(target_path)

    assert remove_cache_artifact(artifact_path)
    assert not artifact_path.exists()
    assert not artifact_path.is_symlink()
    if artifact_type == "symlink":
        assert target_path.read_text(encoding="utf-8") == "target"

    assert not remove_cache_artifact(artifact_path)
