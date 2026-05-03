#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Class for reviewing and refining Cantonese transcriptions."""

from __future__ import annotations

from enum import StrEnum
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

from scinoephile.audio.subtitles import (
    AudioSeries,
    get_series_from_segments,
)
from scinoephile.audio.transcription.demucs_separator import DemucsSeparator
from scinoephile.audio.transcription.segment_tools import (
    get_segment_split_on_whitespace,
    get_segment_zho_converted,
)
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.whisper_transcriber import WhisperTranscriber
from scinoephile.common.validation import val_input_dir_path
from scinoephile.core.llms import LLMProvider, Queryer, TestCase
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.llms.providers.registry import get_default_provider

from .aligner import Aligner
from .deliniation import YueVsZhoYueHansDeliniationPrompt
from .punctuation import YueVsZhoYueHansPunctuationPrompt

if TYPE_CHECKING:
    from pydub import AudioSegment

__all__ = [
    "DemucsMode",
    "VADMode",
    "YueTranscriber",
]

logger = getLogger(__name__)


class DemucsMode(StrEnum):
    """Demucs preprocessing modes for 粤文 transcription."""

    ON = "on"
    """Run Demucs preprocessing."""
    OFF = "off"
    """Skip Demucs preprocessing."""


class VADMode(StrEnum):
    """Whisper voice activity detection modes for 粤文 transcription."""

    AUTO = "auto"
    """Use VAD automatically when needed."""
    ON = "on"
    """Always use VAD."""
    OFF = "off"
    """Never use VAD."""


class YueTranscriber:
    """Class for transcribing and aligning 粤文 audio."""

    def __init__(
        self,
        *,
        model_name: str = "khleeloo/whisper-large-v3-cantonese",
        demucs_mode: DemucsMode = DemucsMode.OFF,
        vad_mode: VADMode = VADMode.AUTO,
        provider: LLMProvider | None = None,
        convert: OpenCCConfig | None = None,
        deliniation_prompt_cls: type[YueVsZhoYueHansDeliniationPrompt],
        punctuation_prompt_cls: type[YueVsZhoYueHansPunctuationPrompt],
        test_case_directory_path: Path,
        deliniation_test_cases: list[TestCase],
        punctuation_test_cases: list[TestCase],
    ):
        """Initialize.

        Arguments:
            model_name: Whisper model name used for transcription
            demucs_mode: Demucs preprocessing mode for transcription
            vad_mode: Whisper VAD mode for transcription
            provider: provider to use for LLM queryers
            convert: OpenCC configuration used to convert transcribed text
            deliniation_prompt_cls: prompt class for block-boundary deliniation
            punctuation_prompt_cls: prompt class for line punctuation
            test_case_directory_path: path to directory containing test cases
            deliniation_test_cases: deliniation test cases
            punctuation_test_cases: punctuation test cases
        """
        self.test_case_directory_path = val_input_dir_path(test_case_directory_path)
        self.model_name = model_name
        self.vad_mode = vad_mode
        self.demucs_mode = demucs_mode
        self.convert = convert
        if provider is None:
            provider = get_default_provider()
        self.demucs_separator = None
        if demucs_mode == DemucsMode.ON:
            self.demucs_separator = DemucsSeparator()
        self.vad_transcriber = None
        if vad_mode in (VADMode.AUTO, VADMode.ON):
            self.vad_transcriber = self._get_whisper_transcriber(use_vad=True)
        self.no_vad_transcriber = None
        if vad_mode in (VADMode.AUTO, VADMode.OFF):
            self.no_vad_transcriber = self._get_whisper_transcriber(use_vad=False)
        deliniation_queryer_cls = Queryer.get_queryer_cls(deliniation_prompt_cls)
        self.deliniation_queryer = deliniation_queryer_cls(
            prompt_test_cases=[tc for tc in deliniation_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in deliniation_test_cases if tc.verified],
            provider=provider,
            cache_dir_path=get_runtime_cache_dir_path("llm"),
        )
        punctuation_queryer_cls = Queryer.get_queryer_cls(punctuation_prompt_cls)
        self.punctuation_queryer = punctuation_queryer_cls(
            prompt_test_cases=[tc for tc in punctuation_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in punctuation_test_cases if tc.verified],
            provider=provider,
            cache_dir_path=get_runtime_cache_dir_path("llm"),
        )
        self.aligner = Aligner(
            deliniation_queryer=self.deliniation_queryer,
            punctuation_queryer=self.punctuation_queryer,
            test_case_dir_path=self.test_case_directory_path,
        )

    def process_all_blocks(
        self,
        yuewen: AudioSeries,
        zhongwen: Series,
        stop_at_idx: int | None = None,
    ) -> AudioSeries:
        """Process all blocks of audio, transcribing and aligning them with subtitles.

        Arguments:
            yuewen: nascent 粤文 subtitles
            zhongwen: corresponding 中文 subtitles
            stop_at_idx: stop after processing this block index
        """
        all_yuewen_block_series: list | None = [None] * len(yuewen.blocks)

        # Run all blocks
        if stop_at_idx is None:
            stop_at_idx = len(yuewen.blocks) - 1
        for block_idx in range(stop_at_idx + 1):
            yuewen_block = yuewen.blocks[block_idx]
            zhongwen_block = zhongwen.blocks[block_idx]
            yuewen_block_series = self.process_block(yuewen_block, zhongwen_block)
            logger.info(f"BLOCK {block_idx}:")
            logger.info(f"中文:\n{zhongwen_block.to_simple_string()}")
            logger.info(f"粤文:\n{yuewen_block_series.to_simple_string()}")
            all_yuewen_block_series[block_idx] = yuewen_block_series

        # Concatenate and return
        all_events = []
        for block_series in all_yuewen_block_series:
            if block_series is not None:
                all_events.extend(block_series.events)
        all_events.sort(key=lambda event: event.start)
        yuewen_series = AudioSeries(audio=yuewen.audio, events=all_events)
        logger.info(f"Concatenated Series:\n{yuewen_series.to_simple_string()}")
        return yuewen_series

    def process_block(
        self,
        yuewen_block: AudioSeries,
        zhongwen_block: Series,
    ) -> AudioSeries:
        """Process a single block of audio, transcribing and aligning it with subtitles.

        Arguments:
            yuewen_block: nascent 粤文 block
            zhongwen_block: corresponding 中文 block
        """
        # Transcribe audio
        segments = self._transcribe_block_audio(yuewen_block.audio)

        # Split segments based on pauses
        split_segments = []
        for segment in segments:
            split_segments.extend(get_segment_split_on_whitespace(segment))

        # Convert transcribed text, if applicable
        converted_segments = split_segments
        if self.convert is not None:
            converted_segments = [
                get_segment_zho_converted(segment, self.convert)
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

        self.aligner.update_all_test_cases()

        return yuewen_block_series

    def _get_cached_block_transcription(
        self, cache_audio: AudioSegment
    ) -> list[TranscribedSegment] | None:
        """Get cached block transcription before expensive preprocessing.

        Arguments:
            cache_audio: original block audio used for cache-key generation
        Returns:
            cached transcription, if present
        """
        if self.vad_mode == VADMode.ON:
            assert self.vad_transcriber is not None
            return self.vad_transcriber.get_cached_transcription(cache_audio)
        if self.vad_mode == VADMode.OFF:
            assert self.no_vad_transcriber is not None
            return self.no_vad_transcriber.get_cached_transcription(cache_audio)

        assert self.vad_transcriber is not None
        cached_segments = self.vad_transcriber.get_cached_transcription(cache_audio)
        if cached_segments is not None and any(
            segment.text.strip() for segment in cached_segments
        ):
            return cached_segments

        return None

    def _get_whisper_transcriber(self, use_vad: bool) -> WhisperTranscriber:
        """Build a Whisper transcriber for the requested VAD setting.

        Arguments:
            use_vad: whether Whisper VAD is enabled for transcription
        Returns:
            configured Whisper transcriber
        """
        return WhisperTranscriber(
            model_name=self.model_name,
            cache_dir_path=get_runtime_cache_dir_path("whisper"),
            use_demucs=self.demucs_mode == DemucsMode.ON,
            use_vad=use_vad,
        )

    def _transcribe_block_audio(self, audio: AudioSegment) -> list[TranscribedSegment]:
        """Transcribe one block of audio with the configured VAD behavior.

        Arguments:
            audio: block audio to transcribe
        Returns:
            transcribed segments
        """
        cache_audio = audio
        cached_segments = self._get_cached_block_transcription(cache_audio)
        if cached_segments is not None:
            return cached_segments

        if self.demucs_mode == DemucsMode.ON:
            assert self.demucs_separator is not None
            logger.info("Applying Demucs vocal separation before transcription")
            audio = self.demucs_separator(audio)

        if self.vad_mode == VADMode.ON:
            assert self.vad_transcriber is not None
            return self.vad_transcriber(audio, cache_audio=cache_audio)
        if self.vad_mode == VADMode.OFF:
            assert self.no_vad_transcriber is not None
            return self.no_vad_transcriber(audio, cache_audio=cache_audio)

        assert self.vad_transcriber is not None
        segments = self.vad_transcriber(audio, cache_audio=cache_audio)
        if any(segment.text.strip() for segment in segments):
            return segments

        logger.info("Retrying block transcription without VAD after empty result")
        assert self.no_vad_transcriber is not None
        return self.no_vad_transcriber(audio, cache_audio=cache_audio)
