#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

"""Tests of exception documentation."""

from __future__ import annotations

from test.style.docs.checks import get_sample_docstring_violations


def test_docstring_raises_sections_cover_explicit_raises():
    """Test named, dynamic, and bare raises require documentation."""
    violations = get_sample_docstring_violations(
        '''
def named():
    """Raise a named exception."""
    raise ValueError

def dynamic(exception):
    """Raise a dynamic exception.

    Arguments:
        exception: exception to raise
    """
    raise exception

def reraised():
    """Reraise an exception."""
    try:
        dependency()
    except ValueError:
        raise

def documented():
    """Raise a documented exception.

    Raises:
        ValueError: always
    """
    raise ValueError

def propagated():
    """Propagate a documented exception.

    Raises:
        ValueError: when raised by the dependency
    """
    dependency()
'''
    )

    assert [
        (violation.qualified_name, violation.rule_id) for violation in violations
    ] == [
        ("named", "missing-raises"),
        ("dynamic", "missing-raises"),
        ("reraised", "missing-raises"),
    ]


def test_docstring_raises_ignore_nested_scopes_and_abstract_placeholders():
    """Test nested raises and abstract contract stubs do not affect a callable."""
    violations = get_sample_docstring_violations(
        '''
from abc import abstractmethod

def outer():
    """Define a nested function."""

    def inner():
        """Raise a documented exception.

        Raises:
            ValueError: always
        """
        raise ValueError

    inner()

@abstractmethod
def abstract() -> int:
    """Return a concrete implementation's value.

    Returns:
        implementation value
    """
    raise NotImplementedError()
'''
    )

    assert not violations
