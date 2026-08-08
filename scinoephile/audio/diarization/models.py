#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Typed speaker diarization results and transcription reconciliation."""

from __future__ import annotations

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, Field, model_validator

from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment

__all__ = ["DiarizationMode", "SpeakerDiarizationResult", "SpeakerTurn"]


class DiarizationMode(StrEnum):
    """Speaker diarization behavior."""

    AUTO = "auto"
    """Use diarization when available and continue without it after failure."""
    ON = "on"
    """Require successful speaker diarization."""
    OFF = "off"
    """Do not run speaker diarization."""


class SpeakerTurn(BaseModel):
    """One source-timeline interval assigned to an anonymous speaker."""

    start: float = Field(ge=0.0)
    """Turn start time relative to the complete source audio, in seconds."""
    end: float = Field(gt=0.0)
    """Turn end time relative to the complete source audio, in seconds."""
    speaker: str = Field(min_length=1)
    """Anonymous source-wide speaker label."""

    @model_validator(mode="after")
    def validate_duration(self) -> Self:
        """Ensure the turn has positive duration."""
        if self.end <= self.start:
            raise ValueError("Speaker turn end must be after its start.")
        return self


class SpeakerDiarizationResult(BaseModel):
    """Overlap-aware and ASR-oriented source-timeline speaker turns."""

    turns: list[SpeakerTurn]
    """Regular overlap-preserving speaker diarization turns."""
    exclusive_turns: list[SpeakerTurn]
    """Non-overlapping turns intended for transcription reconciliation."""

    @model_validator(mode="after")
    def validate_turn_order(self) -> Self:
        """Ensure timelines are ordered and exclusive turns do not overlap."""
        for name, turns in (
            ("regular", self.turns),
            ("exclusive", self.exclusive_turns),
        ):
            if turns != sorted(
                turns, key=lambda turn: (turn.start, turn.end, turn.speaker)
            ):
                raise ValueError(f"{name.title()} speaker turns must be ordered.")
        for previous, current in zip(
            self.exclusive_turns, self.exclusive_turns[1:], strict=False
        ):
            if current.start < previous.end:
                raise ValueError("Exclusive speaker turns must not overlap.")
        return self

    def assign_speakers(
        self, segments: list[TranscribedSegment], *, offset_seconds: float = 0.0
    ) -> list[TranscribedSegment]:
        """Assign source-wide speakers to copied transcription word timings.

        Arguments:
            segments: transcription segments timed relative to an audio slice
            offset_seconds: audio-slice start relative to the complete source
        Returns:
            copied segments whose timed words carry anonymous speaker labels
        Raises:
            ValueError: if the offset is negative
        """
        if offset_seconds < 0.0:
            raise ValueError("Speaker-assignment offset cannot be negative.")

        assigned_segments = []
        for segment in segments:
            if segment.words is None:
                assigned_segments.append(segment.model_copy(deep=True))
                continue
            assigned_words = []
            for word in segment.words:
                turn = self._get_exclusive_turn(
                    word.start + offset_seconds, word.end + offset_seconds
                )
                update: dict[str, str | float | None] = {
                    "speaker": None,
                    "speaker_turn_end": None,
                    "speaker_turn_start": None,
                }
                if turn is not None:
                    update = {
                        "speaker": turn.speaker,
                        "speaker_turn_end": turn.end,
                        "speaker_turn_start": turn.start,
                    }
                assigned_words.append(word.model_copy(update=update))
            assigned_segments.append(
                segment.model_copy(update={"words": assigned_words}, deep=True)
            )
        return assigned_segments

    def get_exclusive_speaker(self, start: float, end: float) -> str | None:
        """Get the exclusive speaker with greatest overlap with an interval.

        Arguments:
            start: interval start relative to the complete source, in seconds
            end: interval end relative to the complete source, in seconds
        Returns:
            anonymous speaker label, or None when the interval contains no speech
        Raises:
            ValueError: if the interval is invalid
        """
        if start < 0.0 or end < start:
            raise ValueError("Speaker-assignment interval is invalid.")
        turn = self._get_exclusive_turn(start, end)
        if turn is None:
            return None
        return turn.speaker

    def _get_exclusive_turn(self, start: float, end: float) -> SpeakerTurn | None:
        """Get the exclusive speaker turn with greatest interval overlap.

        Arguments:
            start: interval start relative to the complete source, in seconds
            end: interval end relative to the complete source, in seconds
        Returns:
            greatest-overlap exclusive turn, or None when none overlaps
        Raises:
            ValueError: if the interval is invalid
        """
        if start < 0.0 or end < start:
            raise ValueError("Speaker-assignment interval is invalid.")
        interval_end = end
        if interval_end == start:
            interval_end = start + 1e-9

        best_turn = None
        best_overlap = 0.0
        midpoint = (start + interval_end) / 2
        for turn in self.exclusive_turns:
            if turn.start >= interval_end:
                break
            overlap = min(interval_end, turn.end) - max(start, turn.start)
            if overlap <= 0.0:
                continue
            if overlap > best_overlap:
                best_turn = turn
                best_overlap = overlap
                continue
            if overlap == best_overlap and best_turn is not None:
                current_contains_midpoint = turn.start <= midpoint < turn.end
                best_contains_midpoint = best_turn.start <= midpoint < best_turn.end
                if current_contains_midpoint and not best_contains_midpoint:
                    best_turn = turn
        if best_turn is None:
            return None
        return best_turn

    def reconcile_transcription(
        self, segments: list[TranscribedSegment], *, offset_seconds: float = 0.0
    ) -> list[TranscribedSegment]:
        """Assign speakers and expose safe internal changes as segment boundaries.

        Splitting is conservative: the word text must map exactly onto the segment
        text, and splitting must preserve the text that subtitle conversion exposes.
        Generic speaker assignment remains unsplit for callers that do not want
        diarization to alter transcription units.

        Arguments:
            segments: transcription segments timed relative to an audio slice
            offset_seconds: audio-slice start relative to the complete source
        Returns:
            copied speaker-assigned segments split at safe speaker transitions
        Raises:
            ValueError: if the offset is negative
        """
        assigned_segments = self.assign_speakers(
            segments, offset_seconds=offset_seconds
        )
        reconciled_segments = []
        for segment in assigned_segments:
            words = segment.words
            if words is None or len(words) < 2:
                reconciled_segments.append(segment)
                continue
            if "".join(word.text for word in words) != segment.text:
                reconciled_segments.append(segment)
                continue

            split_indexes = [
                index
                for index in range(1, len(words))
                if words[index - 1].speaker is not None
                and words[index].speaker is not None
                and words[index - 1].speaker != words[index].speaker
            ]
            if not split_indexes:
                reconciled_segments.append(segment)
                continue

            word_groups = [
                words[start:end]
                for start, end in zip(
                    [0, *split_indexes], [*split_indexes, len(words)], strict=True
                )
            ]
            group_texts = [
                "".join(word.text for word in word_group) for word_group in word_groups
            ]
            if (
                any(not text.strip() for text in group_texts)
                or "".join(text.strip() for text in group_texts) != segment.text.strip()
            ):
                reconciled_segments.append(segment)
                continue

            for group_index, (word_group, text) in enumerate(
                zip(word_groups, group_texts, strict=True)
            ):
                start = word_group[0].start
                if group_index == 0:
                    start = segment.start
                end = word_group[-1].end
                if group_index == len(word_groups) - 1:
                    end = segment.end
                reconciled_segments.append(
                    segment.model_copy(
                        update={
                            "start": start,
                            "end": end,
                            "text": text,
                            "words": word_group,
                        },
                        deep=True,
                    )
                )

        return [
            segment.model_copy(update={"id": segment_id})
            for segment_id, segment in enumerate(reconciled_segments)
        ]
