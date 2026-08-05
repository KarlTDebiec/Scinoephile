#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Deterministic delineation of timestamped transcription into subtitles."""

from __future__ import annotations

from dataclasses import dataclass, replace

from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.transcribed_word import TranscribedWord

__all__ = [
    "UnguidedBoundaryEvidence",
    "UnguidedDelineationResult",
    "UnguidedDelineationSettings",
    "UnguidedDelineator",
]


_STRONG_PUNCTUATION = frozenset(".!?;。！？；…")
"""Punctuation that strongly supports a following subtitle boundary."""

_WEAK_PUNCTUATION = frozenset(",:，：、")
"""Punctuation that weakly supports a following subtitle boundary."""

_RELAXED_CONSTRAINT_PENALTY = 25.0
"""Penalty applied when an indivisible unit exceeds a hard constraint."""

_SCORE_EPSILON = 1e-9
"""Tolerance used when comparing dynamic-programming path costs."""


@dataclass(frozen=True, slots=True, kw_only=True)
class UnguidedDelineationSettings:
    """Tunable constraints and evidence weights for unguided delineation."""

    target_characters: int = 9
    """Preferred number of non-whitespace characters per subtitle."""
    max_characters: int = 20
    """Maximum characters per subtitle, except for an indivisible unit."""
    preferred_min_duration_seconds: float = 0.75
    """Lower edge of the preferred spoken duration range."""
    preferred_max_duration_seconds: float = 3.5
    """Upper edge of the preferred spoken duration range."""
    max_duration_seconds: float = 6.0
    """Maximum spoken duration, except for an indivisible unit."""
    max_characters_per_second: float = 10.0
    """Reading speed above which a soft penalty is applied."""
    forced_gap_seconds: float = 3.0
    """Inter-unit pause that always forces a subtitle boundary."""
    full_pause_seconds: float = 0.8
    """Pause duration that receives full pause evidence."""
    full_voice_activity_gap_seconds: float = 0.4
    """Gap duration that permits full low-VAD evidence."""
    speaker_stability_seconds: float = 0.3
    """Same-speaker duration on each side required for full change evidence."""
    pause_weight: float = 1.6
    """Weight assigned to normalized pause evidence."""
    voice_activity_weight: float = 0.8
    """Weight assigned to normalized low-VAD evidence."""
    speaker_change_weight: float = 0.8
    """Weight assigned to a stable speaker transition."""
    strong_punctuation_weight: float = 1.0
    """Weight assigned to strong outgoing punctuation."""
    weak_punctuation_weight: float = 0.35
    """Weight assigned to weak outgoing punctuation."""
    boundary_penalty: float = 0.6
    """Base cost of introducing an internal subtitle boundary."""
    single_character_penalty: float = 1.0
    """Penalty applied to a one-character subtitle."""

    def __post_init__(self):
        """Validate delineation configuration."""
        if self.target_characters < 1:
            raise ValueError("Target subtitle characters must be positive.")
        if self.max_characters < self.target_characters:
            raise ValueError("Maximum subtitle characters cannot be below the target.")
        if self.preferred_min_duration_seconds < 0.0:
            raise ValueError("Preferred minimum duration must be non-negative.")
        if self.preferred_max_duration_seconds < self.preferred_min_duration_seconds:
            raise ValueError(
                "Preferred maximum duration cannot be below the preferred minimum."
            )
        if self.max_duration_seconds < self.preferred_max_duration_seconds:
            raise ValueError("Maximum duration cannot be below the preferred maximum.")
        for name, value in (
            ("maximum characters per second", self.max_characters_per_second),
            ("forced gap", self.forced_gap_seconds),
            ("full pause", self.full_pause_seconds),
            ("full voice-activity gap", self.full_voice_activity_gap_seconds),
            ("speaker stability", self.speaker_stability_seconds),
        ):
            if value <= 0.0:
                raise ValueError(f"Unguided delineation {name} must be positive.")
        for name, value in (
            ("pause", self.pause_weight),
            ("voice activity", self.voice_activity_weight),
            ("speaker change", self.speaker_change_weight),
            ("strong punctuation", self.strong_punctuation_weight),
            ("weak punctuation", self.weak_punctuation_weight),
            ("boundary", self.boundary_penalty),
            ("single character", self.single_character_penalty),
        ):
            if value < 0.0:
                raise ValueError(
                    f"Unguided delineation {name} weight must be non-negative."
                )


@dataclass(frozen=True, slots=True, kw_only=True)
class UnguidedBoundaryEvidence:
    """Audio and text evidence for one boundary between transcription units."""

    index: int
    """Number of transcription units preceding the boundary."""
    time: float
    """Boundary anchor at the outgoing unit's end, in seconds."""
    pause_seconds: float
    """Nonnegative pause before the following unit, in seconds."""
    following_voice_activity_score: float | None
    """Mean voice probability in the following gap, when available."""
    pause_score: float
    """Normalized pause evidence in [0, 1]."""
    voice_activity_score: float
    """Normalized low-voice-probability evidence in [0, 1]."""
    speaker_change: bool | None
    """Whether known adjacent speaker labels differ."""
    speaker_change_score: float
    """Speaker-change evidence reduced by short surrounding runs."""
    punctuation_score: float
    """Normalized outgoing punctuation evidence in [0, 1]."""
    total_score: float
    """Weighted sum of all boundary evidence."""
    selected: bool = False
    """Whether global optimization selected this boundary."""
    forced: bool = False
    """Whether a long pause requires this boundary."""


@dataclass(frozen=True, slots=True, kw_only=True)
class UnguidedDelineationResult:
    """Globally delineated segments and auditable boundary evidence."""

    segments: list[TranscribedSegment]
    """Delineated transcription segments in source order."""
    boundaries: list[UnguidedBoundaryEvidence]
    """All candidate boundaries, including selection decisions."""
    total_cost: float
    """Total objective value of the selected segmentation."""
    used_relaxed_constraints: bool
    """Whether an indivisible unit exceeded a hard constraint."""


@dataclass(frozen=True, slots=True)
class _DelineationUnit:
    """Smallest safely delineable timed text unit."""

    text: str
    start: float
    end: float
    seek: int
    words: tuple[TranscribedWord, ...] | None
    speaker: str | None
    speaker_turn_end: float | None
    speaker_turn_start: float | None
    following_voice_activity_score: float | None


@dataclass(frozen=True, slots=True)
class _DelineationPath:
    """Best known segmentation reaching one transcription-unit offset."""

    cost: float
    boundaries: tuple[int, ...]
    used_relaxed_constraints: bool


class UnguidedDelineator:
    """Globally delineate timed transcription using soft multimodal evidence."""

    def __init__(self, settings: UnguidedDelineationSettings | None = None):
        """Initialize.

        Arguments:
            settings: tunable delineation constraints and evidence weights
        """
        if settings is None:
            settings = UnguidedDelineationSettings()
        self.settings = settings
        """Tunable delineation constraints and evidence weights."""

    def __call__(self, segments: list[TranscribedSegment]) -> UnguidedDelineationResult:
        """Delineate timestamped transcription segments.

        Arguments:
            segments: source-ordered transcription segments
        Returns:
            globally optimized segments and boundary diagnostics
        Raises:
            ValueError: if segment or word timings are invalid or unordered
        """
        units = self._get_units(segments)
        if not units:
            return UnguidedDelineationResult(
                segments=[],
                boundaries=[],
                total_cost=0.0,
                used_relaxed_constraints=False,
            )

        boundaries = self._get_boundaries(units)
        boundary_by_index = {boundary.index: boundary for boundary in boundaries}
        character_offsets = [0]
        for unit in units:
            character_offsets.append(
                character_offsets[-1]
                + sum(not character.isspace() for character in unit.text)
            )
        forced_indexes = {boundary.index for boundary in boundaries if boundary.forced}
        paths: list[_DelineationPath | None] = [None] * (len(units) + 1)
        paths[0] = _DelineationPath(0.0, (), False)

        minimum_start_index = 0
        for end_index in range(1, len(units) + 1):
            best_path = None
            if end_index - 1 in forced_indexes:
                minimum_start_index = end_index - 1
            for start_index in range(end_index - 1, minimum_start_index - 1, -1):
                previous_path = paths[start_index]
                if previous_path is None:
                    continue
                if end_index - start_index > 1:
                    character_count = (
                        character_offsets[end_index] - character_offsets[start_index]
                    )
                    duration_seconds = max(
                        0.0, units[end_index - 1].end - units[start_index].start
                    )
                    if (
                        character_count > self.settings.max_characters
                        or duration_seconds > self.settings.max_duration_seconds
                    ):
                        break
                edge = self._get_segment_cost(units, start_index, end_index)
                if edge is None:
                    continue
                edge_cost, relaxed = edge
                selected_boundaries = previous_path.boundaries
                if end_index < len(units):
                    boundary = boundary_by_index[end_index]
                    edge_cost += self.settings.boundary_penalty - boundary.total_score
                    selected_boundaries = (*selected_boundaries, end_index)
                candidate_path = _DelineationPath(
                    cost=previous_path.cost + edge_cost,
                    boundaries=selected_boundaries,
                    used_relaxed_constraints=(
                        previous_path.used_relaxed_constraints or relaxed
                    ),
                )
                if self._path_is_better(candidate_path, best_path):
                    best_path = candidate_path
            paths[end_index] = best_path

        path = paths[-1]
        if path is None:
            raise ValueError("Unable to delineate transcription under its constraints.")
        selected_boundary_indexes = set(path.boundaries)
        selected_boundaries = [
            replace(boundary, selected=boundary.index in selected_boundary_indexes)
            for boundary in boundaries
        ]
        output_segments = self._get_output_segments(
            units, path.boundaries, boundary_by_index
        )
        return UnguidedDelineationResult(
            segments=output_segments,
            boundaries=selected_boundaries,
            total_cost=path.cost,
            used_relaxed_constraints=path.used_relaxed_constraints,
        )

    def _get_boundaries(
        self, units: list[_DelineationUnit]
    ) -> list[UnguidedBoundaryEvidence]:
        """Calculate evidence at each safe transcription-unit boundary."""
        boundaries = []
        for index in range(1, len(units)):
            left = units[index - 1]
            right = units[index]
            pause_seconds = max(0.0, right.start - left.end)
            pause_score = min(1.0, pause_seconds / self.settings.full_pause_seconds)

            following_voice_activity_score = left.following_voice_activity_score
            voice_activity_score = 0.0
            if following_voice_activity_score is not None:
                voice_activity_score = (1.0 - following_voice_activity_score) * min(
                    1.0, pause_seconds / self.settings.full_voice_activity_gap_seconds
                )

            speaker_change = None
            speaker_change_score = 0.0
            boundary_time = left.end
            if left.speaker is not None and right.speaker is not None:
                speaker_change = left.speaker != right.speaker
                if speaker_change:
                    left_start = left.speaker_turn_start
                    left_end = left.speaker_turn_end
                    if left_start is None or left_end is None:
                        left_start = left.start
                        left_end = left.end
                        unit_index = index - 2
                        while (
                            unit_index >= 0
                            and units[unit_index].speaker == left.speaker
                        ):
                            left_start = units[unit_index].start
                            unit_index -= 1
                    right_start = right.speaker_turn_start
                    right_end = right.speaker_turn_end
                    if right_start is None or right_end is None:
                        right_start = right.start
                        right_end = right.end
                        unit_index = index + 1
                        while (
                            unit_index < len(units)
                            and units[unit_index].speaker == right.speaker
                        ):
                            right_end = units[unit_index].end
                            unit_index += 1
                    speaker_change_score = min(
                        1.0,
                        (left_end - left_start)
                        / self.settings.speaker_stability_seconds,
                        (right_end - right_start)
                        / self.settings.speaker_stability_seconds,
                    )
                    if left.speaker_turn_end is not None:
                        boundary_time = max(
                            left.end, min(left.speaker_turn_end, right.start)
                        )

            punctuation_score = 0.0
            punctuation_reward = 0.0
            outgoing_text = left.text.rstrip()
            if outgoing_text and outgoing_text[-1] in _STRONG_PUNCTUATION:
                punctuation_score = 1.0
                punctuation_reward = self.settings.strong_punctuation_weight
            elif outgoing_text and outgoing_text[-1] in _WEAK_PUNCTUATION:
                punctuation_score = 0.4
                punctuation_reward = self.settings.weak_punctuation_weight

            total_score = (
                self.settings.pause_weight * pause_score
                + self.settings.voice_activity_weight * voice_activity_score
                + self.settings.speaker_change_weight * speaker_change_score
                + punctuation_reward
            )
            boundaries.append(
                UnguidedBoundaryEvidence(
                    index=index,
                    time=boundary_time,
                    pause_seconds=pause_seconds,
                    following_voice_activity_score=following_voice_activity_score,
                    pause_score=pause_score,
                    voice_activity_score=voice_activity_score,
                    speaker_change=speaker_change,
                    speaker_change_score=speaker_change_score,
                    punctuation_score=punctuation_score,
                    total_score=total_score,
                    forced=pause_seconds >= self.settings.forced_gap_seconds,
                )
            )
        return boundaries

    def _get_output_segments(
        self,
        units: list[_DelineationUnit],
        boundaries: tuple[int, ...],
        boundary_by_index: dict[int, UnguidedBoundaryEvidence],
    ) -> list[TranscribedSegment]:
        """Build output segments from selected transcription-unit boundaries."""
        offsets = (0, *boundaries, len(units))
        output_segments = []
        for segment_id, (start_index, end_index) in enumerate(
            zip(offsets[:-1], offsets[1:], strict=True)
        ):
            segment_units = units[start_index:end_index]
            segment_end = segment_units[-1].end
            if end_index < len(units):
                boundary = boundary_by_index[end_index]
                segment_end = max(
                    segment_end, min(boundary.time, units[end_index].start)
                )
            words = None
            if all(unit.words is not None for unit in segment_units):
                words = [
                    word.model_copy(deep=True)
                    for unit in segment_units
                    for word in (unit.words or ())
                ]
            output_segments.append(
                TranscribedSegment(
                    id=segment_id,
                    seek=segment_units[0].seek,
                    start=segment_units[0].start,
                    end=segment_end,
                    text="".join(unit.text for unit in segment_units),
                    words=words,
                )
            )
        return output_segments

    def _get_segment_cost(
        self, units: list[_DelineationUnit], start_index: int, end_index: int
    ) -> tuple[float, bool] | None:
        """Get one proposed subtitle's objective cost and relaxation status."""
        segment_units = units[start_index:end_index]
        text = "".join(unit.text for unit in segment_units)
        character_count = sum(not character.isspace() for character in text)
        duration_seconds = max(0.0, segment_units[-1].end - segment_units[0].start)
        hard_constraint_violated = (
            character_count == 0
            or character_count > self.settings.max_characters
            or duration_seconds > self.settings.max_duration_seconds
        )
        relaxed = False
        if hard_constraint_violated:
            if len(segment_units) > 1:
                return None
            relaxed = True

        character_loss = (
            (character_count - self.settings.target_characters) / 7.0
        ) ** 2
        short_duration = max(
            0.0, self.settings.preferred_min_duration_seconds - duration_seconds
        )
        long_duration = max(
            0.0, duration_seconds - self.settings.preferred_max_duration_seconds
        )
        short_duration_loss = 0.0
        if self.settings.preferred_min_duration_seconds > 0.0:
            short_duration_loss = (
                short_duration / self.settings.preferred_min_duration_seconds
            ) ** 2
        long_duration_scale = (
            self.settings.max_duration_seconds
            - self.settings.preferred_max_duration_seconds
        )
        if long_duration_scale <= 0.0:
            long_duration_scale = max(self.settings.preferred_max_duration_seconds, 1.0)
        long_duration_loss = (long_duration / long_duration_scale) ** 2
        duration_loss = 0.5 * (short_duration_loss + long_duration_loss)
        characters_per_second = character_count / max(duration_seconds, 0.001)
        reading_speed_loss = (
            1.5
            * (
                max(
                    0.0, characters_per_second - self.settings.max_characters_per_second
                )
                / 4.0
            )
            ** 2
        )
        single_character_loss = 0.0
        if character_count == 1:
            single_character_loss = self.settings.single_character_penalty
        cost = (
            character_loss + duration_loss + reading_speed_loss + single_character_loss
        )
        if relaxed:
            cost += _RELAXED_CONSTRAINT_PENALTY
        return cost, relaxed

    @staticmethod
    def _get_units(segments: list[TranscribedSegment]) -> list[_DelineationUnit]:
        """Convert segments into their smallest text-preserving timed units."""
        units = []
        previous_start = float("-inf")
        for segment in segments:
            if segment.end < segment.start:
                raise ValueError("Transcription segment end precedes its start.")
            words = [word for word in (segment.words or []) if word.text]
            words_match_text = (
                bool(words) and "".join(word.text for word in words) == segment.text
            )
            if words_match_text:
                for word in words:
                    if word.end < word.start:
                        raise ValueError("Transcribed word end precedes its start.")
                    if word.start < previous_start:
                        raise ValueError("Transcribed word timings are not ordered.")
                    units.append(
                        _DelineationUnit(
                            text=word.text,
                            start=word.start,
                            end=word.end,
                            seek=segment.seek,
                            words=(word,),
                            speaker=word.speaker,
                            speaker_turn_end=word.speaker_turn_end,
                            speaker_turn_start=word.speaker_turn_start,
                            following_voice_activity_score=(
                                word.following_voice_activity_score
                            ),
                        )
                    )
                    previous_start = word.start
                continue
            if not segment.text:
                continue
            if segment.start < previous_start:
                raise ValueError("Transcription segment timings are not ordered.")
            units.append(
                _DelineationUnit(
                    text=segment.text,
                    start=segment.start,
                    end=segment.end,
                    seek=segment.seek,
                    words=None,
                    speaker=None,
                    speaker_turn_end=None,
                    speaker_turn_start=None,
                    following_voice_activity_score=None,
                )
            )
            previous_start = segment.start
        return units

    @staticmethod
    def _path_is_better(
        candidate: _DelineationPath, current: _DelineationPath | None
    ) -> bool:
        """Determine whether one dynamic-programming path wins deterministically."""
        if current is None:
            return True
        if candidate.cost < current.cost - _SCORE_EPSILON:
            return True
        if candidate.cost > current.cost + _SCORE_EPSILON:
            return False
        if len(candidate.boundaries) < len(current.boundaries):
            return True
        if len(candidate.boundaries) > len(current.boundaries):
            return False
        return candidate.boundaries < current.boundaries
