#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to OpenAI Integration."""
from __future__ import annotations

from scinoephile.open_ai.openai_service import OpenAiService
from scinoephile.open_ai.subtitle_group_response import SubtitleGroupResponse
from scinoephile.open_ai.subtitle_series_response import SubtitleSeriesResponse
from scinoephile.open_ai.sync_group_notes_response import SyncGroupNotesResponse
from scinoephile.open_ai.sync_notes_response import (
    SyncNotesResponse,
)

__all__ = [
    "OpenAiService",
    "SubtitleGroupResponse",
    "SubtitleSeriesResponse",
    "SyncGroupNotesResponse",
    "SyncNotesResponse",
]
