#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

"""Tests of TypedDict field documentation."""

from __future__ import annotations

import ast
from pathlib import Path

from scinoephile.common import package_root
from test.helpers.files import get_python_files


def test_typed_dict_field_documentation_violations_are_detected():
    """Test undocumented TypedDict fields are detected."""
    tree = ast.parse(
        '''
class Example(TypedDict):
    """Example payload."""

    documented: str
    """Documented field."""

    undocumented: int
'''
    )

    violations = _get_typed_dict_field_documentation_violations(
        file_path=Path("sample.py"), tree=tree
    )

    assert violations == [
        "sample.py:8: TypedDict field Example.undocumented lacks documentation"
    ]


def test_typed_dict_fields_are_documented():
    """Test TypedDict fields have attribute docstrings."""
    violations: list[str] = []
    for file_path in get_python_files(package_root.parent):
        tree = ast.parse(
            file_path.read_text(encoding="utf-8"), filename=file_path.as_posix()
        )
        violations.extend(
            _get_typed_dict_field_documentation_violations(
                file_path=file_path.relative_to(package_root.parent), tree=tree
            )
        )

    assert not violations, "Document TypedDict fields:\n" + "\n".join(violations)


def _get_typed_dict_field_documentation_violations(
    file_path: Path, tree: ast.Module
) -> list[str]:
    """Get undocumented TypedDict fields from a parsed Python file.

    Arguments:
        file_path: source file path
        tree: parsed Python module
    Returns:
        formatted documentation violations
    """
    violations = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        if not any(
            (isinstance(base, ast.Name) and base.id == "TypedDict")
            or (isinstance(base, ast.Attribute) and base.attr == "TypedDict")
            for base in node.bases
        ):
            continue

        for statement_idx, statement in enumerate(node.body):
            if not isinstance(statement, ast.AnnAssign) or not isinstance(
                statement.target, ast.Name
            ):
                continue
            next_statement_idx = statement_idx + 1
            next_statement = None
            if next_statement_idx < len(node.body):
                next_statement = node.body[next_statement_idx]
            has_docstring = (
                isinstance(next_statement, ast.Expr)
                and isinstance(next_statement.value, ast.Constant)
                and isinstance(next_statement.value.value, str)
            )
            if not has_docstring:
                violations.append(
                    f"{file_path}:{statement.lineno}: TypedDict field "
                    f"{node.name}.{statement.target.id} lacks documentation"
                )
    return violations
