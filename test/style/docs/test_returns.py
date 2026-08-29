#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

"""Tests of return-value documentation."""

from __future__ import annotations

import pytest

from test.style.docs.checks import get_sample_docstring_violations


def test_docstring_abstract_methods_require_returns_section():
    """Test value-returning abstract method contracts require `Returns:`."""
    violations = get_sample_docstring_violations(
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
    violations = get_sample_docstring_violations(
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


@pytest.mark.parametrize("return_statement", ["return", "return None"])
def test_docstring_non_value_returns_reject_returns_section(return_statement: str):
    """Test bare and literal-None returns reject `Returns:` documentation.

    Arguments:
        return_statement: non-value return statement
    """
    violations = get_sample_docstring_violations(
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
    violations = get_sample_docstring_violations(
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


def test_docstring_typed_interface_stubs_require_returns_section():
    """Test value-returning typed interface stubs require `Returns:`."""
    violations = get_sample_docstring_violations(
        '''
class Interface:
    """Example interface."""

    def value(self, token: str) -> int | None:
        """Get a value.

        Arguments:
            token: token text
        """
        ...

    def unavailable(self) -> str:
        """Get an unavailable value."""
        raise NotImplementedError

    def no_value(self) -> None:
        """Perform an operation."""
        ...
'''
    )

    assert [
        (violation.qualified_name, violation.rule_id) for violation in violations
    ] == [
        ("Interface.value", "missing-returns"),
        ("Interface.unavailable", "missing-returns"),
        ("Interface.unavailable", "missing-raises"),
    ]


def test_docstring_properties_need_no_returns_section():
    """Test property and cached-property getters need no `Returns:` section."""
    violations = get_sample_docstring_violations(
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


def test_docstring_returns_are_required_for_async_functions():
    """Test value-returning async functions require `Returns:`."""
    violations = get_sample_docstring_violations(
        '''
async def sample():
    """Sample async function."""
    return 1
'''
    )

    assert [violation.rule_id for violation in violations] == ["missing-returns"]


def test_docstring_returns_are_required_for_value_returns():
    """Test ordinary value-returning functions require `Returns:`."""
    violations = get_sample_docstring_violations(
        '''
def sample():
    """Sample function."""
    return 1
'''
    )

    assert [violation.rule_id for violation in violations] == ["missing-returns"]
