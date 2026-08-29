#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

"""Tests of docstring coverage and violation reporting."""

from __future__ import annotations

from pathlib import Path

from test.style.docs.checks import DocstringViolation, get_sample_docstring_violations


def test_documented_docstrings_have_no_violations():
    """Test documented modules, classes, and functions have no violations."""
    violations = get_sample_docstring_violations(
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


def test_docstring_missing_definitions_are_detected():
    """Test missing definition docstrings are detected with qualified names."""
    violations = get_sample_docstring_violations(
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
    assert not get_sample_docstring_violations("", include_module_docstring=False)

    violations = get_sample_docstring_violations(
        "value = 1", include_module_docstring=False
    )

    assert [
        (violation.qualified_name, violation.rule_id) for violation in violations
    ] == [("<module>", "missing-docstring")]


def test_docstring_overload_stubs_are_exempt():
    """Test direct and qualified overload stubs are exempt."""
    violations = get_sample_docstring_violations(
        """
from typing import overload

@overload
def parse(value: str) -> str: ...

@typing.overload
def load(value: int) -> int: ...
"""
    )

    assert not violations


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
