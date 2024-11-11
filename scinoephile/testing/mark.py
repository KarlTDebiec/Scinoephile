#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Marks for testing."""
from __future__ import annotations

from functools import partial
from os import getenv

from pytest import mark, param


def skip_if_ci(inner: partial | None = None) -> partial:
    """Mark test to skip if running within continuous integration pipeline.

    Arguments:
        inner: Nascent partial function of pytest.param with additional marks
    Returns:
        Partial function of pytest.param with marks
    """
    marks = [mark.skipif(getenv("CI") is not None, reason="Skip when running in CI")]
    if inner:
        marks.extend(inner.keywords["marks"])
    return partial(param, marks=marks)
