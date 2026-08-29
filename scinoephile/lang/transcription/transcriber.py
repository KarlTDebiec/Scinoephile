#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reference-guided audio transcriber."""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from logging import getLogger
from pathlib import Path
from statistics import median

from pydub import AudioSegment
from pydub.effects import normalize

from scinoephile.audio.subtitles import AudioSeries, get_series_from_segments
from scinoephile.audio.transcription import (
    CtcAligner,
    DemucsMode,
    MlxAudioTranscriber,
    TranscribedSegment,
    TranscribedWord,
    TranscriptionError,
    VadMode,
    WhisperModel,
    WhisperTranscriber,
    get_segment_split_at_idx,
    get_segment_split_on_word_timings,
)
from scinoephile.audio.transcription.mlx_audio.model_spec import MlxAudioModelSpec
from scinoephile.audio.transcription.quality import get_transcription_quality_issue
from scinoephile.audio.transcription.whisper.model_spec import WhisperModelSpec
from scinoephile.common.validation import val_index_range
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.core.text import FULL_PUNC_CHARS, HALF_PUNC_CHARS

from .aligner import TranscriptionAligner

__all__ = [
    "GuidedTranscriber",
    "MlxAudioTimingMode",
    "TranscribedSegmentSplitter",
    "TranscriptionModel",
    "get_segment_split_on_phrase_timings",
]


TranscribedSegmentSplitter = Callable[[TranscribedSegment], list[TranscribedSegment]]
"""Callable that splits one transcribed segment into zero or more segments."""

logger = getLogger(__name__)

_EXPECTED_TAIL_TOLERANCE_SECONDS = 1.0
"""Gap before the final guided subtitle that triggers focused recovery."""

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

_LEXICAL_INFIX_PUNCTUATION = {
    "'",
    "-",
    ".",
    "/",
    ":",
    "‐",
    "–",
    "’",
    "．",
    "：",
    "－",
    "／",
    "＇",
    "﹣",
}
"""Punctuation preserved between ASCII alphanumeric characters."""

_MLX_PHRASE_MAX_CHARACTERS = 12
"""Maximum characters retained in one phrase-level MLX timing unit."""

_MLX_PHRASE_MIN_CHARACTERS = 2
"""Minimum preferred characters in one phrase-level MLX timing unit."""

_MLX_PHRASE_PAUSE_RATIO = 2.5
"""Median-duration multiple treated as phrase-final CTC hold time."""

_MLX_PHRASE_PAUSE_SECONDS = 0.6
"""Minimum absolute CTC hold time treated as phrase-final."""

_MLX_PHRASE_TARGET_CHARACTERS = 7
"""Preferred characters in one phrase-level MLX timing unit."""

_MLX_PHRASE_STRONG_PUNCTUATION = set(".!?;。！？；…")
"""Sentence punctuation treated as a strong phrase boundary."""

_MLX_PHRASE_WEAK_PUNCTUATION = set(",:，：、")
"""Clause punctuation treated as a weak phrase boundary."""


class MlxAudioTimingMode(StrEnum):
    """Granularity of CTC timing units exposed for MLX-Audio alignment."""

    SEGMENT = "segment"
    """Retain complete MLX-Audio transcription segments."""
    PHRASE = "phrase"
    """Group CTC timing units into pause- and punctuation-aware phrases."""
    CTC_UNIT = "ctc-unit"
    """Expose every individually timed CTC unit."""


class TranscriptionModel(StrEnum):
    """Supported transcription models."""

    WHISPER = "whisper"
    """Transcribe using Whisper."""
    MIMO = "mimo"
    """Transcribe using MiMo through MLX-Audio."""
    QWEN3_ASR = "qwen3-asr"
    """Transcribe using Qwen3-ASR through MLX-Audio."""
    GLM_ASR = "glm-asr"
    """Transcribe using GLM-ASR through MLX-Audio."""
    FIRERED_ASR2 = "firered-asr2"
    """Transcribe using FireRedASR2 through MLX-Audio."""
    SENSEVOICE = "sensevoice"
    """Transcribe using SenseVoice through MLX-Audio."""


class GuidedTranscriber:
    """Transcribe audio and align it with reference subtitles."""

    def __init__(
        self,
        *,
        language: Language,
        guide_language: Language,
        audio_model: WhisperModelSpec | MlxAudioModelSpec,
        aligner: TranscriptionAligner,
        demucs_mode: DemucsMode = DemucsMode.OFF,
        vad_mode: VadMode = VadMode.OFF,
        cache_root_path: Path | None = None,
        overwrite_cache: bool = False,
        mlx_audio_transcriber: MlxAudioTranscriber | None = None,
        mlx_audio_timing_mode: MlxAudioTimingMode = MlxAudioTimingMode.CTC_UNIT,
        segment_splitter: TranscribedSegmentSplitter | None = None,
        strip_generated_punctuation: bool = False,
    ):
        """Initialize.

        Arguments:
            language: transcription language
            guide_language: guide subtitle language
            audio_model: configured transcription model
            aligner: transcription aligner
            demucs_mode: Demucs preprocessing mode
            vad_mode: voice activity detection mode
            cache_root_path: cache root directory path
            overwrite_cache: whether to replace matching generated cache files
            mlx_audio_transcriber: configured MLX-Audio transcriber, when selected
            mlx_audio_timing_mode: granularity of MLX-Audio CTC timing units
            segment_splitter: optional strategy for splitting transcribed segments
            strip_generated_punctuation: whether to remove generated sentence
                punctuation after timing and before guided alignment
        """
        self.language = language
        self.guide_language = guide_language
        self.audio_model = audio_model
        self.model_name = audio_model.name
        self.aligner = aligner
        self.demucs_mode = demucs_mode
        self.vad_mode = vad_mode
        self.mlx_audio_transcriber = mlx_audio_transcriber
        self.mlx_audio_timing_mode = mlx_audio_timing_mode
        self.segment_splitter = segment_splitter
        self.strip_generated_punctuation = strip_generated_punctuation

        # Use MLX-Audio's shared preprocessing fallbacks without Whisper recovery
        if isinstance(self.audio_model, MlxAudioModelSpec):
            if self.mlx_audio_transcriber is None:
                raise ValueError("MLX-Audio backend requires a MLX-Audio transcriber.")
            self.transcriber = self.mlx_audio_transcriber
            self.recovery_transcriber = None
            self.tail_recovery_transcriber = None
            return

        # Configure standard preprocessing fallbacks
        if not isinstance(self.audio_model, WhisperModelSpec):
            raise ValueError("Whisper backend requires a Whisper model.")
        whisper_ctc_aligner = CtcAligner(
            self.language,
            cache_root_path=cache_root_path,
            overwrite_cache=overwrite_cache,
        )
        whisper_model = WhisperModel(self.audio_model, self.language)
        self.transcriber = WhisperTranscriber(
            model=whisper_model,
            language=self.language,
            demucs_mode=self.demucs_mode,
            vad_mode=self.vad_mode,
            cache_root_path=cache_root_path,
            overwrite_cache=overwrite_cache,
            ctc_aligner=whisper_ctc_aligner,
        )

        # Configure defensive decoding after standard attempts are exhausted
        recovery_demucs_mode = DemucsMode.OFF
        if self.demucs_mode is DemucsMode.ON:
            recovery_demucs_mode = DemucsMode.ON
        recovery_vad_mode = VadMode.OFF
        if self.vad_mode is VadMode.ON:
            recovery_vad_mode = VadMode.ON
        self.recovery_transcriber = WhisperTranscriber(
            model=whisper_model,
            language=self.language,
            demucs_mode=recovery_demucs_mode,
            vad_mode=recovery_vad_mode,
            cache_root_path=cache_root_path,
            overwrite_cache=overwrite_cache,
            temperature=_RECOVERY_TEMPERATURES,
            condition_on_previous_text=False,
            ctc_aligner=whisper_ctc_aligner,
            demucs_separator=self.transcriber.demucs_separator,
        )

        # Configure focused recovery for missing speech near a guided tail
        self.tail_recovery_transcriber = WhisperTranscriber(
            model=whisper_model,
            language=self.language,
            demucs_mode=DemucsMode.OFF,
            vad_mode=VadMode.OFF,
            cache_root_path=cache_root_path,
            overwrite_cache=overwrite_cache,
            condition_on_previous_text=False,
            ctc_aligner=whisper_ctc_aligner,
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
        self, audio_block: AudioSeries, reference_block: Series
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
        expected_last_start = max(0.0, (reference_block[-1].start - offset) / 1000)
        segments = self._transcribe_block_audio(
            audio_block.audio, expected_last_start=expected_last_start
        )
        if self.segment_splitter is None:
            split_segments = segments
        else:
            split_segments = []
            for segment in segments:
                split_segments.extend(self.segment_splitter(segment))

        # Expose the configured MLX-Audio timing granularity to guided alignment
        if isinstance(self.audio_model, MlxAudioModelSpec):
            timed_segments = []
            for segment in split_segments:
                if self.mlx_audio_timing_mode is MlxAudioTimingMode.SEGMENT:
                    timed_segments.append(segment)
                elif self.mlx_audio_timing_mode is MlxAudioTimingMode.PHRASE:
                    timed_segments.extend(get_segment_split_on_phrase_timings(segment))
                else:
                    timed_segments.extend(get_segment_split_on_word_timings(segment))
            split_segments = [
                segment.model_copy(update={"id": segment_idx})
                for segment_idx, segment in enumerate(timed_segments)
            ]

        if self.strip_generated_punctuation:
            split_segments = [
                _get_segment_without_generated_punctuation(segment)
                for segment in split_segments
            ]
            split_segments = [
                segment for segment in split_segments if segment.text.strip()
            ]
        transcription_block = get_series_from_segments(
            split_segments, audio=audio_block.audio, offset=offset
        )
        alignment = self.aligner.align(reference_block, transcription_block)
        return alignment.transcription

    def _transcribe_block_audio(
        self, audio: AudioSegment, *, expected_last_start: float | None = None
    ) -> list[TranscribedSegment]:
        """Transcribe one block of audio with the configured VAD behavior.

        Arguments:
            audio: block audio to transcribe
            expected_last_start: expected start of the final guided subtitle
        Returns:
            transcribed segments
        """
        if isinstance(self.audio_model, MlxAudioModelSpec):
            return self._transcribe_block_audio_with_mlx_audio(audio)

        audio_duration = len(audio) / 1000

        def is_usable(candidate: list[TranscribedSegment]) -> bool:
            """Determine whether a transcription candidate is usable."""
            return self._segments_are_usable(candidate, audio_duration=audio_duration)

        # Inspect standard and recovery caches before invoking Demucs
        assert self.recovery_transcriber is not None
        segments = self.transcriber.get_cached_transcription(audio, is_usable=is_usable)
        if segments is None:
            segments = self.recovery_transcriber.get_cached_transcription(
                audio, is_usable=is_usable
            )

        # Run standard fallbacks, followed by defensive decoding
        if segments is None:
            try:
                segments = self.transcriber(audio, is_usable=is_usable)
            except TranscriptionError as exc:
                logger.warning(f"Whisper transcription attempts failed: {exc}")
                segments = []
        if not segments:
            logger.info("Retrying block transcription with defensive Whisper decoding")
            try:
                segments = self.recovery_transcriber(audio, is_usable=is_usable)
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
            segments, audio, expected_last_start=expected_last_start
        )

    def _transcribe_block_audio_with_mlx_audio(
        self, audio: AudioSegment
    ) -> list[TranscribedSegment]:
        """Transcribe one block using MLX-Audio.

        Arguments:
            audio: block audio to transcribe
        Returns:
            usable transcribed segments, or an empty list when none are produced
        """
        assert self.mlx_audio_transcriber is not None
        audio_duration = len(audio) / 1000

        def is_usable(segments: list[TranscribedSegment]) -> bool:
            """Determine whether an MLX-Audio attempt is usable."""
            return self._segments_are_usable(segments, audio_duration=audio_duration)

        try:
            segments = self.mlx_audio_transcriber(audio, is_usable=is_usable)
        except TranscriptionError as exc:
            logger.warning(f"MLX-Audio transcription failed: {exc}")
        else:
            if segments:
                return segments

        logger.warning(
            "MLX-Audio did not produce usable output; leaving this block empty for "
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
        assert self.tail_recovery_transcriber is not None
        last_word_end = max(
            word.end for segment in segments for word in (segment.words or [])
        )
        if (
            expected_last_start is None
            or last_word_end + _EXPECTED_TAIL_TOLERANCE_SECONDS >= expected_last_start
        ):
            return segments

        tail_start = max(
            last_word_end, expected_last_start - _TAIL_RECOVERY_CONTEXT_SECONDS
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
            tail_audio, headroom=_TAIL_RECOVERY_HEADROOM_DB
        )
        tail_audio_duration = len(normalized_tail_audio) / 1000
        try:
            tail_segments = self.tail_recovery_transcriber(
                normalized_tail_audio,
                is_usable=lambda candidate: self._segments_are_usable(
                    candidate, audio_duration=tail_audio_duration
                ),
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
            tail_segments, tail_start, max(segment.id for segment in segments) + 1
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
        segments: list[TranscribedSegment], *, audio_duration: float | None = None
    ) -> bool:
        """Determine whether transcribed segments are usable for alignment.

        Arguments:
            segments: transcribed segments to inspect
            audio_duration: original block audio duration in seconds
        Returns:
            whether the segments contain plausible nonempty text with word timings
        """
        issue = get_transcription_quality_issue(
            segments, audio_duration_seconds=audio_duration
        )
        if issue is None:
            return True
        logger.warning(f"Rejecting transcription: {issue}")
        return False


def get_segment_split_on_phrase_timings(
    segment: TranscribedSegment,
) -> list[TranscribedSegment]:
    """Split an MLX-Audio segment into phrase-sized CTC timing groups.

    CTC blank frames are represented as held duration on neighboring timing units,
    so unusually long unit durations provide pause evidence even when consecutive
    units have no literal timestamp gap.

    Arguments:
        segment: CTC-aligned MLX-Audio segment
    Returns:
        transcribed segments grouped into phrase-level timing units
    """
    words = segment.words
    if not words or len(segment.text) <= _MLX_PHRASE_MIN_CHARACTERS:
        return [segment]
    if "".join(word.text for word in words) != segment.text:
        return [segment]

    durations = [max(word.end - word.start, 0.0) for word in words]
    pause_threshold = max(
        _MLX_PHRASE_PAUSE_SECONDS, median(durations) * _MLX_PHRASE_PAUSE_RATIO
    )
    boundary_scores = _get_phrase_boundary_scores(
        segment.text, words, durations, pause_threshold
    )

    # Select phrase boundaries while retaining short genuine utterances
    split_offsets: list[int] = []
    phrase_start = 0
    text_length = len(segment.text)
    while text_length - phrase_start > _MLX_PHRASE_MIN_CHARACTERS:
        minimum_offset = phrase_start + _MLX_PHRASE_MIN_CHARACTERS
        maximum_offset = min(
            phrase_start + _MLX_PHRASE_MAX_CHARACTERS,
            text_length - _MLX_PHRASE_MIN_CHARACTERS,
        )
        hard_offsets = [
            offset
            for offset, score in boundary_scores.items()
            if minimum_offset <= offset <= maximum_offset and score >= 3
        ]
        if hard_offsets:
            split_offset = min(hard_offsets)
        elif text_length - phrase_start <= _MLX_PHRASE_MAX_CHARACTERS:
            break
        else:
            candidate_offsets = [
                offset
                for offset in boundary_scores
                if minimum_offset <= offset <= maximum_offset
            ]
            if candidate_offsets:
                split_offset = max(
                    candidate_offsets,
                    key=lambda offset: (
                        boundary_scores[offset],
                        -abs(offset - phrase_start - _MLX_PHRASE_TARGET_CHARACTERS),
                    ),
                )
            else:
                split_offset = phrase_start + _MLX_PHRASE_TARGET_CHARACTERS
        split_offsets.append(split_offset)
        phrase_start = split_offset
    if not split_offsets:
        return [segment]

    # Split through the existing character-aware timing helper
    output: list[TranscribedSegment] = []
    remaining = segment
    previous_offset = 0
    for split_offset in split_offsets:
        first, remaining = get_segment_split_at_idx(
            remaining, split_offset - previous_offset
        )
        output.append(first)
        previous_offset = split_offset
    output.append(remaining)
    return output


def _get_phrase_boundary_scores(
    text: str,
    words: list[TranscribedWord],
    durations: list[float],
    pause_threshold: float,
) -> dict[int, int]:
    """Score phrase boundaries using punctuation and CTC hold durations."""
    boundary_scores: dict[int, int] = {}
    for character_index, character in enumerate(text, 1):
        if character in _MLX_PHRASE_STRONG_PUNCTUATION:
            boundary_scores[character_index] = 4
        elif character in _MLX_PHRASE_WEAK_PUNCTUATION:
            boundary_scores[character_index] = 2

    character_offset = 0
    for word, duration in zip(words, durations, strict=True):
        character_offset += len(word.text)
        boundary_scores.setdefault(character_offset, 1)
        if duration >= pause_threshold:
            boundary_scores[character_offset] = max(
                boundary_scores[character_offset], 3
            )
    return boundary_scores


def _get_segment_without_generated_punctuation(
    segment: TranscribedSegment,
) -> TranscribedSegment:
    """Remove generated punctuation from segment text and word timing data.

    Arguments:
        segment: timed transcription segment
    Returns:
        segment whose text and word data use matching character offsets
    """
    keep_characters = _get_text_character_retention(segment.text)
    text = _strip_generated_punctuation(segment.text)
    if not segment.words:
        return segment.model_copy(update={"text": text})

    # Apply the segment-level retention map to its corresponding timed words
    word_text = "".join(word.text for word in segment.words)
    if word_text == segment.text:
        words: list[TranscribedWord] = []
        character_offset = 0
        for word in segment.words:
            word_end = character_offset + len(word.text)
            retained_word_text = "".join(
                character
                for character, keep_character in zip(
                    word.text, keep_characters[character_offset:word_end], strict=True
                )
                if keep_character
            )
            if retained_word_text:
                words.append(word.model_copy(update={"text": retained_word_text}))
            character_offset = word_end
        return segment.model_copy(update={"text": text, "words": words})

    # Preserve safe offsets when backend word text cannot be mapped character-wise
    words = []
    if text:
        words.append(
            TranscribedWord(
                text=text,
                start=segment.start,
                end=segment.end,
                confidence=min(word.confidence for word in segment.words),
            )
        )
    return segment.model_copy(update={"text": text, "words": words})


def _get_text_character_retention(text: str) -> list[bool]:
    """Identify characters retained when removing generated punctuation.

    Arguments:
        text: timed transcription text
    Returns:
        whether each character should be retained
    """
    punctuation = HALF_PUNC_CHARS | FULL_PUNC_CHARS
    output: list[bool] = []
    for index, character in enumerate(text):
        keep_character = character not in punctuation
        if (
            character in _LEXICAL_INFIX_PUNCTUATION
            and 0 < index < len(text) - 1
            and text[index - 1].isascii()
            and text[index - 1].isalnum()
            and text[index + 1].isascii()
            and text[index + 1].isalnum()
        ):
            keep_character = True
        output.append(keep_character)
    return output


def _strip_generated_punctuation(text: str) -> str:
    """Remove generated punctuation while retaining ASCII lexical infixes.

    Arguments:
        text: timed transcription text
    Returns:
        text without generated sentence punctuation
    """
    return "".join(
        character
        for character, keep_character in zip(
            text, _get_text_character_retention(text), strict=True
        )
        if keep_character
    )
