#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test the placement of CLI localization mappings."""

from __future__ import annotations

import ast
from collections.abc import Iterator

from scinoephile.common import package_root
from test.helpers.files import get_python_files


def test_cli_localizations_use_module_constants():
    """Test CLI classes assign or merge named module-level localization mappings."""
    violations = []
    file_paths = [
        file_path
        for dir_name in ("cli", "common/cli", "core/cli")
        for file_path in get_python_files(package_root / dir_name)
    ]
    for file_path in file_paths:
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        module_names = {target.id for target, _ in _named_assignments(tree.body)}
        module_names.update(
            alias.asname or alias.name
            for node in tree.body
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        )
        for cls in tree.body:
            if not isinstance(cls, ast.ClassDef):
                continue
            for target, value in _named_assignments(cls.body):
                if target.id != "localizations":
                    continue
                sources = [value]
                if (
                    isinstance(value, ast.Call)
                    and isinstance(value.func, ast.Name)
                    and value.func.id == "merge_localizations"
                    and value.args
                    and not value.keywords
                ):
                    sources = value.args
                if all(
                    isinstance(source, ast.Name)
                    and source.id.isupper()
                    and source.id.endswith("_LOCALIZATIONS")
                    and source.id in module_names
                    for source in sources
                ):
                    continue
                violations.append(
                    f"{file_path.relative_to(package_root.parent)}:{target.lineno}: "
                    f"{cls.name}.localizations must assign or merge module-level "
                    "*_LOCALIZATIONS constants"
                )

    assert not violations, "\n".join(violations)


def _named_assignments(
    statements: list[ast.stmt],
) -> Iterator[tuple[ast.Name, ast.expr]]:
    """Get simple assignments with values from a module or class body.

    Arguments:
        statements: statements in the body to inspect
    Yields:
        named assignment target and its value
    """
    for node in statements:
        match node:
            case ast.Assign(targets=targets, value=value):
                for target in targets:
                    if isinstance(target, ast.Name):
                        yield target, value
            case ast.AnnAssign(target=ast.Name() as target, value=ast.expr() as value):
                yield target, value
