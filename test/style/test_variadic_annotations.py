#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

"""Tests of variadic argument annotations."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from scinoephile.common import package_root
from test.helpers.files import get_python_files


@dataclass(frozen=True)
class _VariadicAnnotationViolation:
    """Variadic argument annotation violation."""

    file_path: Path
    """Source file path."""

    line_number: int
    """Source line number."""

    callable_name: str
    """Name of the callable containing the annotation."""

    argument_name: str
    """Name of the variadic argument."""

    argument_prefix: str
    """Prefix identifying a positional or keyword variadic argument."""

    def __str__(self) -> str:
        """Format the violation for assertion output.

        Returns:
            formatted violation
        """
        return (
            f"{self.file_path}:{self.line_number}: {self.callable_name} uses "
            f"{self.argument_prefix}{self.argument_name}: object"
        )


def test_variadic_annotations_accept_intentional_types():
    """Test intentional variadic annotations are accepted."""
    tree = ast.parse(
        """
def accepts_positional_any(*args: Any):
    pass


def accepts_any(**kwargs: Any):
    pass


def accepts_unpack(**kwargs: Unpack[Options]):
    pass


def accepts_narrow_type(**kwargs: str):
    pass
"""
    )

    violations = _get_variadic_annotation_violations(
        file_path=Path("sample.py"), tree=tree
    )

    assert not violations


def test_variadic_object_annotations_are_detected():
    """Test object-annotated variadic arguments are detected."""
    tree = ast.parse(
        """
def ordinary(*args: object, **kwargs: object):
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

    violations = _get_variadic_annotation_violations(
        file_path=Path("sample.py"), tree=tree
    )

    assert [str(violation) for violation in violations] == [
        "sample.py:2: ordinary uses *args: object",
        "sample.py:2: ordinary uses **kwargs: object",
        "sample.py:7: nested uses **options: object",
        "sample.py:11: asynchronous uses **values: object",
        "sample.py:15: qualified uses **values: object",
        "sample.py:19: quoted uses **values: object",
    ]


def test_variadic_object_annotations_are_not_used():
    """Test Python sources intentionally annotate variadic arguments."""
    violations: list[_VariadicAnnotationViolation] = []
    for file_path in get_python_files(package_root.parent):
        tree = ast.parse(
            file_path.read_text(encoding="utf-8"), filename=file_path.as_posix()
        )
        violations.extend(
            _get_variadic_annotation_violations(
                file_path=file_path.relative_to(package_root.parent), tree=tree
            )
        )

    assert not violations, (
        "Use Any, Unpack[...], or a narrower type for variadic arguments:\n"
        + "\n".join(str(violation) for violation in violations)
    )


def _get_variadic_annotation_violations(
    file_path: Path, tree: ast.Module
) -> list[_VariadicAnnotationViolation]:
    """Get object-annotated variadic arguments in a parsed Python file.

    Arguments:
        file_path: source file path
        tree: parsed Python module
    Returns:
        variadic argument annotation violations
    """
    violations: list[_VariadicAnnotationViolation] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            continue
        variadic_arguments = ((node.args.vararg, "*"), (node.args.kwarg, "**"))
        for argument, argument_prefix in variadic_arguments:
            if argument is None:
                continue
            annotation = argument.annotation
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
                _VariadicAnnotationViolation(
                    file_path=file_path,
                    line_number=argument.lineno,
                    callable_name=node.name,
                    argument_name=argument.arg,
                    argument_prefix=argument_prefix,
                )
            )
    violations.sort(key=lambda violation: violation.line_number)
    return violations
