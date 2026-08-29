#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

"""Tests of generator yield documentation."""

from __future__ import annotations

from test.style.docs.checks import get_sample_docstring_violations


def test_docstring_yields_sections_match_generator_bodies():
    """Test sync, delegated, and async yields require matching documentation."""
    violations = get_sample_docstring_violations(
        '''
def missing():
    """Yield a value."""
    yield 1

def delegated():
    """Delegate generated values."""
    yield from ()

async def asynchronous():
    """Yield a value asynchronously."""
    yield 1

def unexpected():
    """Do nothing.

    Yields:
        nonexistent value
    """

def documented():
    """Yield a documented value.

    Yields:
        generated value
    """
    yield 1
'''
    )

    assert [
        (violation.qualified_name, violation.rule_id) for violation in violations
    ] == [
        ("missing", "missing-yields"),
        ("delegated", "missing-yields"),
        ("asynchronous", "missing-yields"),
        ("unexpected", "unexpected-yields"),
    ]
