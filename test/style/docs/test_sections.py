#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

"""Tests of docstring section formatting."""

from __future__ import annotations

import pytest

from test.style.docs.checks import get_sample_docstring_violations


@pytest.mark.parametrize(
    ("section_name", "body"),
    [
        ("Raises", "raise ValueError"),
        ("Returns", "return value"),
        ("Yields", "yield value"),
    ],
)
def test_docstring_section_spacing_is_enforced(section_name: str, body: str):
    """Test adjacent output sections reject a preceding blank line.

    Arguments:
        section_name: output section name
        body: callable body source
    """
    violations = get_sample_docstring_violations(
        f'''
def sample(value):
    """Sample function.

    Arguments:
        value: sample value

    {section_name}:
        sample value
    """
    {body}
'''
    )

    assert [violation.rule_id for violation in violations] == ["section-spacing"]
