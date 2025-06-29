#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runnable for converting segments to an audio series."""

from __future__ import annotations

from typing import Any

from langchain_core.runnables import Runnable, RunnableConfig

from scinoephile.audio import AudioSeries, AudioSubtitle
from scinoephile.audio.models import TranscriptionPayload


class SegmentToSeriesConverter(Runnable):
    """Runnable for converting segments to an audio series."""

    def invoke(
        self,
        input: TranscriptionPayload,
        config: RunnableConfig | None = None,
        **kwargs: Any,
    ) -> TranscriptionPayload:
        """Convert segments to an audio series.

        Arguments:
            input: Transcription payload containing audio block and segments
            config: Runnable configuration
            **kwargs: Additional keyword arguments
        Returns:
            Transcription payload with audio series created from segments
        """
        source = input["source"]
        segments = input["segments"]
        source_start = source.events[0].start

        events = []
        for segment in segments:
            start = source_start + int(segment.start * 1000)
            end = source_start + int(segment.end * 1000)
            text = segment.text.strip()
            event = AudioSubtitle(
                start=start,
                end=end,
                text=text,
                segment=segment,
            )
            events.append(event)

        series = AudioSeries()
        series.audio = source.audio
        series.events = events
        return TranscriptionPayload(
            source=source,
            segments=segments,
            series=series,
        )
