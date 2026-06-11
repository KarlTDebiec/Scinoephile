#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of project packaging metadata."""

from __future__ import annotations

import tomllib
from pathlib import Path


def test_web_dependencies_are_optional():
    """Test web UI dependencies are grouped in the web extra."""
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    dependencies = pyproject["project"]["dependencies"]
    optional_dependencies = pyproject["project"]["optional-dependencies"]

    assert not any(dependency.startswith("flask") for dependency in dependencies)
    assert any(
        dependency.startswith("flask") for dependency in optional_dependencies["web"]
    )
