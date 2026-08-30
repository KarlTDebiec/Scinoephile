#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

"""Tests of TypedDict field documentation."""

from __future__ import annotations

from test.style.docs.checks import get_sample_docstring_violations


def test_typed_dict_field_documentation_violations_are_detected():
    """Test undocumented TypedDict fields are detected."""
    violations = get_sample_docstring_violations(
        '''
class Example(TypedDict):
    """Example payload."""

    documented: str
    """Documented field."""

    undocumented: int
'''
    )

    assert [
        (violation.qualified_name, violation.rule_id) for violation in violations
    ] == [("Example.undocumented", "missing-typed-dict-field-docstring")]
