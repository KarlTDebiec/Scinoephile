#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reference-guided audio transcriber."""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from logging import getLogger

from pydub import AudioSegment
from pydub.effects import normalize

from scinoephile.audio.subtitles import AudioSeries, get_series_from_segments
from scinoephile.audio.transcription import (
    DemucsSeparator,
    MimoTranscriber,
    MimoTranscriptionError,
    TranscribedSegment,
    TranscriptionAlignmentError,
    WhisperTranscriber,
)
from scinoephile.common.validation import val_index_range
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series

from .aligner import TranscriptionAligner

__all__ = [
    "DemucsMode",
    "GuidedTranscriber",
    "TranscriptionBackend",
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


class TranscriptionBackend(StrEnum):
    """Audio transcription backends."""

    WHISPER = "whisper"
    """Transcribe using Whisper."""
    MIMO = "mimo"
    """Transcribe using MiMo."""


class VADMode(StrEnum):
    """Voice activity detection modes for transcription."""

    AUTO = "auto"
    """Use VAD automatically when needed."""
    ON = "on"
    """Always use VAD."""
    OFF = "off"
    """Never use VAD."""


class GuidedTranscriber:
    """Transcribe audio and align it with reference subtitles."""

    def __init__(
        self,
        *,
        language: Language,
        reference_language: Language,
        model_name: str,
        whisper_language: str,
        aligner: TranscriptionAligner,
        backend: TranscriptionBackend = TranscriptionBackend.WHISPER,
        demucs_mode: DemucsMode = DemucsMode.OFF,
        vad_mode: VADMode = VADMode.AUTO,
        mimo_transcriber: MimoTranscriber | None = None,
        segment_splitter: TranscribedSegmentSplitter | None = None,
    ):
        """Initialize.

        Arguments:
            language: transcription language
            reference_language: reference subtitle language
            model_name: Whisper model name used for transcription
            whisper_language: language code passed to Whisper
            aligner: transcription aligner
            backend: audio transcription backend
            demucs_mode: Demucs preprocessing mode
            vad_mode: voice activity detection mode
            mimo_transcriber: MiMo transcriber when MiMo is selected
            segment_splitter: optional strategy for splitting transcribed segments
        """
        self.language = language
        self.reference_language = reference_language
        self.model_name = model_name
        self.whisper_language = whisper_language
        self.aligner = aligner
        self.backend = backend
        self.demucs_mode = demucs_mode
        self.vad_mode = vad_mode
        self.mimo_transcriber = mimo_transcriber
        self.segment_splitter = segment_splitter

        self.demucs_separator = None
        if backend != TranscriptionBackend.MIMO and demucs_mode in (
            DemucsMode.AUTO,
            DemucsMode.ON,
        ):
            self.demucs_separator = DemucsSeparator(
                cache_dir_path=get_runtime_cache_dir_path("demucs")
            )
        self.vad_transcriber = None
        self.no_vad_transcriber = None
        self.unseparated_vad_transcriber = None
        self.unseparated_no_vad_transcriber = None
        self.recovery_transcriber = None
        self.tail_recovery_transcriber = None
        if backend == TranscriptionBackend.MIMO:
            if mimo_transcriber is None:
                raise ValueError("MiMo backend requires a MiMo transcriber.")
            return

        primary_uses_demucs = demucs_mode in (DemucsMode.AUTO, DemucsMode.ON)
        if vad_mode in (VADMode.AUTO, VADMode.ON):
            self.vad_transcriber = self._get_whisper_transcriber(
                use_demucs=primary_uses_demucs,
                use_vad=True,
            )
        if vad_mode in (VADMode.AUTO, VADMode.OFF):
            self.no_vad_transcriber = self._get_whisper_transcriber(
                use_demucs=primary_uses_demucs,
                use_vad=False,
            )

        if demucs_mode == DemucsMode.AUTO and vad_mode in (
            VADMode.AUTO,
            VADMode.ON,
        ):
            self.unseparated_vad_transcriber = self._get_whisper_transcriber(
                use_demucs=False,
                use_vad=True,
            )
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
        *,
        start_at_idx: int = 0,
    ) -> AudioSeries:
        """Transcribe all audio blocks and align them with reference subtitles.

        Arguments:
            audio_series: audio divided into subtitle-timed blocks
            reference_series: reference subtitles corresponding to audio blocks
            stop_at_idx: exclusive zero-based block index at which to stop processing
            start_at_idx: inclusive zero-based block index at which to start processing
        Returns:
            transcribed and aligned audio subtitle series
        Raises:
            ScinoephileError: if audio and reference block counts differ
            ValueError: if the processing range is invalid
        """
        audio_blocks = audio_series.blocks
        reference_blocks = reference_series.blocks
        if len(audio_blocks) != len(reference_blocks):
            raise ScinoephileError(
                f"Audio has {len(audio_blocks)} blocks but reference subtitles have "
                f"{len(reference_blocks)} blocks."
            )
        block_range = val_index_range(len(audio_blocks), start_at_idx, stop_at_idx)
        if (
            self.aligner.delineation_processor.prune_test_cases
            or self.aligner.punctuation_processor.prune_test_cases
        ) and block_range != range(len(audio_blocks)):
            raise ValueError(
                "Cannot prune test cases while processing only a subset of blocks."
            )

        output_events = []
        for block_idx in block_range:
            audio_block = audio_blocks[block_idx]
            reference_block = reference_blocks[block_idx]
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
        self.aligner.update_all_test_cases()
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
        return alignment.transcription

    def _get_cached_block_transcription(
        self,
        cache_audio: AudioSegment,
        *,
        audio_duration: float,
    ) -> tuple[list[TranscribedSegment] | None, set[WhisperTranscriber]]:
        """Get cached block transcription before expensive preprocessing.

        Arguments:
            cache_audio: original block audio used for cache-key generation
            audio_duration: original block audio duration in seconds
        Returns:
            cached transcription, if usable, and transcribers with unusable caches
        """
        rejected_transcribers: set[WhisperTranscriber] = set()
        transcribers = list(self._get_standard_transcribers())
        if self.demucs_mode == DemucsMode.AUTO:
            transcribers.extend(self._get_standard_transcribers(unseparated=True))
        assert self.recovery_transcriber is not None
        transcribers.append(self.recovery_transcriber)
        for transcriber in transcribers:
            cached_segments = transcriber.get_cached_transcription(cache_audio)
            if cached_segments is None:
                continue
            if self._segments_are_usable(
                cached_segments,
                audio_duration=audio_duration,
            ):
                return cached_segments, rejected_transcribers
            if transcriber is not self.recovery_transcriber:
                rejected_transcribers.add(transcriber)
        return None, rejected_transcribers

    def _get_standard_transcribers(
        self,
        *,
        unseparated: bool = False,
    ) -> tuple[WhisperTranscriber, ...]:
        """Get standard transcribers in configured retry order.

        Arguments:
            unseparated: whether to return original-audio retry transcribers
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
                f"Demucs separation failed in automatic mode; retrying with "
                f"original audio: {exc}"
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
        """
        if self.backend == TranscriptionBackend.MIMO:
            return self._transcribe_block_audio_with_mimo(audio)

        cache_audio = audio
        audio_duration = len(cache_audio) / 1000
        segments, rejected_transcribers = self._get_cached_block_transcription(
            cache_audio,
            audio_duration=audio_duration,
        )
        if segments is None:
            segments = self._transcribe_with_whisper_candidates(
                audio,
                cache_audio=cache_audio,
                audio_duration=audio_duration,
                rejected_transcribers=rejected_transcribers,
            )
        if segments is None:
            logger.warning(
                "No configured transcription attempt produced usable output; leaving "
                "this block empty for downstream gap translation"
            )
            return []
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
        """Run and validate one transcription candidate.

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
        except (AssertionError, ImportError) as exc:
            logger.warning(
                f"{type(transcriber).__name__} transcription candidate failed: {exc}"
            )
            return None
        if self._segments_are_usable(
            segments,
            audio_duration=audio_duration,
        ):
            return segments
        return None

    def _transcribe_block_audio_with_mimo(
        self,
        audio: AudioSegment,
    ) -> list[TranscribedSegment]:
        """Transcribe one block using only MiMo.

        Arguments:
            audio: block audio to transcribe
        Returns:
            usable transcribed segments, or an empty list when none are produced
        """
        assert self.mimo_transcriber is not None
        audio_duration = len(audio) / 1000

        def is_usable(segments: list[TranscribedSegment]) -> bool:
            """Determine whether a MiMo attempt is usable for guided alignment."""
            return self._segments_are_usable(
                segments,
                audio_duration=audio_duration,
            )

        try:
            segments = self.mimo_transcriber(
                audio,
                cache_audio=audio,
                is_usable=is_usable,
            )
        except (
            AssertionError,
            ImportError,
            MimoTranscriptionError,
            TranscriptionAlignmentError,
        ) as exc:
            logger.warning(f"MiMo transcription failed: {exc}")
        else:
            if is_usable(segments):
                return segments

        logger.warning(
            "MiMo did not produce usable output; leaving this block empty for "
            "downstream gap translation"
        )
        return []

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

        assert self.tail_recovery_transcriber is not None

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
        unusable_cached_tail = (
            tail_segments is not None
            and not self._segments_are_usable(
                tail_segments,
                audio_duration=tail_audio_duration,
            )
        )
        if unusable_cached_tail:
            logger.info(
                f"Keeping valid base Whisper transcription ending at "
                f"{last_word_end:.2f}s after unusable cached focused tail recovery"
            )

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
        if tail_segments is None or unusable_cached_tail:
            if not recovery_failed_with_assertion and not unusable_cached_tail:
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

    def _transcribe_with_whisper_candidates(
        self,
        audio: AudioSegment,
        *,
        cache_audio: AudioSegment,
        audio_duration: float,
        rejected_transcribers: set[WhisperTranscriber],
    ) -> list[TranscribedSegment] | None:
        """Try each configured Whisper candidate in recovery order.

        Arguments:
            audio: original block audio to transcribe
            cache_audio: original audio used for cache-key generation
            audio_duration: original block audio duration in seconds
            rejected_transcribers: transcribers with unusable cached output
        Returns:
            usable transcribed segments, if produced
        """
        primary_audio = self._get_primary_transcription_audio(audio)
        if primary_audio is not None:
            for transcriber in (
                candidate
                for candidate in self._get_standard_transcribers()
                if candidate not in rejected_transcribers
            ):
                segments = self._transcribe_with_candidate(
                    transcriber,
                    primary_audio,
                    cache_audio=cache_audio,
                    audio_duration=audio_duration,
                )
                if segments is not None:
                    return segments

        if self.demucs_mode == DemucsMode.AUTO:
            if primary_audio is not None:
                logger.info(
                    "Retrying block transcription with original audio after "
                    "unusable Demucs result"
                )
            for transcriber in (
                candidate
                for candidate in self._get_standard_transcribers(unseparated=True)
                if candidate not in rejected_transcribers
            ):
                segments = self._transcribe_with_candidate(
                    transcriber,
                    audio,
                    cache_audio=cache_audio,
                    audio_duration=audio_duration,
                )
                if segments is not None:
                    return segments

        assert self.recovery_transcriber is not None
        if self.recovery_transcriber in rejected_transcribers:
            return None
        logger.info("Retrying block transcription with defensive Whisper decoding")
        recovery_audio = audio
        if self.demucs_mode == DemucsMode.ON:
            assert primary_audio is not None
            recovery_audio = primary_audio
        return self._transcribe_with_candidate(
            self.recovery_transcriber,
            recovery_audio,
            cache_audio=cache_audio,
            audio_duration=audio_duration,
        )

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
                    f"Rejecting transcription segment {segment.id} without word timings"
                )
                return False
            duration_error = None
            if int(segment.end * 1000) <= int(segment.start * 1000):
                duration_error = (
                    f"Rejecting transcription segment {segment.id} with non-positive "
                    f"millisecond duration ({segment.start:.3f}s to "
                    f"{segment.end:.3f}s)"
                )
            else:
                for word in segment.words:
                    if not word.text.strip():
                        continue
                    if int(word.end * 1000) <= int(word.start * 1000):
                        duration_error = (
                            f"Rejecting transcription segment {segment.id} with word "
                            f"{word.text!r} having non-positive millisecond duration "
                            f"({word.start:.3f}s to {word.end:.3f}s)"
                        )
                        break
            if duration_error is not None:
                logger.warning(duration_error)
                return False
            if (
                segment.compression_ratio is not None
                and segment.compression_ratio > _MAX_COMPRESSION_RATIO
            ):
                logger.warning(
                    f"Rejecting repetitive transcription segment {segment.id} with "
                    f"compression ratio {segment.compression_ratio:.2f} "
                    f"(maximum {_MAX_COMPRESSION_RATIO:.2f})"
                )
                return False
            if (
                audio_duration is not None
                and segment.end > audio_duration + _AUDIO_END_TOLERANCE_SECONDS
            ):
                logger.warning(
                    f"Rejecting transcription segment {segment.id} ending at "
                    f"{segment.end:.2f}s beyond {audio_duration:.2f}s source audio"
                )
                return False

        if not has_text:
            logger.warning("Rejecting empty transcription")
            return False
        return True
