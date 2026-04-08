#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CUHK dictionary package."""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "CuhkDictionaryService",
]


def __getattr__(name: str) -> Any:
    """Lazily expose package attributes to avoid circular imports.

    Arguments:
        name: attribute name requested from the package
    Returns:
        exported package attribute
    Raises:
        AttributeError: if the attribute is unknown
    """
    if name == "CuhkDictionaryService":
        return import_module(".service", __name__).CuhkDictionaryService
    raise AttributeError(name)
