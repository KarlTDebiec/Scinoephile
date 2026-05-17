#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Class for reviewing and refining Cantonese transcriptions."""

from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum
from logging import getLogger
from pathlib import Path

from pydub import AudioSegment

from scinoephile.audio.subtitles import (
    AudioSeries,
    get_series_from_segments,
)
from scinoephile.audio.transcription import (
    MIMO_MODEL_NAME,
    MIMO_TOKENIZER_NAME,
    DemucsSeparator,
    MimoRuntime,
    MimoTranscriber,
    MimoTranscriptionError,
    TranscribedSegment,
    TranscriptionAlignmentError,
    WhisperTranscriber,
    get_segment_split_on_whitespace,
    get_segment_zho_converted,
)
from scinoephile.common.validation import val_input_dir_path
from scinoephile.core.llms import LLMProvider, Queryer, TestCase
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.providers.registry import get_provider

from .aligner import Aligner
from .deliniation import YueDeliniationVsZhoPromptYueHans
from .punctuation import YuePunctuationVsZhoPromptYueHans

__all__ = [
    "DemucsMode",
    "MimoRuntime",
    "TranscriptionBackend",
    "VADMode",
    "YueTranscriber",
]

logger = getLogger(__name__)


class DemucsMode(StrEnum):
    """Demucs preprocessing modes for written Cantonese transcription."""

    ON = "on"
    """Run Demucs preprocessing."""
    OFF = "off"
    """Skip Demucs preprocessing."""


class TranscriptionBackend(StrEnum):
    """ASR backend modes for written Cantonese transcription."""

    WHISPER = "whisper"
    """Use Whisper timestamped transcription."""
    MIMO = "mimo"
    """Use MiMo ASR with forced timestamp alignment."""


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
        model_name: str = "khleeloo/whisper-large-v3-cantonese",
        backend: TranscriptionBackend = TranscriptionBackend.WHISPER,
        demucs_mode: DemucsMode = DemucsMode.OFF,
        vad_mode: VADMode = VADMode.AUTO,
        mimo_model_name: str = MIMO_MODEL_NAME,
        mimo_tokenizer_name: str = MIMO_TOKENIZER_NAME,
        mimo_runtime: MimoRuntime = MimoRuntime.AUTO,
        mimo_language: str = "yue",
        mimo_max_tokens: int | None = None,
        mimo_chunk_duration_seconds: float | None = None,
        mimo_chunk_overlap_seconds: float = 1.0,
        mimo_worker_command: Sequence[str] | None = None,
        mimo_aligner_backend: str = "whisperx",
        mimo_aligner_language: str = "zh",
        mimo_aligner_model_name: str | None = None,
        mimo_aligner_worker_command: Sequence[str] | None = None,
        mimo_fallback: bool = True,
        provider: LLMProvider | None = None,
        convert: OpenCCConfig | None = None,
        additional_context: str | None = None,
        deliniation_prompt_cls: type[YueDeliniationVsZhoPromptYueHans],
        punctuation_prompt_cls: type[YuePunctuationVsZhoPromptYueHans],
        test_case_directory_path: Path,
        deliniation_test_cases: list[TestCase],
        punctuation_test_cases: list[TestCase],
    ):
        """Initialize.

        Arguments:
            model_name: Whisper model name used for transcription
            backend: ASR backend used for initial transcription
            demucs_mode: Demucs preprocessing mode for transcription
            vad_mode: Whisper VAD mode for transcription
            mimo_model_name: MiMo model name used when backend is MiMo
            mimo_tokenizer_name: MiMo audio tokenizer name
            mimo_runtime: runtime implementation used for MiMo inference
            mimo_language: language metadata passed to MiMo
            mimo_max_tokens: optional maximum number of MiMo text tokens to generate
            mimo_chunk_duration_seconds: optional chunk duration for MiMo inference
            mimo_chunk_overlap_seconds: context overlap applied to each MiMo chunk
            mimo_worker_command: optional command that runs the MiMo worker
            mimo_aligner_backend: timestamp alignment backend for MiMo
            mimo_aligner_language: language code used by the MiMo timestamp aligner
            mimo_aligner_model_name: optional timestamp aligner model name
            mimo_aligner_worker_command: optional timestamp aligner worker command
            mimo_fallback: whether Whisper and MiMo may fall back to each other
            provider: provider to use for LLM queryers
            convert: OpenCC configuration used to convert transcribed text
            additional_context: additional context to include in LLM prompts
            deliniation_prompt_cls: prompt class for block-boundary deliniation
            punctuation_prompt_cls: prompt class for line punctuation
            test_case_directory_path: path to directory containing test cases
            deliniation_test_cases: deliniation test cases
            punctuation_test_cases: punctuation test cases
        """
        self.test_case_directory_path = val_input_dir_path(test_case_directory_path)
        self.model_name = model_name
        self.backend = backend
        self.vad_mode = vad_mode
        self.demucs_mode = demucs_mode
        self.mimo_model_name = mimo_model_name
        self.mimo_tokenizer_name = mimo_tokenizer_name
        self.mimo_runtime = mimo_runtime
        self.mimo_language = mimo_language
        self.mimo_max_tokens = mimo_max_tokens
        self.mimo_chunk_duration_seconds = mimo_chunk_duration_seconds
        self.mimo_chunk_overlap_seconds = mimo_chunk_overlap_seconds
        self.mimo_worker_command = (
            tuple(mimo_worker_command) if mimo_worker_command is not None else None
        )
        self.mimo_aligner_backend = mimo_aligner_backend
        self.mimo_aligner_language = mimo_aligner_language
        self.mimo_aligner_model_name = mimo_aligner_model_name
        self.mimo_aligner_worker_command = (
            tuple(mimo_aligner_worker_command)
            if mimo_aligner_worker_command is not None
            else None
        )
        self.mimo_fallback = mimo_fallback
        self.convert = convert
        if provider is None:
            provider = get_provider()
        self.demucs_separator = None
        if demucs_mode == DemucsMode.ON:
            self.demucs_separator = DemucsSeparator(
                cache_dir_path=get_runtime_cache_dir_path("demucs")
            )
        needs_whisper = backend == TranscriptionBackend.WHISPER or mimo_fallback
        self.vad_transcriber = None
        if needs_whisper and vad_mode in (VADMode.AUTO, VADMode.ON):
            self.vad_transcriber = self._get_whisper_transcriber(use_vad=True)
        self.no_vad_transcriber = None
        if needs_whisper and vad_mode in (VADMode.AUTO, VADMode.OFF):
            self.no_vad_transcriber = self._get_whisper_transcriber(use_vad=False)
        self.mimo_transcriber = None
        needs_mimo = backend == TranscriptionBackend.MIMO or (
            backend == TranscriptionBackend.WHISPER and mimo_fallback
        )
        if needs_mimo:
            self.mimo_transcriber = self._get_mimo_transcriber()
        deliniation_queryer_cls = Queryer.get_queryer_cls(deliniation_prompt_cls)
        self.deliniation_queryer = deliniation_queryer_cls(
            prompt_test_cases=[tc for tc in deliniation_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in deliniation_test_cases if tc.verified],
            provider=provider,
            cache_dir_path=get_runtime_cache_dir_path("llm"),
            additional_context=additional_context,
        )
        punctuation_queryer_cls = Queryer.get_queryer_cls(punctuation_prompt_cls)
        self.punctuation_queryer = punctuation_queryer_cls(
            prompt_test_cases=[tc for tc in punctuation_test_cases if tc.prompt],
            verified_test_cases=[tc for tc in punctuation_test_cases if tc.verified],
            provider=provider,
            cache_dir_path=get_runtime_cache_dir_path("llm"),
            additional_context=additional_context,
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
        if getattr(self, "backend", TranscriptionBackend.WHISPER) == (
            TranscriptionBackend.MIMO
        ):
            assert self.mimo_transcriber is not None
            return self.mimo_transcriber.get_cached_transcription(cache_audio)

        return self._get_cached_whisper_block_transcription(cache_audio)

    def _get_cached_whisper_block_transcription(
        self, cache_audio: AudioSegment
    ) -> list[TranscribedSegment] | None:
        """Get cached Whisper block transcription.

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

    def _get_mimo_transcriber(self) -> MimoTranscriber:
        """Build a MiMo transcriber for the requested backend settings.

        Returns:
            configured MiMo transcriber
        """
        return MimoTranscriber(
            model_name=self.mimo_model_name,
            tokenizer_name=self.mimo_tokenizer_name,
            mimo_runtime=self.mimo_runtime,
            language=self.mimo_language,
            max_tokens=self.mimo_max_tokens,
            chunk_duration_seconds=self.mimo_chunk_duration_seconds,
            chunk_overlap_seconds=self.mimo_chunk_overlap_seconds,
            cache_dir_path=get_runtime_cache_dir_path("mimo"),
            aligner_backend=self.mimo_aligner_backend,
            aligner_language=self.mimo_aligner_language,
            aligner_model_name=self.mimo_aligner_model_name,
            aligner_worker_command=self.mimo_aligner_worker_command,
            worker_command=self.mimo_worker_command,
            use_demucs=self.demucs_mode == DemucsMode.ON,
            use_vad=self.vad_mode != VADMode.OFF,
        )

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

        if getattr(self, "backend", TranscriptionBackend.WHISPER) == (
            TranscriptionBackend.MIMO
        ):
            return self._transcribe_audio_with_mimo(audio, cache_audio=cache_audio)

        try:
            segments = self._transcribe_audio_with_whisper(
                audio,
                cache_audio=cache_audio,
            )
        except AssertionError as exc:
            if not getattr(self, "mimo_fallback", False):
                raise
            logger.warning(f"Falling back to MiMo after Whisper failure: {exc}")
            return self._transcribe_audio_with_mimo(
                audio,
                cache_audio=cache_audio,
                allow_whisper_fallback=False,
            )

        if self._segments_are_usable(segments):
            return segments
        if not getattr(self, "mimo_fallback", False):
            return segments

        logger.warning("Falling back to MiMo after unusable Whisper transcription")
        return self._transcribe_audio_with_mimo(
            audio,
            cache_audio=cache_audio,
            allow_whisper_fallback=False,
        )

    def _transcribe_audio_with_mimo(
        self,
        audio: AudioSegment,
        *,
        cache_audio: AudioSegment,
        allow_whisper_fallback: bool = True,
    ) -> list[TranscribedSegment]:
        """Transcribe audio using the MiMo backend.

        Arguments:
            audio: block audio to transcribe, after any preprocessing
            cache_audio: original block audio used for cache-key generation
            allow_whisper_fallback: whether MiMo failure should retry Whisper
        Returns:
            transcribed segments
        """
        assert self.mimo_transcriber is not None
        try:
            return self.mimo_transcriber(audio, cache_audio=cache_audio)
        except (MimoTranscriptionError, TranscriptionAlignmentError) as exc:
            if not self.mimo_fallback or not allow_whisper_fallback:
                raise
            logger.warning(f"Falling back to Whisper after MiMo failure: {exc}")
            return self._transcribe_audio_with_whisper(
                audio,
                cache_audio=cache_audio,
            )

    def _transcribe_audio_with_whisper(
        self,
        audio: AudioSegment,
        *,
        cache_audio: AudioSegment,
    ) -> list[TranscribedSegment]:
        """Transcribe audio using Whisper VAD retry behavior.

        Arguments:
            audio: block audio to transcribe, after any preprocessing
            cache_audio: original block audio used for cache-key generation
        Returns:
            transcribed segments
        """
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
