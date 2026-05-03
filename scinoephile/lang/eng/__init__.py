#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English (eng) text.

Package hierarchy (modules may import from any above):
* cleaning / flattening / ocr_validation / prompts
* ocr_fusion / block_review
"""

from __future__ import annotations

import importlib as _importlib
from collections.abc import Callable
from typing import Any

_FUNCTION_EXPORT_MODULES = {
    "get_eng_block_reviewed": ".block_review",
    "get_eng_cleaned": ".cleaning",
    "get_eng_flattened": ".flattening",
    "get_eng_ocr_fused": ".ocr_fusion",
    "validate_eng_ocr": ".ocr_validation",
}

get_eng_block_reviewed: Callable[..., Any]
"""Block review English subtitles."""
get_eng_cleaned: Callable[..., Any]
"""Clean English subtitles."""
get_eng_flattened: Callable[..., Any]
"""Flatten English subtitles."""
get_eng_ocr_fused: Callable[..., Any]
"""Fuse English OCR subtitle outputs."""
validate_eng_ocr: Callable[..., Any]
"""Validate English OCR subtitles."""

__all__ = [
    "get_eng_cleaned",
    "get_eng_flattened",
    "get_eng_ocr_fused",
    "get_eng_block_reviewed",
    "validate_eng_ocr",
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
