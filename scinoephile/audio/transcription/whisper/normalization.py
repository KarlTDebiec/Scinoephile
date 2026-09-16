#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Normalizes malformed or unusable Whisper transcription output."""

from __future__ import annotations

from collections.abc import Sequence
from itertools import groupby
from logging import getLogger
from pathlib import Path

from scinoephile.audio.transcription.quality import (
    MAX_COMPRESSION_RATIO,
    get_text_compression_ratio,
    get_transcription_quality_issue,
)
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment

__all__ = ["SUBTITLE_CREDIT_HALLUCINATION_MARKERS", "normalize_segments"]

SUBTITLE_CREDIT_HALLUCINATION_MARKERS = ("amara.org", "字幕由", "字幕提供者")
"""Markers indicating an ASR-generated subtitle-credit hallucination."""

_SUBTITLE_CREDIT_MIN_NO_SPEECH_PROBABILITY = 0.6
"""Minimum no-speech probability for discarding a terminal subtitle credit."""

logger = getLogger(__name__)


def normalize_segments(
    segments: Sequence[TranscribedSegment],
    *,
    model_name: str,
    source: str,
    cache_path: Path | None,
    use_vad: bool,
    audio_duration_seconds: float | None = None,
    discard_repetitive_windows: bool = True,
) -> list[TranscribedSegment]:
    """Normalize malformed transcription segments from Whisper output.

    Arguments:
        segments: raw transcription segments
        model_name: Whisper model name, for logging
        source: source of the segments, for logging
        cache_path: cache path associated with the segments, if any
        use_vad: whether Whisper VAD produced the segments
        audio_duration_seconds: complete source-audio duration, if known
        discard_repetitive_windows: whether to discard windows whose retained text is
            pathologically repetitive
    Returns:
        normalized transcription segments
    """
    normalized_segments: list[TranscribedSegment] = []
    segment_idx = 0
    while segment_idx < len(segments):
        segment = segments[segment_idx].model_copy(deep=True)

        if segment_idx + 1 < len(segments):
            next_segment = segments[segment_idx + 1]
            if segment_text_from_words := _get_duplicate_segment_pair_text(
                segment, next_segment
            ):
                logger.warning(
                    f"Coalescing malformed Whisper segment pair for "
                    f"model={model_name} vad={use_vad} "
                    f"source={source} cache={cache_path} "
                    f"segment_idxs=({segment_idx},{segment_idx + 1}) "
                    f"ids=({segment.id},{next_segment.id}) "
                    f"text={segment_text_from_words!r}"
                )
                normalized_segments.append(
                    _get_coalesced_segment(
                        segment, next_segment, segment_text_from_words
                    )
                )
                segment_idx += 2
                continue

        if segment.text.strip() and not segment.words:
            logger.warning(
                f"Whisper segment is missing word timings for "
                f"model={model_name} vad={use_vad} "
                f"source={source} cache={cache_path} "
                f"segment_idx={segment_idx} id={segment.id} "
                f"start={segment.start} end={segment.end} "
                f"text={segment.text!r}"
            )

        normalized_segments.append(segment)
        segment_idx += 1

    pending_suffix_indexes: list[int] = []
    segment_idx = len(normalized_segments) - 1
    while segment_idx >= 0:
        segment = normalized_segments[segment_idx]
        if not segment.text.strip():
            segment_idx -= 1
            continue
        high_no_speech_probability = (
            segment.no_speech_prob is not None
            and segment.no_speech_prob >= _SUBTITLE_CREDIT_MIN_NO_SPEECH_PROBABILITY
        )

        normalized_text = segment.text.casefold()
        marker_indexes = [
            normalized_text.index(marker)
            for marker in SUBTITLE_CREDIT_HALLUCINATION_MARKERS
            if marker in normalized_text
        ]
        if not marker_indexes:
            if not high_no_speech_probability:
                break
            pending_suffix_indexes.append(segment_idx)
            segment_idx -= 1
            continue
        if not high_no_speech_probability and (
            audio_duration_seconds is None
            or get_transcription_quality_issue(
                [segment], audio_duration_seconds=audio_duration_seconds
            )
            is None
        ):
            break

        marker_idx = min(marker_indexes)
        retained_text = segment.text[:marker_idx].rstrip()
        suffix_segment_indexes = [segment_idx, *reversed(pending_suffix_indexes)]
        action = "Discarding"
        if retained_text:
            action = "Trimming"
        logger.warning(
            f"{action} terminal Whisper subtitle-credit hallucination for "
            f"model={model_name} vad={use_vad} "
            f"source={source} cache={cache_path} "
            f"segment_idxs={tuple(suffix_segment_indexes)} id={segment.id} "
            f"no_speech_prob={segment.no_speech_prob:.3f} "
            f"text={segment.text!r}"
        )
        for suffix_segment_idx in pending_suffix_indexes:
            del normalized_segments[suffix_segment_idx]
        pending_suffix_indexes.clear()

        if retained_text:
            normalized_segments[segment_idx] = _get_segment_prefix(
                segment, len(retained_text)
            )
            break

        del normalized_segments[segment_idx]
        segment_idx -= 1

    return _normalize_decode_window_compression(
        normalized_segments,
        model_name=model_name,
        source=source,
        cache_path=cache_path,
        use_vad=use_vad,
        discard_repetitive_windows=discard_repetitive_windows,
    )


def _get_coalesced_segment(
    segment_with_words: TranscribedSegment,
    duplicate_segment: TranscribedSegment,
    text: str,
) -> TranscribedSegment:
    """Coalesce a malformed empty-text/timed and text-only duplicate pair.

    Arguments:
        segment_with_words: first segment containing word timings
        duplicate_segment: following duplicate segment lacking word timings
        text: repaired segment text
    Returns:
        coalesced segment
    """
    coalesced_segment = duplicate_segment.model_copy(deep=True)
    coalesced_segment.start = min(segment_with_words.start, duplicate_segment.start)
    coalesced_segment.end = max(segment_with_words.end, duplicate_segment.end)
    coalesced_segment.text = text
    coalesced_segment.words = [
        word.model_copy(deep=True) for word in (segment_with_words.words or [])
    ]
    return coalesced_segment


def _get_duplicate_segment_pair_text(
    segment: TranscribedSegment, next_segment: TranscribedSegment
) -> str | None:
    """Get repaired text for a known malformed duplicate-segment pair.

    Arguments:
        segment: current segment
        next_segment: following segment
    Returns:
        repaired text if the pair matches the known malformed pattern
    """
    if (
        not segment.words
        or next_segment.words
        or segment.text.strip()
        or not next_segment.text.strip()
        or next_segment.start > segment.end
    ):
        return None

    segment_text_from_words = "".join(word.text for word in segment.words)
    if not segment_text_from_words or next_segment.text != segment_text_from_words:
        return None

    return segment_text_from_words


def _get_segment_prefix(
    segment: TranscribedSegment, end_idx: int
) -> TranscribedSegment:
    """Get a segment prefix with corresponding word timings.

    Arguments:
        segment: segment whose suffix should be removed
        end_idx: exclusive text index at which the suffix begins
    Returns:
        copied segment containing only the requested prefix
    """
    prefix = segment.model_copy(
        deep=True, update={"text": segment.text[:end_idx], "tokens": None}
    )
    if not prefix.words:
        return prefix

    prefix_words = []
    consumed_chars = 0
    for word in prefix.words:
        next_consumed_chars = consumed_chars + len(word.text)
        if next_consumed_chars <= end_idx:
            prefix_words.append(word)
        elif consumed_chars < end_idx:
            retained_length = end_idx - consumed_chars
            retained_ratio = retained_length / len(word.text)
            retained_end = word.start + (word.end - word.start) * retained_ratio
            prefix_words.append(
                word.model_copy(
                    update={
                        "text": word.text[:retained_length],
                        "end": retained_end,
                        "following_voice_activity_score": None,
                        "voice_activity_coverage": None,
                        "voice_activity_peak": None,
                        "voice_activity_score": None,
                    }
                )
            )
            break
        else:
            break
        consumed_chars = next_consumed_chars

    prefix.words = prefix_words
    if prefix_words:
        prefix_words[-1].following_voice_activity_score = None
        prefix.end = prefix_words[-1].end
    return prefix


def _normalize_decode_window_compression(
    segments: Sequence[TranscribedSegment],
    *,
    model_name: str,
    source: str,
    cache_path: Path | None,
    use_vad: bool,
    discard_repetitive_windows: bool,
) -> list[TranscribedSegment]:
    """Normalize Whisper compression scores against retained window text.

    Whisper reports compression for a complete decode window, then copies that
    score onto each emitted segment. The score may include a repetitive unfinished
    suffix that is absent from the retained segments.

    Arguments:
        segments: normalized segments to inspect by decode window
        model_name: Whisper model name, for logging
        source: source of the segments, for logging
        cache_path: cache path associated with the segments, if any
        use_vad: whether Whisper VAD produced the segments
        discard_repetitive_windows: whether to discard windows whose retained text is
            pathologically repetitive
    Returns:
        segments with stale scores corrected and repetitive windows discarded
    """
    normalized_segments: list[TranscribedSegment] = []
    for seek, window_segments in groupby(segments, key=lambda segment: segment.seek):
        window = list(window_segments)
        reported_ratios = [
            segment.compression_ratio
            for segment in window
            if segment.compression_ratio is not None
        ]
        reported_ratio = max(reported_ratios, default=0.0)
        if reported_ratio <= MAX_COMPRESSION_RATIO:
            normalized_segments.extend(window)
            continue

        retained_ratio = get_text_compression_ratio(
            "".join(segment.text for segment in window)
        )
        segment_ids = tuple(segment.id for segment in window)
        if retained_ratio > MAX_COMPRESSION_RATIO:
            if not discard_repetitive_windows:
                normalized_segments.extend(window)
                continue
            logger.warning(
                f"Discarding repetitive Whisper decode window for "
                f"model={model_name} vad={use_vad} source={source} "
                f"cache={cache_path} seek={seek} segment_ids={segment_ids} "
                f"reported_compression_ratio={reported_ratio:.2f} "
                f"retained_compression_ratio={retained_ratio:.2f}"
            )
            continue

        logger.warning(
            f"Correcting stale Whisper decode-window compression score for "
            f"model={model_name} vad={use_vad} source={source} "
            f"cache={cache_path} seek={seek} segment_ids={segment_ids} "
            f"reported_compression_ratio={reported_ratio:.2f} "
            f"retained_compression_ratio={retained_ratio:.2f}"
        )
        for segment in window:
            segment.compression_ratio = retained_ratio
        normalized_segments.extend(window)

    return normalized_segments
