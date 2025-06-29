#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runnable for converting between Hanzi characters."""

from __future__ import annotations

from typing import Any

from langchain_core.runnables import Runnable, RunnableConfig
from opencc import OpenCC

from scinoephile.audio.core import AudioBlock
from scinoephile.audio.models import TranscribedSegment, TranscriptionPayload


class HanziConverter(Runnable):
    """Runnable for converting between Hanzi characters."""

    def __init__(self, config: str = "s2hk"):
        """Initialize.

        Arguments:
            config: OpenCC configuration string (default: "s2hk")
        """
        super().__init__()

        self.config = config
        self.converter = OpenCC(config)

    def invoke(
        self,
        input: TranscriptionPayload,
        config: RunnableConfig | None = None,
        **kwargs: Any,
    ) -> TranscriptionPayload:
        """Convert Hanzi characters.

        Arguments:
            input: Transcription payload containing audio block and segments
            config: Runnable configuration
            **kwargs: Additional keyword arguments
        Returns:
            Transcription payload with converted segments
        """
        block: AudioBlock = input["block"]
        segments: list[TranscribedSegment] = input["segments"]
        for segment in segments:
            segment.text = self.converter.convert(segment.text)
            if segment.words:
                i = 0
                for word in segment.words:
                    word_length = len(word.text)
                    word.text = segment.text[i : i + word_length]
                    i += word_length
        return TranscriptionPayload(block=block, segments=segments)
