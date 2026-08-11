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
class StyleViolation:
    """Repository style violation."""

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


def test_module_export_violations_are_detected():
    """Test invalid module export declarations are detected."""
    tree = ast.parse(
        '''
class Exported:
    """Exported class."""


class Missing:
    """Missing class."""


_internal = object()

__all__ = ["Exported", "Exported", "_internal", "Unknown"]
'''
    )

    violations = get_module_export_violations(
        file_path=package_root.parent / "sample.py", tree=tree
    )

    assert [violation.message for violation in violations] == [
        "`__all__` contains duplicate names: Exported",
        "`__all__` contains internal names: _internal",
        "`__all__` contains unbound names: Unknown",
        "`__all__` omits public definitions: Missing",
    ]

    missing_declaration_violations = get_module_export_violations(
        file_path=package_root.parent / "sample.py",
        tree=ast.parse("class PublicClass:\n    pass"),
    )

    assert [violation.message for violation in missing_declaration_violations] == [
        "public definitions require `__all__`: PublicClass"
    ]


def test_percent_interpolation_arguments_are_detected():
    """Test logging-style percent interpolation arguments are detected."""
    tree = ast.parse('logger.warning("hello %s", name)')

    violations = get_string_interpolation_violations(
        file_path=package_root.parent / "sample.py", tree=tree
    )

    assert [violation.message for violation in violations] == [
        "uses `%` interpolation arguments; prefer f-strings"
    ]


def test_private_import_violations_are_detected():
    """Test imports of names private to another module are detected."""
    tree = ast.parse(
        """from .ten import TenVadProvider as _provider
from .ten import _TenVadProvider
from .pyannote import (
    _PyannoteVadProvider,
)
"""
    )

    violations = get_private_import_violations(
        file_path=package_root.parent / "sample.py", tree=tree
    )

    assert [violation.message for violation in violations] == [
        "imports private name `_TenVadProvider` from `.ten`",
        "imports private name `_PyannoteVadProvider` from `.pyannote`",
    ]


def test_python_module_exports_are_declared():
    """Test package modules declare valid public exports."""
    violations: list[StyleViolation] = []
    for file_path in get_python_files(package_root):
        tree = ast.parse(
            file_path.read_text(encoding="utf-8"), filename=file_path.as_posix()
        )
        violations.extend(get_module_export_violations(file_path=file_path, tree=tree))

    assert not violations, "Declare valid module exports:\n" + "\n".join(
        str(violation) for violation in violations
    )


def test_python_sources_do_not_import_private_names():
    """Test Python sources do not import names private to another module."""
    violations: list[StyleViolation] = []
    for file_path in get_python_files(package_root.parent):
        tree = ast.parse(
            file_path.read_text(encoding="utf-8"), filename=file_path.as_posix()
        )
        violations.extend(get_private_import_violations(file_path=file_path, tree=tree))

    assert not violations, "Do not import private names from other modules:\n" + (
        "\n".join(str(violation) for violation in violations)
    )


def test_python_sources_do_not_use_percent_string_interpolation():
    """Test Python sources do not use percent-style string interpolation."""
    violations: list[StyleViolation] = []
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

    violations = get_typed_dict_field_documentation_violations(
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
            get_typed_dict_field_documentation_violations(
                file_path=file_path.relative_to(package_root.parent), tree=tree
            )
        )

    assert not violations, "Document TypedDict fields:\n" + "\n".join(violations)


def get_module_export_violations(
    file_path: Path, tree: ast.Module
) -> list[StyleViolation]:
    """Get module export style violations from a parsed Python file.

    Arguments:
        file_path: source file path
        tree: parsed Python module
    Returns:
        module export style violations
    """
    public_definitions = {
        name: node.lineno
        for node in tree.body
        if (name := _get_module_definition_name(node)) is not None
        and not name.startswith("_")
    }

    all_assignments: list[ast.Assign | ast.AnnAssign | ast.AugAssign] = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in node.targets
        ):
            all_assignments.append(node)
        elif (
            isinstance(node, (ast.AnnAssign, ast.AugAssign))
            and isinstance(node.target, ast.Name)
            and node.target.id == "__all__"
        ):
            all_assignments.append(node)
    if not all_assignments:
        if not public_definitions:
            return []
        return [
            StyleViolation(
                file_path=file_path,
                line_number=min(public_definitions.values()),
                message=(
                    "public definitions require `__all__`: "
                    + ", ".join(sorted(public_definitions))
                ),
            )
        ]

    first_assignment = all_assignments[0]
    if len(all_assignments) > 1:
        return [
            StyleViolation(
                file_path=file_path,
                line_number=first_assignment.lineno,
                message="`__all__` must be assigned exactly once",
            )
        ]

    exports = None
    if (
        not isinstance(first_assignment, ast.AugAssign)
        and first_assignment.value is not None
    ):
        exports = _get_literal_module_exports(first_assignment.value)
    if exports is None:
        return [
            StyleViolation(
                file_path=file_path,
                line_number=first_assignment.lineno,
                message="`__all__` must be a list or tuple of string literals",
            )
        ]

    if not exports:
        return [
            StyleViolation(
                file_path=file_path,
                line_number=first_assignment.lineno,
                message="do not declare an empty `__all__`",
            )
        ]

    bound_names = _get_module_bound_names(tree)
    violations: list[StyleViolation] = []
    duplicate_names = sorted(
        export for export in set(exports) if exports.count(export) > 1
    )
    internal_names = sorted(export for export in exports if export.startswith("_"))
    unbound_names = sorted(set(exports) - bound_names)
    missing_names = sorted(public_definitions.keys() - set(exports))
    messages = [
        (duplicate_names, "`__all__` contains duplicate names"),
        (internal_names, "`__all__` contains internal names"),
        (unbound_names, "`__all__` contains unbound names"),
        (missing_names, "`__all__` omits public definitions"),
    ]
    for names, message in messages:
        if not names:
            continue
        violations.append(
            StyleViolation(
                file_path=file_path,
                line_number=first_assignment.lineno,
                message=f"{message}: {', '.join(names)}",
            )
        )
    return violations


def get_private_import_violations(
    file_path: Path, tree: ast.Module
) -> list[StyleViolation]:
    """Get imports of names private to another module.

    Arguments:
        file_path: source file path
        tree: parsed Python module
    Returns:
        private import style violations
    """
    violations: list[StyleViolation] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        source_module = f"{'.' * node.level}{node.module or ''}"
        for alias in node.names:
            if not alias.name.startswith("_"):
                continue
            violations.append(
                StyleViolation(
                    file_path=file_path,
                    line_number=alias.lineno,
                    message=(
                        f"imports private name `{alias.name}` from `{source_module}`"
                    ),
                )
            )
    return violations


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
    file_path: Path, tree: ast.Module
) -> list[StyleViolation]:
    """Get string interpolation style violations in a parsed Python file.

    Arguments:
        file_path: source file path
        tree: parsed Python module
    Returns:
        string interpolation style violations
    """
    violations: list[StyleViolation] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and is_percent_interpolation_binop(node):
            violations.append(
                StyleViolation(
                    file_path=file_path,
                    line_number=node.lineno,
                    message="uses `%` interpolation; prefer f-strings",
                )
            )
        if isinstance(node, ast.Call) and is_percent_interpolation_call(node):
            violations.append(
                StyleViolation(
                    file_path=file_path,
                    line_number=node.lineno,
                    message="uses `%` interpolation arguments; prefer f-strings",
                )
            )
    return violations


def get_typed_dict_field_documentation_violations(
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


def _get_assignment_target_names(target: ast.expr) -> set[str]:
    """Get names bound by an assignment target.

    Arguments:
        target: assignment target
    Returns:
        bound names
    """
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, (ast.List, ast.Tuple)):
        return {
            name
            for element in target.elts
            for name in _get_assignment_target_names(element)
        }
    return set()


def _get_literal_module_exports(value: ast.expr) -> list[str] | None:
    """Get literal string exports from an `__all__` value.

    Arguments:
        value: assigned `__all__` value
    Returns:
        literal string exports, or None if the value is not a literal sequence
    """
    if not isinstance(value, (ast.List, ast.Tuple)):
        return None

    exports: list[str] = []
    for element in value.elts:
        if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
            return None
        exports.append(element.value)
    return exports


def _get_module_bound_names(tree: ast.Module) -> set[str]:
    """Get names bound directly in a parsed Python module.

    Arguments:
        tree: parsed Python module
    Returns:
        module-level bound names
    """
    bound_names: set[str] = set()
    for node in tree.body:
        definition_name = _get_module_definition_name(node)
        if definition_name is not None:
            bound_names.add(definition_name)
        elif isinstance(node, ast.Import):
            bound_names.update(
                alias.asname or alias.name.partition(".")[0] for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            bound_names.update(
                alias.asname or alias.name for alias in node.names if alias.name != "*"
            )
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                bound_names.update(_get_assignment_target_names(target))
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
            bound_names.update(_get_assignment_target_names(node.target))
    return bound_names


def _get_module_definition_name(node: ast.stmt) -> str | None:
    """Get the name defined by a module-level statement.

    Arguments:
        node: module-level statement
    Returns:
        defined name, if the statement is a definition
    """
    if isinstance(node, (ast.AsyncFunctionDef, ast.ClassDef, ast.FunctionDef)):
        return node.name
    if isinstance(node, ast.TypeAlias) and isinstance(node.name, ast.Name):
        return node.name.id
    return None
