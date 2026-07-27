#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reference-guided audio transcriber."""

from __future__ import annotations

from collections.abc import Callable
from logging import getLogger
from pathlib import Path

from pydub import AudioSegment
from pydub.effects import normalize

from scinoephile.audio.subtitles import AudioSeries, get_series_from_segments
from scinoephile.audio.transcription import (
    DemucsMode,
    TranscribedSegment,
    TranscriptionError,
    VADMode,
    WhisperTranscriber,
)
from scinoephile.common.validation import val_index_range
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series

from .aligner import TranscriptionAligner

__all__ = [
    "GuidedTranscriber",
    "TranscribedSegmentSplitter",
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


class GuidedTranscriber:
    """Transcribe audio and align it with reference subtitles."""

    def __init__(
        self,
        *,
        language: Language,
        guide_language: Language,
        model_name: str,
        whisper_language: str,
        aligner: TranscriptionAligner,
        demucs_mode: DemucsMode = DemucsMode.AUTO,
        vad_mode: VADMode = VADMode.AUTO,
        cache_dir_path: Path | None = None,
        overwrite_cache: bool = False,
        segment_splitter: TranscribedSegmentSplitter | None = None,
    ):
        """Initialize.

        Arguments:
            language: transcription language
            guide_language: guide subtitle language
            model_name: Whisper model name used for transcription
            whisper_language: language code passed to Whisper
            aligner: transcription aligner
            demucs_mode: Demucs preprocessing mode
            vad_mode: Whisper VAD mode
            cache_dir_path: cache root directory path
            overwrite_cache: whether to replace matching generated cache files
            segment_splitter: optional strategy for splitting Whisper segments
        """
        self.language = language
        self.guide_language = guide_language
        self.model_name = model_name
        self.whisper_language = whisper_language
        self.aligner = aligner
        self.demucs_mode = demucs_mode
        self.vad_mode = vad_mode
        if cache_dir_path is None:
            cache_dir_path = get_runtime_cache_dir_path(create=False)
        self.cache_dir_path = cache_dir_path
        self.overwrite_cache = overwrite_cache
        self.segment_splitter = segment_splitter

        # Configure standard preprocessing fallbacks
        self.transcriber = WhisperTranscriber(
            model_name=self.model_name,
            language=self.whisper_language,
            demucs_mode=self.demucs_mode,
            vad_mode=self.vad_mode,
            cache_root_path=self.cache_dir_path,
        )

        # Configure defensive decoding after standard attempts are exhausted
        recovery_demucs_mode = DemucsMode.OFF
        if self.demucs_mode is DemucsMode.ON:
            recovery_demucs_mode = DemucsMode.ON
        recovery_vad_mode = VADMode.OFF
        if self.vad_mode is VADMode.ON:
            recovery_vad_mode = VADMode.ON
        self.recovery_transcriber = WhisperTranscriber(
            model_name=self.model_name,
            language=self.whisper_language,
            demucs_mode=recovery_demucs_mode,
            vad_mode=recovery_vad_mode,
            cache_root_path=self.cache_dir_path,
            temperature=_RECOVERY_TEMPERATURES,
            condition_on_previous_text=False,
        )

        # Configure focused recovery for missing speech near a guided tail
        self.tail_recovery_transcriber = WhisperTranscriber(
            model_name=self.model_name,
            language=self.whisper_language,
            demucs_mode=DemucsMode.OFF,
            vad_mode=VADMode.OFF,
            cache_root_path=self.cache_dir_path,
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
                f"REFERENCE ({self.guide_language.code}):\n"
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
        audio_duration = len(audio) / 1000

        def is_usable(candidate: list[TranscribedSegment]) -> bool:
            """Determine whether a transcription candidate is usable."""
            return self._segments_are_usable(
                candidate,
                audio_duration=audio_duration,
            )

        # Inspect or clear recovery caches before invoking Demucs
        segments = None
        if self.overwrite_cache:
            self.recovery_transcriber.remove_cached_transcriptions(audio)
        else:
            segments = self.transcriber.get_cached_transcription(
                audio,
                is_usable=is_usable,
            )
            if segments is None:
                segments = self.recovery_transcriber.get_cached_transcription(
                    audio,
                    is_usable=is_usable,
                )

        # Run standard fallbacks, followed by defensive decoding
        if segments is None:
            try:
                segments = self.transcriber(
                    audio,
                    is_usable=is_usable,
                    overwrite_cache=self.overwrite_cache,
                )
            except TranscriptionError as exc:
                logger.warning(f"Whisper transcription attempts failed: {exc}")
                segments = []
        if not segments:
            logger.info("Retrying block transcription with defensive Whisper decoding")
            try:
                segments = self.recovery_transcriber(
                    audio,
                    is_usable=is_usable,
                )
            except TranscriptionError as exc:
                logger.warning(f"Defensive Whisper decoding failed: {exc}")
                segments = []
        if not segments:
            logger.warning(
                "Whisper produced no usable transcription after all configured "
                "recovery attempts; leaving this block empty for downstream gap "
                "translation"
            )
            return []
        return self._transcribe_with_focused_tail_recovery(
            segments,
            audio,
            expected_last_start=expected_last_start,
        )

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
        last_word_end = max(
            word.end for segment in segments for word in (segment.words or [])
        )
        if (
            expected_last_start is None
            or last_word_end + _EXPECTED_TAIL_TOLERANCE_SECONDS >= expected_last_start
        ):
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
        try:
            tail_segments = self.tail_recovery_transcriber(
                normalized_tail_audio,
                is_usable=lambda candidate: self._segments_are_usable(
                    candidate,
                    audio_duration=tail_audio_duration,
                ),
                overwrite_cache=self.overwrite_cache,
            )
        except TranscriptionError as exc:
            logger.warning(
                f"Keeping valid base Whisper transcription after focused tail "
                f"recovery failed: {exc}"
            )
            return segments
        if not tail_segments:
            logger.info(
                f"Keeping valid base Whisper transcription ending at "
                f"{last_word_end:.2f}s after unusable focused tail recovery"
            )
            return segments

        recovered_segments = self._get_credible_tail_segments(
            tail_segments,
            tail_start,
            max(segment.id for segment in segments) + 1,
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
                logger.warning(f"Rejecting segment {segment.id} without word timings")
                return False
            if int(segment.end * 1000) <= int(segment.start * 1000):
                logger.warning(
                    f"Rejecting Whisper segment {segment.id} with non-positive "
                    f"millisecond duration ({segment.start:.3f}s to "
                    f"{segment.end:.3f}s)"
                )
                return False
            for word in segment.words:
                if not word.text.strip():
                    continue
                if int(word.end * 1000) <= int(word.start * 1000):
                    logger.warning(
                        f"Rejecting Whisper segment {segment.id} with word "
                        f"{word.text!r} having non-positive millisecond duration "
                        f"({word.start:.3f}s to {word.end:.3f}s)"
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
        return has_text
