#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Mandarin Chinese (cmn) text."""

from __future__ import annotations

import importlib as _importlib
from collections.abc import Callable
from typing import Any

_FUNCTION_EXPORT_MODULES = {
    "get_cmn_romanized": ".romanization",
    "is_accented_pinyin": ".romanization",
    "is_numbered_pinyin": ".romanization",
}

get_cmn_romanized: Callable[..., Any]
"""Romanize Mandarin Chinese text."""
is_accented_pinyin: Callable[..., Any]
"""Check whether text is accented Pinyin."""
is_numbered_pinyin: Callable[..., Any]
"""Check whether text is numbered Pinyin."""

__all__ = [
    "get_cmn_romanized",
    "is_accented_pinyin",
    "is_numbered_pinyin",
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
