#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runnable for splitting segments."""

from __future__ import annotations

from typing import Any

from langchain_core.runnables import Runnable, RunnableConfig

from scinoephile.audio.models import TranscribedSegment, TranscriptionPayload


class SegmentSplitter(Runnable):
    """Runnable for splitting segments."""

    def invoke(
        self,
        input: TranscriptionPayload,
        config: RunnableConfig | None = None,
        **kwargs: Any,
    ) -> TranscriptionPayload:
        """Split segments.

        Arguments:
            input: Transcription payload containing audio block and segments
            config: Runnable configuration
            **kwargs: Additional keyword arguments
        Returns:
            Transcription payload with audio series created from segments
        """
        segments = input["segments"]
        split_segments = []
        id = 1
        for segment in segments:
            nascent_words = []
            # Groups of words
            for word in segment.words:
                if word.text.startswith(" "):
                    if nascent_words:
                        nascent_segment = TranscribedSegment(
                            id=id,
                            seek=0,
                            start=nascent_words[0].start,
                            end=nascent_words[-1].end,
                            text="".join([word.text for word in nascent_words]),
                            words=nascent_words,
                        )
                        split_segments.append(nascent_segment)
                        id += 1
                        nascent_words = []
                    word.text = word.text[1:]
                nascent_words.append(word)

            # Final group of words
            if nascent_words:
                nascent_segment = TranscribedSegment(
                    id=id,
                    seek=0,
                    start=nascent_words[0].start,
                    end=nascent_words[-1].end,
                    text="".join([word.text for word in nascent_words]),
                )
                split_segments.append(nascent_segment)
                id += 1
                nascent_words = []

        return TranscriptionPayload(
            block=input["block"],
            segments=split_segments,
        )
