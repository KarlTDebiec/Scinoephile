#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

"""Support for enforcing repository docstring structure."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "DocstringViolation",
    "get_docstring_violations",
    "get_sample_docstring_violations",
]

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
        self.scope_kinds: list[str] = []
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

        is_typed_dict = any(
            (isinstance(base, ast.Name) and base.id == "TypedDict")
            or (isinstance(base, ast.Attribute) and base.attr == "TypedDict")
            for base in node.bases
        )
        if is_typed_dict:
            for statement_index, statement in enumerate(node.body):
                if not isinstance(statement, ast.AnnAssign) or not isinstance(
                    statement.target, ast.Name
                ):
                    continue
                next_statement_index = statement_index + 1
                next_statement = None
                if next_statement_index < len(node.body):
                    next_statement = node.body[next_statement_index]
                has_docstring = (
                    isinstance(next_statement, ast.Expr)
                    and isinstance(next_statement.value, ast.Constant)
                    and isinstance(next_statement.value.value, str)
                )
                if not has_docstring:
                    self._add_violation(
                        line_number=statement.lineno,
                        message="TypedDict field lacks documentation",
                        qualified_name=f"{qualified_name}.{statement.target.id}",
                        rule_id="missing-typed-dict-field-docstring",
                    )

        self.qualified_names.append(node.name)
        self.scope_kinds.append("class")
        self.generic_visit(node)
        self.scope_kinds.pop()
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
        is_method: bool,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        qualified_name: str,
    ):
        """Check the structure of a callable's docstring.

        Arguments:
            decorator_names: terminal names of the callable's decorators
            docstring: cleaned callable docstring
            is_after_model_validator: whether this is an after model validator
            is_method: whether the callable is defined directly on a class
            node: callable definition
            qualified_name: qualified callable name
        """
        sections = _get_docstring_sections(docstring)
        argument_sections = [
            section for section in sections if section.name == "Arguments"
        ]
        args_sections = [section for section in sections if section.name == "Args"]
        expected_argument_names = _get_callable_parameter_names(
            node, is_method=is_method
        )

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

        has_value_return, has_yield, has_explicit_raise = _get_callable_flow(
            node, is_abstract_method="abstractmethod" in decorator_names
        )
        has_returns_section = any(section.name == "Returns" for section in sections)
        has_yields_section = any(section.name == "Yields" for section in sections)
        has_raises_section = any(section.name == "Raises" for section in sections)
        has_summary_return_exemption = (
            bool({"cached_property", "fixture", "getter", "property"} & decorator_names)
            or is_after_model_validator
        )
        if not has_summary_return_exemption:
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
        if has_yield and not has_yields_section:
            self._add_violation(
                line_number=node.lineno,
                message="contains a yield but lacks a `Yields:` section",
                qualified_name=qualified_name,
                rule_id="missing-yields",
            )
        if not has_yield and has_yields_section:
            self._add_violation(
                line_number=node.lineno,
                message="has a `Yields:` section but contains no yield",
                qualified_name=qualified_name,
                rule_id="unexpected-yields",
            )
        if has_explicit_raise and not has_raises_section:
            self._add_violation(
                line_number=node.lineno,
                message="contains an explicit raise but lacks a `Raises:` section",
                qualified_name=qualified_name,
                rule_id="missing-raises",
            )

        compact_section_names = {"Arguments", "Raises", "Returns", "Yields"}
        for section, next_section in zip(sections, sections[1:], strict=False):
            if (
                section.name in compact_section_names
                and next_section.name in compact_section_names
                and section.content_lines
                and not section.content_lines[-1].strip()
            ):
                self._add_violation(
                    line_number=node.lineno,
                    message=(
                        "has a blank line between adjacent "
                        f"`{section.name}:` and `{next_section.name}:` sections"
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
        is_method = bool(self.scope_kinds and self.scope_kinds[-1] == "class")
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
                    is_method=is_method,
                    node=node,
                    qualified_name=qualified_name,
                )

        self.qualified_names.append(definition_name)
        self.scope_kinds.append("callable")
        self.generic_visit(node)
        self.scope_kinds.pop()
        self.qualified_names.pop()


class _CallableFlowVisitor(ast.NodeVisitor):
    """Detect returns, yields, and raises without entering nested lexical scopes."""

    def __init__(self):
        """Initialize the visitor."""
        self.has_explicit_raise = False
        self.has_value_return = False
        self.has_yield = False

    def generic_visit(self, node: ast.AST):
        """Visit child nodes unless the node opens a nested lexical scope.

        Arguments:
            node: AST node
        """
        if isinstance(
            node, (ast.AsyncFunctionDef, ast.ClassDef, ast.FunctionDef, ast.Lambda)
        ):
            return
        super().generic_visit(node)

    def visit_Raise(self, node: ast.Raise):
        """Record an explicit raise statement.

        Arguments:
            node: raise statement
        """
        self.has_explicit_raise = True

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

    def visit_Yield(self, node: ast.Yield):
        """Record a yield expression.

        Arguments:
            node: yield expression
        """
        self.has_yield = True

    def visit_YieldFrom(self, node: ast.YieldFrom):
        """Record a delegated yield expression.

        Arguments:
            node: delegated yield expression
        """
        self.has_yield = True


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


def get_sample_docstring_violations(
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


def _get_callable_parameter_names(
    node: ast.FunctionDef | ast.AsyncFunctionDef, *, is_method: bool
) -> list[str]:
    """Get documented parameter names in signature order.

    Arguments:
        node: callable definition
        is_method: whether the callable is defined directly on a class
    Returns:
        parameter names excluding an implicit method receiver
    """
    parameter_names = [
        argument.arg for argument in (*node.args.posonlyargs, *node.args.args)
    ]
    if is_method and parameter_names and parameter_names[0] in {"cls", "self"}:
        parameter_names.pop(0)
    if node.args.vararg is not None:
        parameter_names.append(f"*{node.args.vararg.arg}")
    parameter_names.extend(argument.arg for argument in node.args.kwonlyargs)
    if node.args.kwarg is not None:
        parameter_names.append(f"**{node.args.kwarg.arg}")
    return parameter_names


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
    content_end_indexes = header_line_indexes[1:]
    if header_line_indexes:
        content_end_indexes.append(len(lines))
    for header_line_index, content_end_index in zip(
        header_line_indexes, content_end_indexes, strict=True
    ):
        sections.append(
            _DocstringSection(
                name=lines[header_line_index].strip()[:-1],
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


def _get_callable_flow(
    node: ast.FunctionDef | ast.AsyncFunctionDef, *, is_abstract_method: bool
) -> tuple[bool, bool, bool]:
    """Check whether a callable returns, yields, or explicitly raises.

    Arguments:
        node: callable definition
        is_abstract_method: whether the callable is an abstract method contract
    Returns:
        whether the callable returns, yields, and explicitly raises
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
    raised_exception = None
    if len(statements) == 1 and isinstance(statements[0], ast.Raise):
        raised_exception = statements[0].exc
        if isinstance(raised_exception, ast.Call):
            raised_exception = raised_exception.func
    is_not_implemented_stub = (
        isinstance(raised_exception, ast.Name)
        and raised_exception.id == "NotImplementedError"
    )
    return_annotation_is_none = (
        isinstance(node.returns, ast.Constant) and node.returns.value is None
    ) or (isinstance(node.returns, ast.Name) and node.returns.id == "None")
    has_value_return_annotation = (
        node.returns is not None and not return_annotation_is_none
    )
    has_value_return = has_value_return_annotation and (
        is_abstract_method or is_ellipsis_stub or is_not_implemented_stub
    )

    visitor = _CallableFlowVisitor()
    for statement in node.body:
        visitor.visit(statement)
    has_value_return = has_value_return or visitor.has_value_return
    has_explicit_raise = visitor.has_explicit_raise and not (
        is_abstract_method and is_not_implemented_stub
    )
    return has_value_return, visitor.has_yield, has_explicit_raise
