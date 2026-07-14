#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reference-guided audio transcription processor."""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from logging import getLogger

from pydub import AudioSegment

from scinoephile.audio.subtitles import AudioSeries, get_series_from_segments
from scinoephile.audio.transcription import (
    DemucsSeparator,
    TranscribedSegment,
    WhisperTranscriber,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series

from .aligner import TranscriptionAligner

__all__ = [
    "DemucsMode",
    "GuidedTranscriptionProcessor",
    "TranscribedSegmentSplitter",
    "VADMode",
]


TranscribedSegmentSplitter = Callable[
    [TranscribedSegment],
    list[TranscribedSegment],
]
"""Callable that splits one transcribed segment into zero or more segments."""

logger = getLogger(__name__)


class DemucsMode(StrEnum):
    """Demucs preprocessing modes for transcription."""

    ON = "on"
    """Run Demucs preprocessing."""
    OFF = "off"
    """Skip Demucs preprocessing."""


class VADMode(StrEnum):
    """Whisper voice activity detection modes for transcription."""

    AUTO = "auto"
    """Use VAD automatically when needed."""
    ON = "on"
    """Always use VAD."""
    OFF = "off"
    """Never use VAD."""


class GuidedTranscriptionProcessor:
    """Transcribe audio and align it with reference subtitles."""

    def __init__(
        self,
        *,
        language: Language,
        reference_language: Language,
        model_name: str,
        whisper_language: str,
        aligner: TranscriptionAligner,
        demucs_mode: DemucsMode = DemucsMode.OFF,
        vad_mode: VADMode = VADMode.AUTO,
        segment_splitter: TranscribedSegmentSplitter | None = None,
    ):
        """Initialize.

        Arguments:
            language: transcription language
            reference_language: reference subtitle language
            model_name: Whisper model name used for transcription
            whisper_language: language code passed to Whisper
            aligner: transcription aligner
            demucs_mode: Demucs preprocessing mode
            vad_mode: Whisper VAD mode
            segment_splitter: optional strategy for splitting Whisper segments
        """
        self.language = language
        self.reference_language = reference_language
        self.model_name = model_name
        self.whisper_language = whisper_language
        self.aligner = aligner
        self.demucs_mode = demucs_mode
        self.vad_mode = vad_mode
        self.segment_splitter = segment_splitter

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

    def process(
        self,
        audio_series: AudioSeries,
        reference_series: Series,
        stop_at_idx: int | None = None,
    ) -> AudioSeries:
        """Transcribe all audio blocks and align them with reference subtitles.

        Arguments:
            audio_series: audio divided into subtitle-timed blocks
            reference_series: reference subtitles corresponding to audio blocks
            stop_at_idx: exclusive block index at which to stop processing
        Returns:
            transcribed and aligned audio subtitle series
        Raises:
            ScinoephileError: if audio and reference block counts differ
            ValueError: if stop_at_idx is negative
        """
        audio_blocks = audio_series.blocks
        reference_blocks = reference_series.blocks
        if len(audio_blocks) != len(reference_blocks):
            raise ScinoephileError(
                f"Audio has {len(audio_blocks)} blocks but reference subtitles have "
                f"{len(reference_blocks)} blocks."
            )
        if stop_at_idx is None:
            stop_at_idx = len(audio_blocks)
        elif stop_at_idx < 0:
            raise ValueError("stop_at_idx must be greater than or equal to 0")

        output_events = []
        for block_idx, (audio_block, reference_block) in enumerate(
            zip(audio_blocks, reference_blocks, strict=True)
        ):
            if block_idx >= stop_at_idx:
                break
            output_block = self.process_block(audio_block, reference_block)
            logger.info(
                f"BLOCK {block_idx}:\n"
                f"REFERENCE ({self.reference_language.tag}):\n"
                f"{reference_block.to_simple_string()}\n"
                f"TRANSCRIPTION ({self.language.tag}):\n"
                f"{output_block.to_simple_string()}"
            )
            output_events.extend(output_block.events)

        output_events.sort(key=lambda event: event.start)
        output = AudioSeries(audio=audio_series.audio, events=output_events)
        logger.info(f"Concatenated Series:\n{output.to_simple_string()}")
        return output

    def process_block(
        self,
        audio_block: AudioSeries,
        reference_block: Series,
    ) -> AudioSeries:
        """Transcribe and align a single audio block.

        Arguments:
            audio_block: audio block to transcribe
            reference_block: corresponding reference subtitle block
        Returns:
            transcribed and aligned audio subtitle block
        """
        segments = self._transcribe_block_audio(audio_block.audio)
        if self.segment_splitter is None:
            split_segments = segments
        else:
            split_segments = []
            for segment in segments:
                split_segments.extend(self.segment_splitter(segment))

        offset = audio_block.buffered_start
        if offset is None:
            offset = audio_block[0].start
        transcription_block = get_series_from_segments(
            split_segments,
            audio=audio_block.audio,
            offset=offset,
        )
        alignment = self.aligner.align(reference_block, transcription_block)
        self.aligner.update_all_test_cases()
        return alignment.transcription

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
            use_vad: whether Whisper VAD is enabled
        Returns:
            configured Whisper transcriber
        """
        return WhisperTranscriber(
            model_name=self.model_name,
            language=self.whisper_language,
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
            whether the segments contain nonempty text with word timings
        """
        if not any(segment.text.strip() for segment in segments):
            return False
        return not any(
            segment.text.strip() and not segment.words for segment in segments
        )
