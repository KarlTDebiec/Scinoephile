#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of repository style requirements."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

import pytest

from scinoephile.common import package_root
from test.helpers.files import get_python_files

DOCSTRING_BASELINE_PATH = Path(__file__).with_name("docstring_violations.txt")
"""Path to the checked-in docstring violation baseline."""

PERCENT_INTERPOLATION_RE = re.compile(
    r"(?<!%)%(?!%)(?:\([^)]+\))?[#0\- +]*(?:\d+|\*)?"
    r"(?:\.(?:\d+|\*))?[hlL]?[diouxXeEfFgGcrsa]"
)
"""Regex matching percent-style string interpolation placeholders."""

SECTION_HEADER_RE = re.compile(r"[A-Za-z][A-Za-z ]*:")
"""Regex matching a standalone Google-style docstring section header."""


@dataclass(frozen=True)
class DocstringViolation:
    """Docstring structure style violation."""

    file_path: Path
    """Repository-relative source file path."""

    line_number: int
    """Source line number."""

    qualified_name: str
    """Qualified name of the violating definition."""

    rule_id: str
    """Stable rule identifier."""

    message: str
    """Violation message."""

    @property
    def fingerprint(self) -> str:
        """Stable fingerprint used by the checked-in baseline."""
        return f"{self.file_path.as_posix()}|{self.qualified_name}|{self.rule_id}"

    def __str__(self) -> str:
        """Format the violation for assertion output.

        Returns:
            formatted violation
        """
        return (
            f"{self.file_path.as_posix()}:{self.line_number}: "
            f"{self.qualified_name}: {self.message}"
        )


@dataclass(frozen=True)
class _DocstringSection:
    """Parsed top-level docstring section."""

    name: str
    """Section name without its trailing colon."""

    header_line_index: int
    """Zero-based header line index within the cleaned docstring."""

    content_lines: tuple[str, ...]
    """Lines between this header and the next top-level header."""


class _DocstringVisitor(ast.NodeVisitor):
    """Collect docstring violations while tracking qualified names."""

    def __init__(self, file_path: Path):
        """Initialize the visitor.

        Arguments:
            file_path: repository-relative source file path
        """
        self.file_path = file_path
        self.qualified_names: list[str] = []
        self.violations: list[DocstringViolation] = []

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visit an async function definition.

        Arguments:
            node: async function definition
        """
        self._visit_callable(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit a class definition.

        Arguments:
            node: class definition
        """
        qualified_name = ".".join((*self.qualified_names, node.name))
        if ast.get_docstring(node, clean=True) is None:
            self._add_violation(
                line_number=node.lineno,
                message="lacks a docstring",
                qualified_name=qualified_name,
                rule_id="missing-docstring",
            )

        self.qualified_names.append(node.name)
        self.generic_visit(node)
        self.qualified_names.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit a function definition.

        Arguments:
            node: function definition
        """
        self._visit_callable(node)

    def visit_Module(self, node: ast.Module):
        """Visit a module.

        Arguments:
            node: parsed module
        """
        if node.body and ast.get_docstring(node, clean=True) is None:
            self._add_violation(
                line_number=1,
                message="lacks a docstring",
                qualified_name="<module>",
                rule_id="missing-docstring",
            )
        self.generic_visit(node)

    def _add_violation(
        self, *, line_number: int, message: str, qualified_name: str, rule_id: str
    ):
        """Add a violation for the current file.

        Arguments:
            line_number: source line number
            message: violation message
            qualified_name: qualified definition name
            rule_id: stable rule identifier
        """
        self.violations.append(
            DocstringViolation(
                file_path=self.file_path,
                line_number=line_number,
                message=message,
                qualified_name=qualified_name,
                rule_id=rule_id,
            )
        )

    def _check_callable(
        self,
        *,
        decorator_names: set[str],
        docstring: str,
        is_after_model_validator: bool,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        qualified_name: str,
    ):
        """Check the structure of a callable's docstring.

        Arguments:
            decorator_names: terminal names of the callable's decorators
            docstring: cleaned callable docstring
            is_after_model_validator: whether this is an after model validator
            node: callable definition
            qualified_name: qualified callable name
        """
        sections = _get_docstring_sections(docstring)
        argument_sections = [
            section for section in sections if section.name == "Arguments"
        ]
        args_sections = [section for section in sections if section.name == "Args"]
        expected_argument_names = _get_callable_parameter_names(node)

        if args_sections:
            self._add_violation(
                line_number=node.lineno,
                message="uses `Args:`; use `Arguments:`",
                qualified_name=qualified_name,
                rule_id="arguments-section-name",
            )
        if expected_argument_names and not argument_sections and not args_sections:
            self._add_violation(
                line_number=node.lineno,
                message="requires an `Arguments:` section",
                qualified_name=qualified_name,
                rule_id="missing-arguments",
            )
        if argument_sections:
            documented_argument_names = [
                argument_name
                for section in argument_sections
                for argument_name in _get_documented_argument_names(section)
            ]
            if documented_argument_names != expected_argument_names:
                self._add_violation(
                    line_number=node.lineno,
                    message=(
                        f"documents arguments {documented_argument_names!r}; "
                        f"signature requires {expected_argument_names!r}"
                    ),
                    qualified_name=qualified_name,
                    rule_id="arguments-mismatch",
                )

        has_value_return = _has_value_return(
            node, is_abstract_method="abstractmethod" in decorator_names
        )
        has_returns_section = any(section.name == "Returns" for section in sections)
        is_property_getter = bool(
            {"cached_property", "getter", "property"} & decorator_names
        )
        if not is_property_getter and not is_after_model_validator:
            if has_value_return and not has_returns_section:
                self._add_violation(
                    line_number=node.lineno,
                    message="returns a value but lacks a `Returns:` section",
                    qualified_name=qualified_name,
                    rule_id="missing-returns",
                )
            if not has_value_return and has_returns_section:
                self._add_violation(
                    line_number=node.lineno,
                    message="has a `Returns:` section but does not return a value",
                    qualified_name=qualified_name,
                    rule_id="unexpected-returns",
                )

        for section, next_section in zip(sections, sections[1:], strict=False):
            if (
                section.name == "Arguments"
                and next_section.name == "Returns"
                and section.content_lines
                and not section.content_lines[-1].strip()
            ):
                self._add_violation(
                    line_number=node.lineno,
                    message=(
                        "has a blank line between adjacent `Arguments:` and "
                        "`Returns:` sections"
                    ),
                    qualified_name=qualified_name,
                    rule_id="section-spacing",
                )

    def _visit_callable(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        """Visit and check a function or method definition.

        Arguments:
            node: callable definition
        """
        decorator_names = {
            decorator_name
            for decorator in node.decorator_list
            if (decorator_name := _get_decorator_terminal_name(decorator)) is not None
        }
        definition_name = node.name
        for accessor_name in ("deleter", "getter", "setter"):
            if accessor_name in decorator_names:
                definition_name = f"{definition_name}.{accessor_name}"
                break
        qualified_name = ".".join((*self.qualified_names, definition_name))
        is_after_model_validator = any(
            _is_after_model_validator(decorator) for decorator in node.decorator_list
        )

        if "overload" not in decorator_names:
            docstring = ast.get_docstring(node, clean=True)
            if docstring is None:
                self._add_violation(
                    line_number=node.lineno,
                    message="lacks a docstring",
                    qualified_name=qualified_name,
                    rule_id="missing-docstring",
                )
            else:
                self._check_callable(
                    decorator_names=decorator_names,
                    docstring=docstring,
                    is_after_model_validator=is_after_model_validator,
                    node=node,
                    qualified_name=qualified_name,
                )

        self.qualified_names.append(definition_name)
        self.generic_visit(node)
        self.qualified_names.pop()


class _ValueReturnVisitor(ast.NodeVisitor):
    """Detect value returns without entering nested lexical scopes."""

    def __init__(self):
        """Initialize the visitor."""
        self.has_value_return = False

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Skip a nested async function.

        Arguments:
            node: nested async function definition
        """

    def visit_ClassDef(self, node: ast.ClassDef):
        """Skip a nested class.

        Arguments:
            node: nested class definition
        """

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Skip a nested function.

        Arguments:
            node: nested function definition
        """

    def visit_Lambda(self, node: ast.Lambda):
        """Skip a nested lambda.

        Arguments:
            node: nested lambda
        """

    def visit_Return(self, node: ast.Return):
        """Record a value-returning return statement.

        Arguments:
            node: return statement
        """
        if node.value is None:
            return
        if isinstance(node.value, ast.Constant) and node.value.value is None:
            return
        self.has_value_return = True


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


def test_documented_docstrings_have_no_violations():
    """Test documented modules, classes, and functions have no violations."""
    violations = _get_sample_docstring_violations(
        '''
class Example:
    """Example class."""

    def echo(self, value):
        """Echo a value.

        Arguments:
            value: value to echo
        Returns:
            echoed value
        """
        return value
'''
    )

    assert not violations


def test_docstring_abstract_methods_require_returns_section():
    """Test value-returning abstract method contracts require `Returns:`."""
    violations = _get_sample_docstring_violations(
        '''
class Interface:
    """Example interface."""

    @abstractmethod
    def value(self, token: str) -> int | None:
        """Get a value.

        Arguments:
            token: token text
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def no_value(self) -> None:
        """Perform an operation."""
        raise NotImplementedError()
'''
    )

    assert [
        (violation.qualified_name, violation.rule_id) for violation in violations
    ] == [("Interface.value", "missing-returns")]


def test_docstring_after_model_validators_need_no_returns_section():
    """Test after model validators may include or omit `Returns:`."""
    violations = _get_sample_docstring_violations(
        '''
class Example:
    """Example model."""

    @model_validator(mode="after")
    def validate_direct(self):
        """Validate the direct model."""
        return self

    @pydantic.model_validator(mode="after")
    def validate_qualified(self):
        """Validate the qualified model.

        Returns:
            validated model
        """
        return self
'''
    )

    assert not violations


@pytest.mark.parametrize(
    "argument_lines",
    [
        "        first: first value",
        "        first: first value\n"
        "        first: duplicate\n"
        "        second: second value",
        "        second: second value\n        first: first value",
        "        first: first value\n"
        "        second: second value\n"
        "        stale: stale value",
    ],
)
def test_docstring_argument_mismatches_are_detected(argument_lines: str):
    """Test missing, duplicate, reordered, and stale entries are detected.

    Arguments:
        argument_lines: malformed argument documentation lines
    """
    violations = _get_sample_docstring_violations(
        f'''
def sample(first, second):
    """Sample function.

    Arguments:
{argument_lines}
    """
'''
    )

    assert [violation.rule_id for violation in violations] == ["arguments-mismatch"]


def test_docstring_arguments_section_name_is_enforced():
    """Test `Args:` is rejected as a substitute for `Arguments:`."""
    violations = _get_sample_docstring_violations(
        '''
def sample(value):
    """Sample function.

    Args:
        value: sample value
    """
'''
    )

    assert [violation.rule_id for violation in violations] == ["arguments-section-name"]


def test_docstring_complex_arguments_are_checked_in_signature_order():
    """Test all parameter kinds use exact ordered `Arguments:` entries."""
    violations = _get_sample_docstring_violations(
        '''
def sample(positional_only, /, positional, *args, keyword_only, **kwargs):
    """Sample function.

    Arguments:
        positional_only: positional-only value
        positional: positional value
        *args: variadic positional values
        keyword_only: keyword-only value
        **kwargs: variadic keyword values
    """
'''
    )

    assert not violations


def test_docstring_header_mentions_in_prose_are_not_sections():
    """Test section header mentions in prose do not satisfy requirements."""
    violations = _get_sample_docstring_violations(
        '''
def sample(value):
    """Mention Arguments: and Returns: in prose without real sections."""
    return value
'''
    )

    assert [violation.rule_id for violation in violations] == [
        "missing-arguments",
        "missing-returns",
    ]


def test_docstring_missing_definitions_are_detected():
    """Test missing definition docstrings are detected with qualified names."""
    violations = _get_sample_docstring_violations(
        '''
class MissingClass:
    pass

def missing_function():
    pass

def outer():
    """Documented outer function."""

    def nested():
        pass

class Properties:
    """Example properties."""

    @property
    def value(self):
        return 1

    @value.setter
    def value(self, value):
        pass
'''
    )

    assert [
        (violation.qualified_name, violation.rule_id) for violation in violations
    ] == [
        ("MissingClass", "missing-docstring"),
        ("missing_function", "missing-docstring"),
        ("outer.nested", "missing-docstring"),
        ("Properties.value", "missing-docstring"),
        ("Properties.value.setter", "missing-docstring"),
    ]


def test_docstring_missing_module_is_detected():
    """Test a nonempty undocumented module is detected."""
    assert not _get_sample_docstring_violations("", include_module_docstring=False)

    violations = _get_sample_docstring_violations(
        "value = 1", include_module_docstring=False
    )

    assert [
        (violation.qualified_name, violation.rule_id) for violation in violations
    ] == [("<module>", "missing-docstring")]


@pytest.mark.parametrize("return_statement", ["return", "return None"])
def test_docstring_non_value_returns_reject_returns_section(return_statement: str):
    """Test bare and literal-None returns reject `Returns:` documentation.

    Arguments:
        return_statement: non-value return statement
    """
    violations = _get_sample_docstring_violations(
        f'''
def sample():
    """Sample function.

    Returns:
        nonexistent value
    """
    {return_statement}
'''
    )

    assert [violation.rule_id for violation in violations] == ["unexpected-returns"]


@pytest.mark.parametrize(
    ("mode", "signature", "argument_lines", "return_expression"),
    [
        ("before", "cls, data", "            data: raw model data", "data"),
        (
            "wrap",
            "cls, data, handler",
            "            data: raw model data\n"
            "            handler: inner validation handler",
            "handler(data)",
        ),
    ],
)
def test_docstring_other_model_validators_require_returns_section(
    mode: str, signature: str, argument_lines: str, return_expression: str
):
    """Test before and wrap model validators still require `Returns:`.

    Arguments:
        mode: model validator mode
        signature: validator signature source
        argument_lines: validator argument documentation source
        return_expression: validator return expression source
    """
    violations = _get_sample_docstring_violations(
        f'''
class Example:
    """Example model."""

    @model_validator(mode="{mode}")
    @classmethod
    def validate({signature}):
        """Validate model input.

        Arguments:
{argument_lines}
        """
        return {return_expression}
'''
    )

    assert [violation.rule_id for violation in violations] == ["missing-returns"]


def test_docstring_only_self_and_cls_need_no_arguments_section():
    """Test `self` and `cls` do not require `Arguments:` documentation."""
    violations = _get_sample_docstring_violations(
        '''
class Example:
    """Example class."""

    def instance_method(self):
        """Run an instance method."""

    @classmethod
    def class_method(cls):
        """Run a class method."""
'''
    )

    assert not violations


def test_docstring_overload_stubs_are_exempt():
    """Test direct and qualified overload stubs are exempt."""
    violations = _get_sample_docstring_violations(
        """
from typing import overload

@overload
def parse(value: str) -> str: ...

@typing.overload
def load(value: int) -> int: ...
"""
    )

    assert not violations


def test_docstring_typed_interface_stubs_require_returns_section():
    """Test value-returning typed interface stubs require `Returns:`."""
    violations = _get_sample_docstring_violations(
        '''
class Interface:
    """Example interface."""

    def value(self, token: str) -> int | None:
        """Get a value.

        Arguments:
            token: token text
        """
        ...

    def no_value(self) -> None:
        """Perform an operation."""
        ...
'''
    )

    assert [
        (violation.qualified_name, violation.rule_id) for violation in violations
    ] == [("Interface.value", "missing-returns")]


def test_docstring_properties_need_no_returns_section():
    """Test property and cached-property getters need no `Returns:` section."""
    violations = _get_sample_docstring_violations(
        '''
class Example:
    """Example class."""

    @property
    def direct(self):
        """Direct value."""
        return 1

    @functools.cached_property
    def cached(self):
        """Cached value."""
        return 2

    @property
    def legacy(self):
        """Legacy value.

        Returns:
            legacy value
        """
        return 3
'''
    )

    assert not violations


def test_docstring_return_detection_stops_at_nested_scopes():
    """Test nested function and class returns do not affect their parent."""
    violations = _get_sample_docstring_violations(
        '''
def outer():
    """Outer function."""

    def inner():
        """Inner function.

        Returns:
            inner value
        """
        return 1

    class Inner:
        """Inner class."""

        def method(self):
            """Return a value.

            Returns:
                method value
            """
            return 2
'''
    )

    assert not violations


def test_docstring_returns_are_required_for_async_functions():
    """Test value-returning async functions require `Returns:`."""
    violations = _get_sample_docstring_violations(
        '''
async def sample():
    """Sample async function."""
    return 1
'''
    )

    assert [violation.rule_id for violation in violations] == ["missing-returns"]


def test_docstring_returns_are_required_for_value_returns():
    """Test ordinary value-returning functions require `Returns:`."""
    violations = _get_sample_docstring_violations(
        '''
def sample():
    """Sample function."""
    return 1
'''
    )

    assert [violation.rule_id for violation in violations] == ["missing-returns"]


def test_docstring_section_spacing_is_enforced():
    """Test adjacent `Arguments:` and `Returns:` reject a blank line."""
    violations = _get_sample_docstring_violations(
        '''
def sample(value):
    """Sample function.

    Arguments:
        value: sample value

    Returns:
        sample value
    """
    return value
'''
    )

    assert [violation.rule_id for violation in violations] == ["section-spacing"]


def test_docstring_violation_format():
    """Test docstring violations have stable fingerprints and useful output."""
    violation = DocstringViolation(
        file_path=Path("sample.py"),
        line_number=3,
        message="lacks a docstring",
        qualified_name="Example.method",
        rule_id="missing-docstring",
    )

    assert violation.fingerprint == ("sample.py|Example.method|missing-docstring")
    assert str(violation) == "sample.py:3: Example.method: lacks a docstring"


def test_python_docstrings_follow_repository_structure():
    """Test Python docstring violations match the exact checked-in baseline."""
    violations: list[DocstringViolation] = []
    for file_path in get_python_files(package_root.parent):
        tree = ast.parse(
            file_path.read_text(encoding="utf-8"), filename=file_path.as_posix()
        )
        violations.extend(
            get_docstring_violations(
                file_path=file_path.relative_to(package_root.parent), tree=tree
            )
        )

    violations_by_fingerprint = {
        violation.fingerprint: violation for violation in violations
    }
    actual_fingerprints = set(violations_by_fingerprint)
    expected_fingerprints = set(
        DOCSTRING_BASELINE_PATH.read_text(encoding="utf-8").splitlines()
    )
    unexpected_fingerprints = sorted(actual_fingerprints - expected_fingerprints)
    resolved_fingerprints = sorted(expected_fingerprints - actual_fingerprints)

    failure_sections = []
    if unexpected_fingerprints:
        failure_sections.append(
            "Unexpected docstring violations (fix these, do not add them to the "
            "baseline):\n"
            + "\n".join(
                str(violations_by_fingerprint[fingerprint])
                for fingerprint in unexpected_fingerprints
            )
        )
    if resolved_fingerprints:
        failure_sections.append(
            "Resolved docstring violations (remove these from the baseline):\n"
            + "\n".join(resolved_fingerprints)
        )
    assert not failure_sections, "\n\n".join(failure_sections)


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


def get_docstring_violations(
    file_path: Path, tree: ast.Module
) -> list[DocstringViolation]:
    """Get docstring structure violations in a parsed Python file.

    Arguments:
        file_path: repository-relative source file path
        tree: parsed Python module
    Returns:
        docstring structure violations
    """
    visitor = _DocstringVisitor(file_path)
    visitor.visit(tree)
    return visitor.violations


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


def _get_callable_parameter_names(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[str]:
    """Get documented parameter names in signature order.

    Arguments:
        node: callable definition
    Returns:
        parameter names excluding `self` and `cls`
    """
    parameter_names = [
        argument.arg for argument in (*node.args.posonlyargs, *node.args.args)
    ]
    if node.args.vararg is not None:
        parameter_names.append(f"*{node.args.vararg.arg}")
    parameter_names.extend(argument.arg for argument in node.args.kwonlyargs)
    if node.args.kwarg is not None:
        parameter_names.append(f"**{node.args.kwarg.arg}")
    return [name for name in parameter_names if name not in {"cls", "self"}]


def _is_after_model_validator(decorator: ast.expr) -> bool:
    """Check whether a decorator is an after Pydantic model validator.

    Arguments:
        decorator: decorator expression
    Returns:
        whether the decorator is `@model_validator(mode="after")`
    """
    if not isinstance(decorator, ast.Call):
        return False
    if _get_decorator_terminal_name(decorator) != "model_validator":
        return False
    return any(
        keyword.arg == "mode"
        and isinstance(keyword.value, ast.Constant)
        and keyword.value.value == "after"
        for keyword in decorator.keywords
    )


def _get_decorator_terminal_name(decorator: ast.expr) -> str | None:
    """Get the terminal name of a decorator expression.

    Arguments:
        decorator: decorator expression
    Returns:
        terminal decorator name, if recognizable
    """
    if isinstance(decorator, ast.Call):
        decorator = decorator.func
    if isinstance(decorator, ast.Name):
        return decorator.id
    if isinstance(decorator, ast.Attribute):
        return decorator.attr
    return None


def _get_docstring_sections(docstring: str) -> list[_DocstringSection]:
    """Parse top-level sections from a cleaned docstring.

    Arguments:
        docstring: cleaned docstring
    Returns:
        parsed sections in source order
    """
    lines = docstring.splitlines()
    header_line_indexes = [
        line_index
        for line_index, line in enumerate(lines)
        if line
        and not line[0].isspace()
        and SECTION_HEADER_RE.fullmatch(line.strip()) is not None
    ]
    sections = []
    for header_index_idx, header_line_index in enumerate(header_line_indexes):
        next_header_index_idx = header_index_idx + 1
        content_end_index = len(lines)
        if next_header_index_idx < len(header_line_indexes):
            content_end_index = header_line_indexes[next_header_index_idx]
        sections.append(
            _DocstringSection(
                name=lines[header_line_index].strip()[:-1],
                header_line_index=header_line_index,
                content_lines=tuple(lines[header_line_index + 1 : content_end_index]),
            )
        )
    return sections


def _get_documented_argument_names(section: _DocstringSection) -> list[str]:
    """Get direct entries from an `Arguments:` section.

    Arguments:
        section: parsed arguments section
    Returns:
        documented argument names in source order
    """
    candidates: list[tuple[int, str]] = []
    for line in section.content_lines:
        stripped_line = line.lstrip()
        if not stripped_line:
            continue
        name, separator, _ = stripped_line.partition(":")
        bare_name = name.removeprefix("**").removeprefix("*")
        if not separator or not bare_name.isidentifier():
            continue
        indentation = len(line) - len(stripped_line)
        candidates.append((indentation, name))
    if not candidates:
        return []
    entry_indentation = min(indentation for indentation, _ in candidates)
    return [
        name for indentation, name in candidates if indentation == entry_indentation
    ]


def _get_sample_docstring_violations(
    source: str, *, include_module_docstring: bool = True
) -> list[DocstringViolation]:
    """Get docstring violations from sample source.

    Arguments:
        source: sample Python source
        include_module_docstring: whether to prepend a module docstring
    Returns:
        detected docstring violations
    """
    if include_module_docstring:
        source = f'"""Sample module."""\n{source}'
    return get_docstring_violations(file_path=Path("sample.py"), tree=ast.parse(source))


def _has_value_return(
    node: ast.FunctionDef | ast.AsyncFunctionDef, *, is_abstract_method: bool
) -> bool:
    """Check whether a callable's body or typed stub contract returns a value.

    Arguments:
        node: callable definition
        is_abstract_method: whether the callable is an abstract method contract
    Returns:
        whether the callable contains an own-body value return or typed value stub
    """
    statements = node.body
    if ast.get_docstring(node, clean=False) is not None:
        statements = statements[1:]
    is_ellipsis_stub = (
        len(statements) == 1
        and isinstance(statements[0], ast.Expr)
        and isinstance(statements[0].value, ast.Constant)
        and statements[0].value.value is Ellipsis
    )
    return_annotation_is_none = (
        isinstance(node.returns, ast.Constant) and node.returns.value is None
    ) or (isinstance(node.returns, ast.Name) and node.returns.id == "None")
    has_value_return_annotation = (
        node.returns is not None and not return_annotation_is_none
    )
    if has_value_return_annotation and (is_abstract_method or is_ellipsis_stub):
        return True

    visitor = _ValueReturnVisitor()
    for statement in node.body:
        visitor.visit(statement)
    return visitor.has_value_return
