#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Chinese (zho) text.

Package hierarchy (modules may import from any above):
* cleaning / conversion / flattening / ocr_validation
* prompts
* ocr_fusion / block_review
"""

from __future__ import annotations

import importlib as _importlib
from collections.abc import Callable
from typing import Any

_FUNCTION_EXPORT_MODULES = {
    "get_zho_block_reviewed": ".block_review",
    "get_zho_cleaned": ".cleaning",
    "get_zho_converted": ".conversion",
    "get_zho_flattened": ".flattening",
    "get_zho_ocr_fused": ".ocr_fusion",
    "is_simplified": ".conversion",
    "is_traditional": ".conversion",
    "validate_zho_ocr": ".ocr_validation",
}

get_zho_block_reviewed: Callable[..., Any]
"""Block review 中文 subtitles."""
get_zho_cleaned: Callable[..., Any]
"""Clean 中文 subtitles."""
get_zho_converted: Callable[..., Any]
"""Convert 中文 text."""
get_zho_flattened: Callable[..., Any]
"""Flatten 中文 subtitles."""
get_zho_ocr_fused: Callable[..., Any]
"""Fuse 中文 OCR subtitle outputs."""
is_simplified: Callable[..., Any]
"""Check whether text is simplified 中文."""
is_traditional: Callable[..., Any]
"""Check whether text is traditional 中文."""
validate_zho_ocr: Callable[..., Any]
"""Validate 中文 OCR subtitles."""

__all__ = [
    "get_zho_cleaned",
    "get_zho_converted",
    "get_zho_flattened",
    "get_zho_ocr_fused",
    "get_zho_block_reviewed",
    "is_simplified",
    "is_traditional",
    "validate_zho_ocr",
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
