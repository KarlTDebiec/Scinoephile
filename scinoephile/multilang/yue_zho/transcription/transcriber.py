#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Class for reviewing and refining Cantonese transcriptions."""

from __future__ import annotations

from enum import StrEnum
from logging import getLogger
from pathlib import Path

from pydub import AudioSegment

from scinoephile.audio.subtitles import (
    AudioSeries,
    get_series_from_segments,
)
from scinoephile.audio.transcription import (
    DemucsSeparator,
    TranscribedSegment,
    WhisperTranscriber,
    get_segment_split_on_whitespace,
    get_segment_zho_converted,
)
from scinoephile.common.validation import val_input_dir_path
from scinoephile.core.llms import LLMProvider, Queryer, TestCase
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.delineation import DelineationManager, DelineationPrompt
from scinoephile.llms.providers.registry import get_provider
from scinoephile.llms.punctuation import PunctuationPrompt

from .aligner import Aligner
from .punctuation import YueZhoPunctuationManager

__all__ = [
    "DEFAULT_YUE_WHISPER_MODEL_NAME",
    "DemucsMode",
    "VADMode",
    "YueTranscriber",
]

DEFAULT_YUE_WHISPER_MODEL_NAME = "khleeloo/whisper-large-v3-cantonese"
"""Default Whisper model name for written Cantonese transcription."""

logger = getLogger(__name__)


class DemucsMode(StrEnum):
    """Demucs preprocessing modes for written Cantonese transcription."""

    ON = "on"
    """Run Demucs preprocessing."""
    OFF = "off"
    """Skip Demucs preprocessing."""


class VADMode(StrEnum):
    """Whisper voice activity detection modes for written Cantonese transcription."""

    AUTO = "auto"
    """Use VAD automatically when needed."""
    ON = "on"
    """Always use VAD."""
    OFF = "off"
    """Never use VAD."""


class YueTranscriber:
    """Class for transcribing and aligning written Cantonese audio."""

    def __init__(
        self,
        *,
        model_name: str = DEFAULT_YUE_WHISPER_MODEL_NAME,
        demucs_mode: DemucsMode = DemucsMode.OFF,
        vad_mode: VADMode = VADMode.AUTO,
        provider: LLMProvider | None = None,
        convert: OpenCCConfig | None = None,
        additional_context: str | None = None,
        delineation_prompt: DelineationPrompt,
        punctuation_prompt: PunctuationPrompt,
        test_case_directory_path: Path,
        delineation_test_cases: list[TestCase],
        punctuation_test_cases: list[TestCase],
    ):
        """Initialize.

        Arguments:
            model_name: Whisper model name used for transcription
            demucs_mode: Demucs preprocessing mode for transcription
            vad_mode: Whisper VAD mode for transcription
            provider: provider to use for LLM queryers
            convert: OpenCC configuration used to convert transcribed text
            additional_context: additional context to include in LLM prompts
            delineation_prompt: prompt for block-boundary delineation
            punctuation_prompt: prompt for line punctuation
            test_case_directory_path: path to directory containing test cases
            delineation_test_cases: delineation test cases
            punctuation_test_cases: punctuation test cases
        """
        self.test_case_directory_path = val_input_dir_path(test_case_directory_path)
        self.model_name = model_name
        self.vad_mode = vad_mode
        self.demucs_mode = demucs_mode
        self.convert = convert
        if provider is None:
            provider = get_provider()
        self.demucs_separator = None
        if demucs_mode == DemucsMode.ON:
            self.demucs_separator = DemucsSeparator(
                cache_dir_path=get_runtime_cache_dir_path("demucs")
            )
        self.vad_transcriber = None
        if vad_mode in (VADMode.AUTO, VADMode.ON):
            self.vad_transcriber = self._get_whisper_transcriber(use_vad=True)
        self.no_vad_transcriber = None
        if vad_mode in (VADMode.AUTO, VADMode.OFF):
            self.no_vad_transcriber = self._get_whisper_transcriber(use_vad=False)
        self.delineation_queryer = Queryer(
            DelineationManager.get_test_case_cls(delineation_prompt),
            few_shot_test_cases=[tc for tc in delineation_test_cases if tc.few_shot],
            verified_test_cases=[tc for tc in delineation_test_cases if tc.verified],
            provider=provider,
            cache_dir_path=get_runtime_cache_dir_path("llm"),
            additional_context=additional_context,
        )
        self.punctuation_queryer = Queryer(
            YueZhoPunctuationManager.get_test_case_cls(punctuation_prompt),
            few_shot_test_cases=[tc for tc in punctuation_test_cases if tc.few_shot],
            verified_test_cases=[tc for tc in punctuation_test_cases if tc.verified],
            provider=provider,
            cache_dir_path=get_runtime_cache_dir_path("llm"),
            additional_context=additional_context,
        )
        self.aligner = Aligner(
            delineation_queryer=self.delineation_queryer,
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
            yuewen: nascent written Cantonese subtitles
            zhongwen: corresponding standard Chinese subtitles
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
            yuewen_block: nascent written Cantonese block
            zhongwen_block: corresponding standard Chinese block
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

        # Sync segments with the corresponding standard Chinese subtitles
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
        if cached_segments is not None and self._segments_are_usable(cached_segments):
            return cached_segments
        if self.no_vad_transcriber is not None:
            cached_segments = self.no_vad_transcriber.get_cached_transcription(
                cache_audio
            )
            if cached_segments is not None and self._segments_are_usable(
                cached_segments
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
        try:
            segments = self.vad_transcriber(audio, cache_audio=cache_audio)
        except AssertionError as exc:
            logger.warning(
                f"Retrying block transcription without VAD after Whisper assertion: "
                f"{exc}"
            )
            assert self.no_vad_transcriber is not None
            return self.no_vad_transcriber(audio, cache_audio=cache_audio)
        if self._segments_are_usable(segments):
            return segments

        logger.info(
            "Retrying block transcription without VAD after unusable VAD result"
        )
        assert self.no_vad_transcriber is not None
        return self.no_vad_transcriber(audio, cache_audio=cache_audio)

    @staticmethod
    def _segments_are_usable(segments: list[TranscribedSegment]) -> bool:
        """Determine whether transcribed segments are usable for alignment.

        Arguments:
            segments: transcribed segments to inspect
        Returns:
            whether the segments contain non-empty text with word timings
        """
        if not any(segment.text.strip() for segment in segments):
            return False

        return not any(
            segment.text.strip() and not segment.words for segment in segments
        )
