#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to models."""

from __future__ import annotations

import hashlib
from typing import Any

__all__ = [
    "get_model_name",
    "make_hashable",
]


def get_model_name(base_name: str, suffix: str) -> str:
    """Build a Pydantic-valid class name from a base name and suffix.

    If the name exceeds the 64-character Pydantic limit, replace the suffix
    with a deterministic short hash.

    Arguments:
        base_name: name of base class
        suffix: descriptive suffix

    Returns:
        Valid class name string
    """
    # Base name and suffix are short enough to use directly
    if len(base_name) + 1 + len(suffix) <= 64:
        return f"{base_name}_{suffix}"

    # Base name is too long even for hash of suffix to be used
    if len(base_name) + 1 + 12 > 64:
        raise ValueError("Base name too long to create a valid Pydantic class name.")

    # Use base name and hash of suffix
    digest = hashlib.sha256(suffix.encode("utf-8")).hexdigest()[:12]
    return f"{base_name}_{digest}"


def make_hashable(value: Any) -> Any:
    """Make a value hashable for use in keys.

    Arguments:
        value: Value to make hashable
    Returns:
        Hashable representation of the value
    """
    if isinstance(value, list):
        return tuple(make_hashable(v) for v in value)
    elif isinstance(value, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in value.items()))
    return value
