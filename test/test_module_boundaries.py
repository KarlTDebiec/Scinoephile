#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of public module boundaries."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from scinoephile.common import package_root
from test.helpers.files import get_python_files


@dataclass(frozen=True)
class ModuleBoundaryViolation:
    """Public module boundary violation."""

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

    violations = get_public_definition_export_violations(
        file_path=package_root.parent / "sample.py", tree=tree
    )

    assert [violation.message for violation in violations] == [
        "`__all__` contains duplicate names: Exported",
        "`__all__` contains internal names: _internal",
        "`__all__` contains unbound names: Unknown",
        "`__all__` omits public definitions: Missing",
    ]

    missing_declaration_violations = get_public_definition_export_violations(
        file_path=package_root.parent / "sample.py",
        tree=ast.parse("class PublicClass:\n    pass"),
    )
    assert [violation.message for violation in missing_declaration_violations] == [
        "public definitions require `__all__`: PublicClass"
    ]

    annotation_violations = get_public_definition_export_violations(
        file_path=package_root.parent / "sample.py",
        tree=ast.parse('PublicName: str\n__all__ = ["PublicName"]'),
    )
    assert [violation.message for violation in annotation_violations] == [
        "`__all__` contains unbound names: PublicName"
    ]


def test_module_export_violations_do_not_infer_assignment_intent():
    """Test assignment names are not inferred as public API."""
    violations = get_public_definition_export_violations(
        file_path=package_root.parent / "sample.py",
        tree=ast.parse("MODULE_CONSTANT = object()"),
    )

    assert violations == []


def test_private_import_violations_are_detected():
    """Test private imports are checked only for project modules."""
    tree = ast.parse(
        """from argparse import _ArgumentGroup
from external_library import _ExternalType
from scinoephile.common.argument_parsing import _ProjectHelper
from .ten import TenVadProvider as _provider
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
        "imports private name `_ProjectHelper` from "
        "`scinoephile.common.argument_parsing`",
        "imports private name `_TenVadProvider` from `.ten`",
        "imports private name `_PyannoteVadProvider` from `.pyannote`",
    ]


def test_python_public_definitions_are_exported():
    """Test package modules explicitly export public definitions."""
    violations: list[ModuleBoundaryViolation] = []
    for file_path in get_python_files(package_root):
        tree = ast.parse(
            file_path.read_text(encoding="utf-8"), filename=file_path.as_posix()
        )
        violations.extend(
            get_public_definition_export_violations(file_path=file_path, tree=tree)
        )

    assert not violations, "Declare valid module exports:\n" + "\n".join(
        str(violation) for violation in violations
    )


def test_python_sources_do_not_import_project_private_names():
    """Test Python sources do not import project-private names."""
    violations: list[ModuleBoundaryViolation] = []
    for file_path in get_python_files(package_root.parent):
        tree = ast.parse(
            file_path.read_text(encoding="utf-8"), filename=file_path.as_posix()
        )
        violations.extend(get_private_import_violations(file_path=file_path, tree=tree))

    assert not violations, "Do not import private names from project modules:\n" + (
        "\n".join(str(violation) for violation in violations)
    )


def get_private_import_violations(
    file_path: Path, tree: ast.Module
) -> list[ModuleBoundaryViolation]:
    """Get imports of names private to another project module.

    Arguments:
        file_path: source file path
        tree: parsed Python module
    Returns:
        private import style violations
    """
    violations: list[ModuleBoundaryViolation] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue

        # Relative imports are project-owned; resolve absolute imports from repo roots
        source_root_name = (node.module or "").partition(".")[0]
        source_root_path = package_root.parent / source_root_name
        if (
            node.level == 0
            and not source_root_path.is_dir()
            and not source_root_path.with_suffix(".py").is_file()
        ):
            continue

        source_module = f"{'.' * node.level}{node.module or ''}"
        for alias in node.names:
            if not alias.name.startswith("_"):
                continue
            violations.append(
                ModuleBoundaryViolation(
                    file_path=file_path,
                    line_number=alias.lineno,
                    message=(
                        f"imports private name `{alias.name}` from `{source_module}`"
                    ),
                )
            )
    return violations


def get_public_definition_export_violations(
    file_path: Path, tree: ast.Module
) -> list[ModuleBoundaryViolation]:
    """Get public definition export violations from a parsed Python file.

    Arguments:
        file_path: source file path
        tree: parsed Python module
    Returns:
        public definition export violations
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
            ModuleBoundaryViolation(
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
            ModuleBoundaryViolation(
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
            ModuleBoundaryViolation(
                file_path=file_path,
                line_number=first_assignment.lineno,
                message="`__all__` must be a list or tuple of string literals",
            )
        ]

    if not exports:
        return [
            ModuleBoundaryViolation(
                file_path=file_path,
                line_number=first_assignment.lineno,
                message="do not declare an empty `__all__`",
            )
        ]

    bound_names = _get_module_bound_names(tree)
    violations: list[ModuleBoundaryViolation] = []
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
            ModuleBoundaryViolation(
                file_path=file_path,
                line_number=first_assignment.lineno,
                message=f"{message}: {', '.join(names)}",
            )
        )
    return violations


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
        elif isinstance(node, ast.AnnAssign):
            if node.value is not None:
                bound_names.update(_get_assignment_target_names(node.target))
        elif isinstance(node, ast.AugAssign):
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
