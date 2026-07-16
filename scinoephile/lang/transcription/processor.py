#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reference-guided audio transcription processor."""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from logging import getLogger

from pydub import AudioSegment
from pydub.effects import normalize

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

_AUDIO_END_TOLERANCE_SECONDS = 1.0
"""Maximum accepted Whisper timestamp extension beyond the source audio."""

_EXPECTED_TAIL_TOLERANCE_SECONDS = 1.0
"""Gap before the final guided subtitle that triggers focused recovery."""

_MAX_COMPRESSION_RATIO = 2.4
"""Maximum Whisper compression ratio accepted for guided alignment."""

_RECOVERY_TEMPERATURES = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
"""Whisper temperature schedule used after standard decoding fails."""

_TAIL_RECOVERY_CONTEXT_SECONDS = 3.0
"""Audio retained before the final guided subtitle during focused recovery."""

_TAIL_RECOVERY_HEADROOM_DB = 1.0
"""Peak headroom used when normalizing focused tail audio."""

_TAIL_RECOVERY_MAX_NO_SPEECH_PROBABILITY = 0.6
"""Maximum no-speech probability accepted from focused tail recovery."""

_TAIL_RECOVERY_MAX_SECONDS_PER_CHARACTER = 1.5
"""Maximum duration per character accepted from focused tail recovery."""


class DemucsMode(StrEnum):
    """Demucs preprocessing modes for transcription."""

    AUTO = "auto"
    """Run Demucs first and retry the original audio when needed."""
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
        if demucs_mode in (DemucsMode.AUTO, DemucsMode.ON):
            self.demucs_separator = DemucsSeparator(
                cache_dir_path=get_runtime_cache_dir_path("demucs")
            )
        primary_uses_demucs = demucs_mode in (DemucsMode.AUTO, DemucsMode.ON)
        self.vad_transcriber = None
        if vad_mode in (VADMode.AUTO, VADMode.ON):
            self.vad_transcriber = self._get_whisper_transcriber(
                use_demucs=primary_uses_demucs,
                use_vad=True,
            )
        self.no_vad_transcriber = None
        if vad_mode in (VADMode.AUTO, VADMode.OFF):
            self.no_vad_transcriber = self._get_whisper_transcriber(
                use_demucs=primary_uses_demucs,
                use_vad=False,
            )

        self.unseparated_vad_transcriber = None
        if demucs_mode == DemucsMode.AUTO and vad_mode in (
            VADMode.AUTO,
            VADMode.ON,
        ):
            self.unseparated_vad_transcriber = self._get_whisper_transcriber(
                use_demucs=False,
                use_vad=True,
            )
        self.unseparated_no_vad_transcriber = None
        if demucs_mode == DemucsMode.AUTO and vad_mode in (
            VADMode.AUTO,
            VADMode.OFF,
        ):
            self.unseparated_no_vad_transcriber = self._get_whisper_transcriber(
                use_demucs=False,
                use_vad=False,
            )

        recovery_uses_vad = vad_mode == VADMode.ON
        self.recovery_transcriber = self._get_whisper_transcriber(
            use_demucs=demucs_mode == DemucsMode.ON,
            use_vad=recovery_uses_vad,
            temperature=_RECOVERY_TEMPERATURES,
            condition_on_previous_text=False,
        )
        self.tail_recovery_transcriber = self._get_whisper_transcriber(
            use_demucs=False,
            use_vad=False,
            condition_on_previous_text=False,
        )

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
                f"BLOCK {block_idx + 1}:\n"
                f"REFERENCE ({self.reference_language.code}):\n"
                f"{reference_block.to_simple_string()}\n"
                f"TRANSCRIPTION ({self.language.code}):\n"
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
        offset = audio_block.buffered_start
        if offset is None:
            offset = audio_block[0].start
        expected_last_start = max(
            0.0,
            (reference_block[-1].start - offset) / 1000,
        )
        segments = self._transcribe_block_audio(
            audio_block.audio,
            expected_last_start=expected_last_start,
        )
        if self.segment_splitter is None:
            split_segments = segments
        else:
            split_segments = []
            for segment in segments:
                split_segments.extend(self.segment_splitter(segment))

        transcription_block = get_series_from_segments(
            split_segments,
            audio=audio_block.audio,
            offset=offset,
        )
        alignment = self.aligner.align(reference_block, transcription_block)
        self.aligner.update_all_test_cases()
        return alignment.transcription

    def _get_cached_block_transcription(
        self,
        cache_audio: AudioSegment,
        *,
        audio_duration: float,
    ) -> list[TranscribedSegment] | None:
        """Get cached block transcription before expensive preprocessing.

        Arguments:
            cache_audio: original block audio used for cache-key generation
            audio_duration: original block audio duration in seconds
        Returns:
            cached transcription, if present
        """
        transcribers = list(self._get_standard_transcribers())
        if self.demucs_mode == DemucsMode.AUTO:
            transcribers.extend(self._get_standard_transcribers(unseparated=True))
        transcribers.append(self.recovery_transcriber)
        for transcriber in transcribers:
            cached_segments = transcriber.get_cached_transcription(cache_audio)
            if cached_segments is not None and self._segments_are_usable(
                cached_segments,
                audio_duration=audio_duration,
            ):
                return cached_segments
        return None

    def _get_standard_transcribers(
        self,
        *,
        unseparated: bool = False,
    ) -> tuple[WhisperTranscriber, ...]:
        """Get standard transcribers in configured retry order.

        Arguments:
            unseparated: whether to return original-audio fallback transcribers
        Returns:
            configured standard transcribers
        """
        if unseparated:
            vad_transcriber = self.unseparated_vad_transcriber
            no_vad_transcriber = self.unseparated_no_vad_transcriber
        else:
            vad_transcriber = self.vad_transcriber
            no_vad_transcriber = self.no_vad_transcriber

        transcribers = []
        if vad_transcriber is not None:
            transcribers.append(vad_transcriber)
        if no_vad_transcriber is not None:
            transcribers.append(no_vad_transcriber)
        return tuple(transcribers)

    def _get_whisper_transcriber(
        self,
        *,
        use_demucs: bool,
        use_vad: bool,
        temperature: float | tuple[float, ...] = 0.0,
        condition_on_previous_text: bool = True,
    ) -> WhisperTranscriber:
        """Build a Whisper transcriber for the requested VAD setting.

        Arguments:
            use_demucs: whether Demucs preprocessing is applied
            use_vad: whether Whisper VAD is enabled
            temperature: decoding temperature or fallback schedule
            condition_on_previous_text: whether to condition each decoding window on
                the preceding window
        Returns:
            configured Whisper transcriber
        """
        return WhisperTranscriber(
            model_name=self.model_name,
            language=self.whisper_language,
            cache_dir_path=get_runtime_cache_dir_path("whisper"),
            use_demucs=use_demucs,
            use_vad=use_vad,
            temperature=temperature,
            condition_on_previous_text=condition_on_previous_text,
        )

    def _get_primary_transcription_audio(
        self,
        audio: AudioSegment,
    ) -> AudioSegment | None:
        """Apply configured Demucs preprocessing.

        Arguments:
            audio: original block audio
        Returns:
            primary transcription audio, or None after automatic separation failure
        """
        if self.demucs_mode == DemucsMode.OFF:
            return audio

        assert self.demucs_separator is not None
        logger.info("Applying Demucs vocal separation before transcription")
        try:
            return self.demucs_separator(audio)
        except ScinoephileError as exc:
            if self.demucs_mode == DemucsMode.ON:
                raise
            logger.warning(
                f"Demucs separation failed in automatic mode; falling back "
                f"to original audio: {exc}"
            )
            return None

    def _transcribe_block_audio(
        self,
        audio: AudioSegment,
        *,
        expected_last_start: float | None = None,
    ) -> list[TranscribedSegment]:
        """Transcribe one block of audio with the configured VAD behavior.

        Arguments:
            audio: block audio to transcribe
            expected_last_start: expected start of the final guided subtitle
        Returns:
            transcribed segments
        Raises:
            ScinoephileError: if all configured Whisper attempts are unusable
        """
        cache_audio = audio
        audio_duration = len(cache_audio) / 1000
        segments = self._get_cached_block_transcription(
            cache_audio,
            audio_duration=audio_duration,
        )
        if segments is None:
            primary_audio = self._get_primary_transcription_audio(audio)
            if primary_audio is not None:
                for transcriber in self._get_standard_transcribers():
                    segments = self._transcribe_with_candidate(
                        transcriber,
                        primary_audio,
                        cache_audio=cache_audio,
                        audio_duration=audio_duration,
                    )
                    if segments is not None:
                        break

            if segments is None and self.demucs_mode == DemucsMode.AUTO:
                if primary_audio is not None:
                    logger.info(
                        "Retrying block transcription with original audio after "
                        "unusable Demucs result"
                    )
                for transcriber in self._get_standard_transcribers(unseparated=True):
                    segments = self._transcribe_with_candidate(
                        transcriber,
                        audio,
                        cache_audio=cache_audio,
                        audio_duration=audio_duration,
                    )
                    if segments is not None:
                        break

            if segments is None:
                logger.info(
                    "Retrying block transcription with defensive Whisper decoding"
                )
                recovery_audio = audio
                if self.demucs_mode == DemucsMode.ON:
                    assert primary_audio is not None
                    recovery_audio = primary_audio
                segments = self._transcribe_with_candidate(
                    self.recovery_transcriber,
                    recovery_audio,
                    cache_audio=cache_audio,
                    audio_duration=audio_duration,
                )
        if segments is None:
            raise ScinoephileError(
                "Whisper produced no usable transcription after all configured "
                "recovery attempts."
            )
        return self._transcribe_with_focused_tail_recovery(
            segments,
            cache_audio,
            expected_last_start=expected_last_start,
        )

    def _transcribe_with_candidate(
        self,
        transcriber: WhisperTranscriber,
        audio: AudioSegment,
        *,
        cache_audio: AudioSegment,
        audio_duration: float,
    ) -> list[TranscribedSegment] | None:
        """Run and validate one Whisper transcription candidate.

        Arguments:
            transcriber: configured Whisper transcriber
            audio: audio to transcribe
            cache_audio: original audio used for cache-key generation
            audio_duration: original block audio duration in seconds
        Returns:
            usable transcribed segments, if produced
        """
        try:
            # Cached candidates were validated before preprocessing
            segments = transcriber(
                audio,
                cache_audio=cache_audio,
                use_cache=False,
            )
        except AssertionError as exc:
            logger.warning(
                f"Whisper transcription candidate failed with an assertion: {exc}"
            )
            return None
        if self._segments_are_usable(
            segments,
            audio_duration=audio_duration,
        ):
            return segments
        return None

    def _transcribe_with_focused_tail_recovery(
        self,
        segments: list[TranscribedSegment],
        audio: AudioSegment,
        *,
        expected_last_start: float | None,
    ) -> list[TranscribedSegment]:
        """Attempt focused recovery for possible speech near a guide-only tail.

        Arguments:
            segments: valid full-block transcription
            audio: original block audio
            expected_last_start: expected start of the final guided subtitle
        Returns:
            valid base transcription with any credible recovered tail appended
        """
        if expected_last_start is None:
            return segments

        last_word_end = max(
            word.end for segment in segments for word in (segment.words or [])
        )
        if last_word_end + _EXPECTED_TAIL_TOLERANCE_SECONDS >= expected_last_start:
            return segments

        tail_start = max(
            last_word_end,
            expected_last_start - _TAIL_RECOVERY_CONTEXT_SECONDS,
        )
        tail_start_ms = round(tail_start * 1000)
        tail_audio = audio[tail_start_ms:]
        if len(tail_audio) == 0 or tail_audio.rms == 0:
            logger.info(
                f"Keeping valid base Whisper transcription ending at "
                f"{last_word_end:.2f}s; focused tail audio is silent"
            )
            return segments

        logger.info(
            f"Attempting focused Whisper recovery from {tail_start:.2f}s after "
            f"transcription ended at {last_word_end:.2f}s before final guided "
            f"subtitle begins at {expected_last_start:.2f}s"
        )
        normalized_tail_audio = normalize(
            tail_audio,
            headroom=_TAIL_RECOVERY_HEADROOM_DB,
        )
        tail_audio_duration = len(normalized_tail_audio) / 1000
        tail_segments = self.tail_recovery_transcriber.get_cached_transcription(
            normalized_tail_audio
        )
        if tail_segments is not None and not self._segments_are_usable(
            tail_segments,
            audio_duration=tail_audio_duration,
        ):
            logger.info("Retrying focused tail transcription after unusable cache")
            tail_segments = None

        recovery_failed_with_assertion = False
        if tail_segments is None:
            try:
                candidate_tail_segments = self.tail_recovery_transcriber(
                    normalized_tail_audio,
                    use_cache=False,
                )
            except AssertionError as exc:
                recovery_failed_with_assertion = True
                logger.warning(
                    f"Keeping valid base Whisper transcription after focused tail "
                    f"recovery failed with an assertion: {exc}"
                )
            else:
                if self._segments_are_usable(
                    candidate_tail_segments,
                    audio_duration=tail_audio_duration,
                ):
                    tail_segments = candidate_tail_segments
        if tail_segments is None:
            if not recovery_failed_with_assertion:
                logger.info(
                    f"Keeping valid base Whisper transcription ending at "
                    f"{last_word_end:.2f}s after unusable focused tail recovery"
                )
            return segments

        recovered_segments = self._get_credible_tail_segments(
            tail_segments,
            tail_start=tail_start,
            first_segment_id=max(segment.id for segment in segments) + 1,
        )

        if not recovered_segments:
            logger.info(
                f"Keeping valid base Whisper transcription ending at "
                f"{last_word_end:.2f}s; focused tail recovery found no credible "
                "speech"
            )
            return segments

        logger.info(
            f"Recovered {len(recovered_segments)} credible Whisper segment(s) "
            "from the focused tail"
        )
        return [*segments, *recovered_segments]

    @staticmethod
    def _get_credible_tail_segments(
        tail_segments: list[TranscribedSegment],
        *,
        tail_start: float,
        first_segment_id: int,
    ) -> list[TranscribedSegment]:
        """Filter and shift credible segments from focused tail recovery.

        Arguments:
            tail_segments: transcription relative to the focused tail audio
            tail_start: focused tail start relative to the block audio
            first_segment_id: identifier assigned to the first recovered segment
        Returns:
            credible recovered segments shifted relative to the block audio
        """
        recovered_segments = []
        next_segment_id = first_segment_id
        for tail_segment in tail_segments:
            if (
                tail_segment.no_speech_prob is not None
                and tail_segment.no_speech_prob
                > _TAIL_RECOVERY_MAX_NO_SPEECH_PROBABILITY
            ):
                continue
            shifted_words = []
            for word in tail_segment.words or []:
                text = word.text.strip()
                if text and (
                    (word.end - word.start) / len(text)
                    > _TAIL_RECOVERY_MAX_SECONDS_PER_CHARACTER
                ):
                    continue
                shifted_words.append(
                    word.model_copy(
                        update={
                            "start": word.start + tail_start,
                            "end": word.end + tail_start,
                        }
                    )
                )
            if not any(word.text.strip() for word in shifted_words):
                continue
            recovered_segments.append(
                tail_segment.model_copy(
                    update={
                        "id": next_segment_id,
                        "start": shifted_words[0].start,
                        "end": shifted_words[-1].end,
                        "text": "".join(word.text for word in shifted_words),
                        "words": shifted_words,
                    },
                    deep=True,
                )
            )
            next_segment_id += 1
        return recovered_segments

    @staticmethod
    def _segments_are_usable(
        segments: list[TranscribedSegment],
        *,
        audio_duration: float | None = None,
    ) -> bool:
        """Determine whether transcribed segments are usable for alignment.

        Arguments:
            segments: transcribed segments to inspect
            audio_duration: original block audio duration in seconds
        Returns:
            whether the segments contain plausible nonempty text with word timings
        """
        has_text = False
        for segment in segments:
            if not segment.text.strip():
                continue
            has_text = True
            if not segment.words:
                logger.warning(
                    f"Rejecting Whisper segment {segment.id} without word timings"
                )
                return False
            if (
                segment.compression_ratio is not None
                and segment.compression_ratio > _MAX_COMPRESSION_RATIO
            ):
                logger.warning(
                    f"Rejecting repetitive Whisper segment {segment.id} with "
                    f"compression ratio {segment.compression_ratio:.2f} "
                    f"(maximum {_MAX_COMPRESSION_RATIO:.2f})"
                )
                return False
            if (
                audio_duration is not None
                and segment.end > audio_duration + _AUDIO_END_TOLERANCE_SECONDS
            ):
                logger.warning(
                    f"Rejecting Whisper segment {segment.id} ending at "
                    f"{segment.end:.2f}s beyond {audio_duration:.2f}s source audio"
                )
                return False

        if not has_text:
            logger.warning("Rejecting empty Whisper transcription")
            return False
        return True
