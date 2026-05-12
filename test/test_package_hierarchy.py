#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of package dependency hierarchy."""

from __future__ import annotations

import ast
from pathlib import Path


def test_core_image_media_lang_hierarchy():
    """Test packages only import from same or lower hierarchy levels."""
    package_levels = {
        "core": 0,
        "image": 1,
        "media": 2,
        "lang": 3,
    }
    violations = []
    root_dir_path = Path(__file__).parents[1] / "scinoephile"
    for file_path in root_dir_path.rglob("*.py"):
        source_package_name = file_path.relative_to(root_dir_path).parts[0]
        if source_package_name not in package_levels:
            continue
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            modules = []
            if isinstance(node, ast.ImportFrom) and node.module is not None:
                modules.append(node.module)
                lineno = node.lineno
            elif isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
                lineno = node.lineno
            else:
                continue
            for module in modules:
                if not module.startswith("scinoephile."):
                    continue
                imported_package_name = module.split(".")[1]
                if imported_package_name not in package_levels:
                    continue
                if (
                    package_levels[imported_package_name]
                    > package_levels[source_package_name]
                ):
                    violations.append(
                        f"{file_path.relative_to(root_dir_path.parents[0])}:"
                        f"{lineno}: {source_package_name} -> "
                        f"{imported_package_name} via {module}"
                    )

    assert violations == []
