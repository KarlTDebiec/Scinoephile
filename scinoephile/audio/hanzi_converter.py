#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runnable for converting between Hanzi characters."""

from __future__ import annotations

from typing import Any

from langchain_core.runnables import Runnable, RunnableConfig
from opencc import OpenCC

from scinoephile.audio import AudioBlock, TranscribedSegment


class HanziConverter(Runnable):
    """Runnable for converting between Hanzi characters."""

    def __init__(self, config: str = "s2hk"):
        self.config = config
        self.converter = OpenCC(config)

    def invoke(
        self,
        input: dict[str, AudioBlock | list[TranscribedSegment]],
        config: RunnableConfig | None = None,
        **kwargs: dict[str, Any],
    ) -> dict[str, AudioBlock | list[TranscribedSegment]]:
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
                joined = "".join([w.text for w in segment.words])
        return {"block": block, "segments": segments}
