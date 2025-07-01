#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runnables related to audio."""

from __future__ import annotations

from scinoephile.audio.runnables.cantonese_merger import CantoneseMerger
from scinoephile.audio.runnables.hanzi_converter import HanziConverter
from scinoephile.audio.runnables.segment_splitter import SegmentSplitter
from scinoephile.audio.runnables.segment_to_series_converter import (
    SegmentToSeriesConverter,
)
from scinoephile.audio.runnables.sync_grouper import SyncGrouper
from scinoephile.audio.runnables.whisper_transcriber import WhisperTranscriber

__all__ = [
    "CantoneseMerger",
    "HanziConverter",
    "SegmentSplitter",
    "SegmentToSeriesConverter",
    "SyncGrouper",
    "WhisperTranscriber",
]
