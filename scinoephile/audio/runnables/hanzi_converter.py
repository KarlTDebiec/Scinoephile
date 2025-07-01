#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runnable for converting between Hanzi characters."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from langchain_core.runnables import Runnable, RunnableConfig
from opencc import OpenCC

from scinoephile.audio.models import TranscribedSegment


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
        input: TranscribedSegment,
        config: RunnableConfig | None = None,
        **kwargs: Any,
    ) -> TranscribedSegment:
        """Convert Hanzi between character sets.

        Arguments:
            input: Transcribed segment containing text and words
            config: Runnable configuration
            **kwargs: Additional keyword arguments
        Returns:
            TranscribedSegment with converted text and words
        """
        output = deepcopy(input)
        output.text = self.converter.convert(output.text)
        if output.words:
            i = 0
            for word in output.words:
                word_length = len(word.text)
                word.text = output.text[i : i + word_length]
                i += word_length
        return output
