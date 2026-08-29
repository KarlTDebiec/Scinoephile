#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

"""Tests of callable argument documentation."""

from __future__ import annotations

import pytest

from test.style.docs.checks import get_sample_docstring_violations


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
    violations = get_sample_docstring_violations(
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
    violations = get_sample_docstring_violations(
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
    violations = get_sample_docstring_violations(
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
    violations = get_sample_docstring_violations(
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


def test_docstring_only_self_and_cls_need_no_arguments_section():
    """Test `self` and `cls` do not require `Arguments:` documentation."""
    violations = get_sample_docstring_violations(
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


def test_docstring_plain_self_and_cls_parameters_require_documentation():
    """Test ordinary functions must document parameters named `self` or `cls`."""
    violations = get_sample_docstring_violations(
        '''
def ordinary(self, cls):
    """Run an ordinary function."""
'''
    )

    assert [violation.rule_id for violation in violations] == ["missing-arguments"]
