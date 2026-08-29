#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

"""Tests of string interpolation style."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

from scinoephile.common import package_root
from test.helpers.files import get_python_files

PERCENT_INTERPOLATION_RE = re.compile(
    r"(?<!%)%(?!%)(?:\([^)]+\))?[#0\- +]*(?:\d+|\*)?"
    r"(?:\.(?:\d+|\*))?[hlL]?[diouxXeEfFgGcrsa]"
)
"""Regex matching percent-style string interpolation placeholders."""


@dataclass(frozen=True)
class _StringInterpolationViolation:
    """String interpolation style violation."""

    file_path: Path
    """Source file path."""

    line_number: int
    """Source line number."""

    message: str
    """Violation message."""

    def __str__(self) -> str:
        """Format the violation for assertion output.

        Returns:
            formatted violation
        """
        return (
            f"{self.file_path.relative_to(package_root.parent)}:"
            f"{self.line_number}: {self.message}"
        )


def test_percent_interpolation_arguments_are_detected():
    """Test logging-style percent interpolation arguments are detected."""
    tree = ast.parse('logger.warning("hello %s", name)')

    violations = _get_string_interpolation_violations(
        file_path=package_root.parent / "sample.py", tree=tree
    )

    assert [violation.message for violation in violations] == [
        "uses `%` interpolation arguments; prefer f-strings"
    ]


def test_python_sources_do_not_use_percent_string_interpolation():
    """Test Python sources do not use percent-style string interpolation."""
    violations: list[_StringInterpolationViolation] = []
    for file_path in get_python_files(package_root.parent):
        tree = ast.parse(
            file_path.read_text(encoding="utf-8"), filename=file_path.as_posix()
        )
        violations.extend(
            _get_string_interpolation_violations(file_path=file_path, tree=tree)
        )

    assert not violations, (
        "Use f-strings instead of percent-style interpolation:\n"
        + "\n".join(str(violation) for violation in violations)
    )


def _get_string_interpolation_violations(
    file_path: Path, tree: ast.Module
) -> list[_StringInterpolationViolation]:
    """Get string interpolation style violations in a parsed Python file.

    Arguments:
        file_path: source file path
        tree: parsed Python module
    Returns:
        string interpolation style violations
    """
    violations: list[_StringInterpolationViolation] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and _is_percent_interpolation_binop(node):
            violations.append(
                _StringInterpolationViolation(
                    file_path=file_path,
                    line_number=node.lineno,
                    message="uses `%` interpolation; prefer f-strings",
                )
            )
        if isinstance(node, ast.Call) and _is_percent_interpolation_call(node):
            violations.append(
                _StringInterpolationViolation(
                    file_path=file_path,
                    line_number=node.lineno,
                    message="uses `%` interpolation arguments; prefer f-strings",
                )
            )
    return violations


def _is_percent_interpolation_binop(node: ast.BinOp) -> bool:
    """Check whether an AST node uses binary percent string interpolation.

    Arguments:
        node: AST node
    Returns:
        whether the node uses binary percent string interpolation
    """
    return (
        isinstance(node, ast.BinOp)
        and isinstance(node.op, ast.Mod)
        and _is_string_with_percent_interpolation(node.left)
    )


def _is_percent_interpolation_call(node: ast.Call) -> bool:
    """Check whether a call uses percent-style string interpolation arguments.

    Arguments:
        node: AST node
    Returns:
        whether the call has a percent-format template followed by values
    """
    if len(node.args) < 2:
        return False
    return _is_string_with_percent_interpolation(node.args[0])


def _is_string_with_percent_interpolation(node: ast.AST) -> bool:
    """Check whether an AST node is a string with percent interpolation.

    Arguments:
        node: AST node
    Returns:
        whether the node is a string with percent interpolation
    """
    if not isinstance(node, ast.Constant):
        return False
    if not isinstance(node.value, str):
        return False
    return PERCENT_INTERPOLATION_RE.search(node.value) is not None
