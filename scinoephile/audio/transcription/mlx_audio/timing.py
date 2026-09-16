#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MLX-Audio transcription timing transformations."""

from __future__ import annotations

from collections.abc import Sequence

from scinoephile.audio.transcription.exceptions import TranscriptionAlignmentError
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.transcribed_word import TranscribedWord

__all__ = ["restore_vad_timestamps"]


def restore_vad_timestamps(
    segments: Sequence[TranscribedSegment], speech_intervals: Sequence[tuple[int, int]]
) -> list[TranscribedSegment]:
    """Map speech-only word timings back to the original audio timeline.

    Arguments:
        segments: transcription timed against concatenated speech audio
        speech_intervals: original-audio speech intervals in milliseconds
    Returns:
        segments split and timed against the original audio
    Raises:
        TranscriptionAlignmentError: if aligned output lacks word timings
    """
    compressed_intervals: list[tuple[int, int, int]] = []
    compressed_start_ms = 0
    for original_start_ms, original_end_ms in speech_intervals:
        duration_ms = original_end_ms - original_start_ms
        compressed_end_ms = compressed_start_ms + duration_ms
        compressed_intervals.append(
            (compressed_start_ms, compressed_end_ms, original_start_ms)
        )
        compressed_start_ms = compressed_end_ms

    output_segments: list[TranscribedSegment] = []
    interval_idx = 0
    current_words: list[TranscribedWord] = []

    def append_current_segment():
        """Append accumulated words as one original-timeline segment."""
        nonlocal current_words
        if not current_words:
            return
        output_segments.append(
            TranscribedSegment(
                id=len(output_segments),
                seek=0,
                start=current_words[0].start,
                end=current_words[-1].end,
                text="".join(word.text for word in current_words),
                words=current_words,
            )
        )
        current_words = []

    for segment in segments:
        if not segment.words:
            raise TranscriptionAlignmentError(
                "MLX-Audio VAD cannot restore a segment without word timings."
            )
        for word in segment.words:
            word_start_ms = round(word.start * 1000)
            word_end_ms = round(word.end * 1000)
            word_midpoint_ms = (word_start_ms + word_end_ms) / 2
            while (
                interval_idx < len(compressed_intervals) - 1
                and word_midpoint_ms > compressed_intervals[interval_idx][1]
            ):
                append_current_segment()
                interval_idx += 1

            (
                interval_compressed_start_ms,
                interval_compressed_end_ms,
                interval_original_start_ms,
            ) = compressed_intervals[interval_idx]
            interval_duration_ms = (
                interval_compressed_end_ms - interval_compressed_start_ms
            )
            mapped_start_ms = interval_original_start_ms + max(
                0,
                min(word_start_ms - interval_compressed_start_ms, interval_duration_ms),
            )
            mapped_end_ms = interval_original_start_ms + max(
                0, min(word_end_ms - interval_compressed_start_ms, interval_duration_ms)
            )
            current_words.append(
                word.model_copy(
                    update={
                        "start": mapped_start_ms / 1000,
                        "end": mapped_end_ms / 1000,
                    }
                )
            )

    append_current_segment()
    return output_segments
