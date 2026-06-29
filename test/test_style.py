#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of repository style requirements."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

from scinoephile.common import package_root

EXCLUDED_DIR_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "local",
}
"""Directory names excluded from recursive source scans."""

PERCENT_INTERPOLATION_RE = re.compile(
    r"(?<!%)%(?!%)(?:\([^)]+\))?[#0\- +]*(?:\d+|\*)?"
    r"(?:\.(?:\d+|\*))?[hlL]?[diouxXeEfFgGcrsa]"
)
"""Regex matching percent-style string interpolation placeholders."""


@dataclass(frozen=True)
class StringInterpolationViolation:
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

    violations = get_string_interpolation_violations(
        file_path=package_root.parent / "sample.py",
        tree=tree,
    )

    assert [violation.message for violation in violations] == [
        "uses `%` interpolation arguments; prefer f-strings"
    ]


def test_python_sources_do_not_use_percent_string_interpolation():
    """Test Python sources do not use percent-style string interpolation."""
    violations: list[StringInterpolationViolation] = []
    for file_path in get_python_files(package_root.parent):
        tree = ast.parse(
            file_path.read_text(encoding="utf-8"), filename=file_path.as_posix()
        )
        violations.extend(
            get_string_interpolation_violations(file_path=file_path, tree=tree)
        )

    assert not violations, (
        "Use f-strings instead of percent-style interpolation:\n"
        + "\n".join(str(violation) for violation in violations)
    )


def get_python_files(target_dir_path: Path) -> list[Path]:
    """Get Python files under a target directory.

    Arguments:
        target_dir_path: directory path to scan
    Returns:
        sorted Python file paths
    """
    return sorted(
        file_path
        for file_path in target_dir_path.rglob("*.py")
        if not is_excluded_path(file_path, target_dir_path)
    )


def get_string_interpolation_violations(
    file_path: Path,
    tree: ast.Module,
) -> list[StringInterpolationViolation]:
    """Get string interpolation style violations in a parsed Python file.

    Arguments:
        file_path: source file path
        tree: parsed Python module
    Returns:
        string interpolation style violations
    """
    violations: list[StringInterpolationViolation] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and is_percent_interpolation_binop(node):
            violations.append(
                StringInterpolationViolation(
                    file_path=file_path,
                    line_number=node.lineno,
                    message="uses `%` interpolation; prefer f-strings",
                )
            )
        if isinstance(node, ast.Call) and is_percent_interpolation_call(node):
            violations.append(
                StringInterpolationViolation(
                    file_path=file_path,
                    line_number=node.lineno,
                    message="uses `%` interpolation arguments; prefer f-strings",
                )
            )
    return violations


def is_excluded_path(file_path: Path, target_dir_path: Path) -> bool:
    """Check whether a discovered file falls under an excluded directory.

    Arguments:
        file_path: discovered file path
        target_dir_path: recursive scan root
    Returns:
        whether the file should be omitted from the scan
    """
    relative_file_path = file_path.relative_to(target_dir_path)
    return any(part in EXCLUDED_DIR_NAMES for part in relative_file_path.parts)


def is_percent_interpolation_binop(node: ast.BinOp) -> bool:
    """Check whether an AST node uses binary percent string interpolation.

    Arguments:
        node: AST node
    Returns:
        whether the node uses binary percent string interpolation
    """
    return (
        isinstance(node, ast.BinOp)
        and isinstance(node.op, ast.Mod)
        and is_string_with_percent_interpolation(node.left)
    )


def is_percent_interpolation_call(node: ast.Call) -> bool:
    """Check whether a call uses percent-style string interpolation arguments.

    Arguments:
        node: AST node
    Returns:
        whether the call has a percent-format template followed by values
    """
    if len(node.args) < 2:
        return False
    return is_string_with_percent_interpolation(node.args[0])


def is_string_with_percent_interpolation(node: ast.AST) -> bool:
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
