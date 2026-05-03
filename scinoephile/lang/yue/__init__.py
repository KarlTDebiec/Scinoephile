#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Cantonese (yue) text.

Package hierarchy (modules may import from any above):
* conversion / prompts / romanization
"""

from __future__ import annotations

import importlib as _importlib
from collections.abc import Callable
from typing import Any

_FUNCTION_EXPORT_MODULES = {
    "get_yue_converted": ".conversion",
    "get_yue_romanized": ".romanization",
    "is_accented_yale": ".romanization",
    "is_numbered_jyutping": ".romanization",
}

get_yue_converted: Callable[..., Any]
"""Convert 粤文 text."""
get_yue_romanized: Callable[..., Any]
"""Romanize 粤文 text."""
is_accented_yale: Callable[..., Any]
"""Check whether text is accented Yale."""
is_numbered_jyutping: Callable[..., Any]
"""Check whether text is numbered Jyutping."""

__all__ = [
    "get_yue_converted",
    "get_yue_romanized",
    "is_accented_yale",
    "is_numbered_jyutping",
]


def __getattr__(name: str) -> object:
    """Load compatibility function exports lazily.

    Arguments:
        name: requested attribute name
    Returns:
        requested exported function
    Raises:
        AttributeError: if the attribute is not a lazy function export
    """
    if name not in _FUNCTION_EXPORT_MODULES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = _importlib.import_module(_FUNCTION_EXPORT_MODULES[name], __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value
