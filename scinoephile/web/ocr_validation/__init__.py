#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Web application for OCR validation.

Package hierarchy (modules may import from any above):
* concerns / html_index
* session
* routes
* app
"""

from __future__ import annotations

from .app import create_app
from .concerns import (
    CharDimsConcern,
    ConcernKind,
    ErrorConcern,
    GapConcern,
    OcrConcern,
    SubtitleRowView,
    ValidationStatus,
)
from .html_index import HtmlSubtitleEntry, load_html_entries, update_html_entry_text
from .session import OcrValidationSession

__all__ = [
    "CharDimsConcern",
    "ConcernKind",
    "ErrorConcern",
    "GapConcern",
    "HtmlSubtitleEntry",
    "OcrConcern",
    "OcrValidationSession",
    "SubtitleRowView",
    "ValidationStatus",
    "create_app",
    "load_html_entries",
    "update_html_entry_text",
]
