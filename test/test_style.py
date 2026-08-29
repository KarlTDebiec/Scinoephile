#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of repository style requirements."""

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


@dataclass(frozen=True)
class VariadicKeywordAnnotationViolation:
    """Variadic keyword argument annotation violation."""

    file_path: Path
    """Source file path."""

    line_number: int
    """Source line number."""

    callable_name: str
    """Name of the callable containing the annotation."""

    argument_name: str
    """Name of the variadic keyword argument."""

    def __str__(self) -> str:
        """Format the violation for assertion output.

        Returns:
            formatted violation
        """
        return (
            f"{self.file_path}:{self.line_number}: {self.callable_name} uses "
            f"**{self.argument_name}: object"
        )


def test_percent_interpolation_arguments_are_detected():
    """Test logging-style percent interpolation arguments are detected."""
    tree = ast.parse('logger.warning("hello %s", name)')

    violations = get_string_interpolation_violations(
        file_path=package_root.parent / "sample.py", tree=tree
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


def test_variadic_keyword_annotations_accept_intentional_types():
    """Test intentional variadic keyword annotations are accepted."""
    tree = ast.parse(
        """
def accepts_any(**kwargs: Any):
    pass


def accepts_unpack(**kwargs: Unpack[Options]):
    pass


def accepts_narrow_type(**kwargs: str):
    pass
"""
    )

    violations = get_variadic_keyword_annotation_violations(
        file_path=Path("sample.py"), tree=tree
    )

    assert not violations


def test_variadic_keyword_object_annotations_are_detected():
    """Test object-annotated variadic keyword arguments are detected."""
    tree = ast.parse(
        """
def ordinary(**kwargs: object):
    pass


def outer():
    def nested(**options: object):
        pass


async def asynchronous(**values: object):
    pass


def qualified(**values: builtins.object):
    pass


def quoted(**values: "object"):
    pass
"""
    )

    violations = get_variadic_keyword_annotation_violations(
        file_path=Path("sample.py"), tree=tree
    )

    assert [str(violation) for violation in violations] == [
        "sample.py:2: ordinary uses **kwargs: object",
        "sample.py:7: nested uses **options: object",
        "sample.py:11: asynchronous uses **values: object",
        "sample.py:15: qualified uses **values: object",
        "sample.py:19: quoted uses **values: object",
    ]


def test_variadic_keyword_object_annotations_are_not_used():
    """Test Python sources intentionally annotate variadic keyword arguments."""
    violations: list[VariadicKeywordAnnotationViolation] = []
    for file_path in get_python_files(package_root.parent):
        tree = ast.parse(
            file_path.read_text(encoding="utf-8"), filename=file_path.as_posix()
        )
        violations.extend(
            get_variadic_keyword_annotation_violations(
                file_path=file_path.relative_to(package_root.parent), tree=tree
            )
        )

    assert not violations, (
        "Use Any, Unpack[TypedDict], or a narrower type for variadic keyword "
        "arguments:\n" + "\n".join(str(violation) for violation in violations)
    )


def get_string_interpolation_violations(
    file_path: Path, tree: ast.Module
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


def get_variadic_keyword_annotation_violations(
    file_path: Path, tree: ast.Module
) -> list[VariadicKeywordAnnotationViolation]:
    """Get object-annotated variadic keyword arguments in a parsed Python file.

    Arguments:
        file_path: source file path
        tree: parsed Python module
    Returns:
        variadic keyword argument annotation violations
    """
    violations = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            continue
        keyword_argument = node.args.kwarg
        if keyword_argument is None:
            continue
        annotation = keyword_argument.annotation
        is_object_annotation = (
            (isinstance(annotation, ast.Name) and annotation.id == "object")
            or (
                isinstance(annotation, ast.Attribute)
                and isinstance(annotation.value, ast.Name)
                and annotation.value.id == "builtins"
                and annotation.attr == "object"
            )
            or (
                isinstance(annotation, ast.Constant)
                and isinstance(annotation.value, str)
                and annotation.value.strip() in {"builtins.object", "object"}
            )
        )
        if not is_object_annotation:
            continue
        violations.append(
            VariadicKeywordAnnotationViolation(
                file_path=file_path,
                line_number=keyword_argument.lineno,
                callable_name=node.name,
                argument_name=keyword_argument.arg,
            )
        )
    violations.sort(key=lambda violation: violation.line_number)
    return violations


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
