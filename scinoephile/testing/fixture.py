#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Functions related to test fixtures."""
from __future__ import annotations

from functools import partial
from typing import Any

from pytest import fixture


def parametrized_fixture(cls: type, params: list[dict[str, Any]]):
    """Decorator for parametrized test fixtures which provides clearer test output.

    Arguments:
        cls: Stage fixture class
        params: Fixture parameters
    Returns:
        Fixture with provided params and clear ids
    """

    def get_name(args):
        return f"{cls.__name__}({','.join(map(str, args.values()))})"

    return partial(fixture(params=params, ids=get_name))
