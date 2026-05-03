#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 粤文/中文 text."""

from __future__ import annotations

import importlib as _importlib
from collections.abc import Callable
from typing import Any

_FUNCTION_EXPORT_MODULES = {
    "get_yue_block_reviewed_vs_zho": ".block_review",
    "get_yue_line_reviewed_vs_zho": ".line_review",
    "get_yue_transcribed_vs_zho": ".transcription",
    "get_yue_translated_vs_zho": ".translation",
}

get_yue_block_reviewed_vs_zho: Callable[..., Any]
"""Block review 粤文 subtitles against 中文 subtitles."""
get_yue_line_reviewed_vs_zho: Callable[..., Any]
"""Line review 粤文 subtitles against 中文 subtitles."""
get_yue_transcribed_vs_zho: Callable[..., Any]
"""Transcribe 粤文 audio against 中文 subtitles."""
get_yue_translated_vs_zho: Callable[..., Any]
"""Translate 粤文 subtitles from 中文 subtitles."""

__all__ = [
    "get_yue_line_reviewed_vs_zho",
    "get_yue_block_reviewed_vs_zho",
    "get_yue_transcribed_vs_zho",
    "get_yue_translated_vs_zho",
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
