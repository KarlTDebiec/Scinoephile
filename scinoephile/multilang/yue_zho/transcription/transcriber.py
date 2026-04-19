#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Class for reviewing and refining Cantonese transcriptions."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path

from scinoephile.audio.subtitles import (
    AudioSeries,
    get_series_from_segments,
)
from scinoephile.audio.transcription import (
    WhisperTranscriber,
    get_segment_split_on_whitespace,
    get_segment_zho_converted,
)
from scinoephile.common.validation import val_input_dir_path
from scinoephile.core.llms import Queryer, TestCase
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.multilang.yue_zho.transcription.punctuating import (
    YueZhoHansPunctuatingPrompt,
)
from scinoephile.multilang.yue_zho.transcription.shifting import (
    YueZhoHansShiftingPrompt,
)

from .aligner import Aligner

logger = getLogger(__name__)


class YueTranscriber:
    """Class for transcribing and aligning 粤文 audio."""

    def __init__(
        self,
        test_case_directory_path: Path,
        shifting_test_cases: list[TestCase],
        punctuating_test_cases: list[TestCase],
    ):
        """Initialize.

        Arguments:
            test_case_directory_path: path to directory containing test cases
            shifting_test_cases: shifting test cases
            punctuating_test_cases: punctuating test cases
        """
        self.test_case_directory_path = val_input_dir_path(test_case_directory_path)
        self.transcriber = WhisperTranscriber(
            "khleeloo/whisper-large-v3-cantonese",
            cache_dir_path=get_runtime_cache_dir_path("whisper"),
        )
        shifting_queryer_cls = Queryer.get_queryer_cls(YueZhoHansShiftingPrompt)
        self.shifting_queryer = shifting_queryer_cls(
            prompt_test_cases=[tc for tc in shifting_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in shifting_test_cases if tc.verified],
            cache_dir_path=get_runtime_cache_dir_path("llm"),
        )
        punctuating_queryer_cls = Queryer.get_queryer_cls(YueZhoHansPunctuatingPrompt)
        self.punctuating_queryer = punctuating_queryer_cls(
            prompt_test_cases=[tc for tc in punctuating_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in punctuating_test_cases if tc.verified],
            cache_dir_path=get_runtime_cache_dir_path("llm"),
        )
        self.aligner = Aligner(
            shifting_queryer=self.shifting_queryer,
            punctuating_queryer=self.punctuating_queryer,
        )

    def process_all_blocks(
        self,
        yuewen: AudioSeries,
        zhongwen: Series,
        stop_at_idx: int | None = None,
    ):
        """Process all blocks of audio, transcribing and aligning them with subtitles.

        Arguments:
            yuewen: Nascent 粤文 subtitles
            zhongwen: Corresponding 中文 subtitles
            stop_at_idx: Stop after processing this block index
        """
        all_yuewen_block_series: list | None = [None] * len(yuewen.blocks)

        # Run all blocks
        if stop_at_idx is None:
            stop_at_idx = len(yuewen.blocks) - 1
        for block_idx in range(stop_at_idx + 1):
            yuewen_block = yuewen.blocks[block_idx]
            zhongwen_block = zhongwen.blocks[block_idx]
            yuewen_block_series = self.process_block(yuewen_block, zhongwen_block)
            logger.info("BLOCK %s:", block_idx)
            logger.info("中文:\n%s", zhongwen_block.to_simple_string())
            logger.info("粤文:\n%s", yuewen_block_series.to_simple_string())
            all_yuewen_block_series[block_idx] = yuewen_block_series

        # Concatenate and return
        all_events = []
        for block_series in all_yuewen_block_series:
            if block_series is not None:
                all_events.extend(block_series.events)
        all_events.sort(key=lambda event: event.start)
        yuewen_series = AudioSeries(audio=yuewen.audio, events=all_events)
        logger.info("Concatenated Series:\n%s", yuewen_series.to_simple_string())
        return yuewen_series

    def process_block(
        self,
        yuewen_block: AudioSeries,
        zhongwen_block: Series,
    ) -> AudioSeries:
        """Process a single block of audio, transcribing and aligning it with subtitles.

        Arguments:
            yuewen_block: Nascent 粤文 block
            zhongwen_block: Corresponding 中文 block
        """
        # Transcribe audio
        segments = self.transcriber(yuewen_block.audio)

        # Split segments based on pauses
        split_segments = []
        for segment in segments:
            split_segments.extend(get_segment_split_on_whitespace(segment))

        # Simplify segments (optional)
        converted_segments = [
            get_segment_zho_converted(segment, OpenCCConfig.hk2s)
            for segment in split_segments
        ]

        # Merge segments into a series
        yuewen_block_series = get_series_from_segments(
            converted_segments,
            audio=yuewen_block.audio,
            offset=yuewen_block[0].start,
        )

        # Sync segments with the corresponding 中文 subtitles
        alignment = self.aligner.align(zhongwen_block, yuewen_block_series)
        yuewen_block_series = alignment.yuewen

        self.aligner.update_all_test_cases(self.test_case_directory_path)

        return yuewen_block_series
