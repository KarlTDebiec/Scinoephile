#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

"""Tests of lexical scope handling in docstring checks."""

from __future__ import annotations

from test.style.docs.checks import get_sample_docstring_violations


def test_docstring_flow_detection_stops_at_nested_scopes():
    """Test nested function and class flow does not affect their parent."""
    violations = get_sample_docstring_violations(
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

    def generator():
        """Yield values.

        Yields:
            generated value
        """
        yield 3
'''
    )

    assert not violations
