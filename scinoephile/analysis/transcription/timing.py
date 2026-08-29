#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Evaluate reference-free transcription display timing against references."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from math import isfinite

from scinoephile.analysis.diff import SeriesDiff
from scinoephile.core.subtitles import Series, Subtitle

from .artifact import AlignmentArtifact, AlignmentBlock, TimingSettings

__all__ = [
    "TimingMetrics",
    "TimingPair",
    "evaluate_timing",
    "get_display_intervals",
    "get_reference_for_alignment",
    "retime_alignment",
]


@dataclass(frozen=True, slots=True)
class TimingPair:
    """One text-aligned candidate/reference timing comparison."""

    candidate_indexes: tuple[int, ...]
    """One-based candidate subtitle indexes in the aligned group."""
    reference_indexes: tuple[int, ...]
    """One-based reference subtitle indexes in the aligned group."""
    candidate_start_ms: int
    """Candidate group display start."""
    candidate_end_ms: int
    """Candidate group display end."""
    reference_start_ms: int
    """Reference group display start."""
    reference_end_ms: int
    """Reference group display end."""
    intersection_ms: int
    """Duration shared by candidate and reference display intervals."""
    union_ms: int
    """Duration covered by either display interval."""

    @property
    def end_error_ms(self) -> int:
        """Get candidate end minus reference end."""
        return self.candidate_end_ms - self.reference_end_ms

    @property
    def intersection_over_union(self) -> float:
        """Get temporal intersection over union."""
        if self.union_ms == 0:
            return 0.0
        return self.intersection_ms / self.union_ms

    @property
    def reference_coverage(self) -> float:
        """Get the fraction of reference display time covered by the candidate."""
        duration_ms = self.reference_end_ms - self.reference_start_ms
        if duration_ms == 0:
            return 0.0
        return self.intersection_ms / duration_ms

    @property
    def start_error_ms(self) -> int:
        """Get candidate start minus reference start."""
        return self.candidate_start_ms - self.reference_start_ms


@dataclass(frozen=True, slots=True)
class TimingMetrics:
    """Aggregate timing metrics for text-aligned subtitle groups."""

    settings: TimingSettings
    """Reference-free timing settings under evaluation."""
    pairs: tuple[TimingPair, ...]
    """Text-aligned candidate/reference timing groups."""
    unmatched_candidate_subtitles: int
    """Candidate subtitles that could not be paired with reference text."""
    unmatched_reference_subtitles: int
    """Reference subtitles that could not be paired with candidate text."""

    @property
    def candidate_to_reference_group_counts(self) -> dict[str, int]:
        """Get alignment-group counts keyed by candidate:reference shape."""
        counts = Counter(
            f"{len(pair.candidate_indexes)}:{len(pair.reference_indexes)}"
            for pair in self.pairs
        )
        return dict(sorted(counts.items()))

    @property
    def mean_absolute_end_error_ms(self) -> float:
        """Get mean absolute display-end error."""
        if not self.pairs:
            return 0.0
        return sum(abs(pair.end_error_ms) for pair in self.pairs) / len(self.pairs)

    @property
    def mean_absolute_start_error_ms(self) -> float:
        """Get mean absolute display-start error."""
        if not self.pairs:
            return 0.0
        return sum(abs(pair.start_error_ms) for pair in self.pairs) / len(self.pairs)

    @property
    def mean_end_error_ms(self) -> float:
        """Get mean signed display-end error."""
        if not self.pairs:
            return 0.0
        return sum(pair.end_error_ms for pair in self.pairs) / len(self.pairs)

    @property
    def mean_intersection_over_union(self) -> float:
        """Get the unweighted mean temporal intersection over union."""
        if not self.pairs:
            return 0.0
        return sum(pair.intersection_over_union for pair in self.pairs) / len(
            self.pairs
        )

    @property
    def mean_reference_coverage(self) -> float:
        """Get the mean fraction of reference display time covered."""
        if not self.pairs:
            return 0.0
        return sum(pair.reference_coverage for pair in self.pairs) / len(self.pairs)

    @property
    def mean_start_error_ms(self) -> float:
        """Get mean signed display-start error."""
        if not self.pairs:
            return 0.0
        return sum(pair.start_error_ms for pair in self.pairs) / len(self.pairs)

    @property
    def micro_intersection_over_union(self) -> float:
        """Get duration-weighted temporal intersection over union."""
        union_ms = sum(pair.union_ms for pair in self.pairs)
        if union_ms == 0:
            return 0.0
        return sum(pair.intersection_ms for pair in self.pairs) / union_ms

    @property
    def one_to_one_micro_intersection_over_union(self) -> float:
        """Get duration-weighted temporal IoU for unambiguous subtitle pairs."""
        pairs = self.one_to_one_pairs
        union_ms = sum(pair.union_ms for pair in pairs)
        if union_ms == 0:
            return 0.0
        return sum(pair.intersection_ms for pair in pairs) / union_ms

    @property
    def one_to_one_pairs(self) -> tuple[TimingPair, ...]:
        """Get pairs containing exactly one candidate and one reference subtitle."""
        return tuple(
            pair
            for pair in self.pairs
            if len(pair.candidate_indexes) == len(pair.reference_indexes) == 1
        )


def evaluate_timing(
    artifact: AlignmentArtifact,
    reference: Series,
    settings: TimingSettings | None = None,
) -> TimingMetrics:
    """Evaluate an artifact's speech timing under display-timing settings.

    Text alignment pairs the independently generated candidate and reference.
    Reference timings affect metrics only; they never alter ASR, merging, CTC
    alignment, or subtitle boundaries.

    Arguments:
        artifact: aligned multi-source transcription artifact
        reference: independent Cantonese reference subtitles
        settings: display timing to evaluate, or artifact timing when omitted
    Returns:
        aggregate and per-pair temporal overlap metrics
    """
    candidate = _get_candidate_series(artifact, settings)
    reference_selection = _get_reference_selection(artifact, reference)
    selected_reference = Series(
        events=[subtitle for _, subtitle in reference_selection]
    )
    original_reference_indexes = tuple(index for index, _ in reference_selection)
    if settings is None:
        settings = artifact.timing
    # Establish the text correspondence from immutable CTC speech bounds so the
    # display-padding policy under test cannot change which subtitles are scored.
    diff = SeriesDiff(_get_speech_series(artifact), selected_reference)
    pairs = []
    unmatched_candidate_indexes = set()
    unmatched_reference_indexes = set()
    for candidate_indexes, reference_indexes in _get_event_index_groups(diff):
        if not candidate_indexes:
            unmatched_reference_indexes.update(reference_indexes)
            continue
        if not reference_indexes:
            unmatched_candidate_indexes.update(candidate_indexes)
            continue
        pairs.append(
            _get_timing_pair(
                candidate,
                selected_reference,
                candidate_indexes,
                reference_indexes,
                original_reference_indexes,
            )
        )
    return TimingMetrics(
        settings=settings,
        pairs=tuple(pairs),
        unmatched_candidate_subtitles=len(unmatched_candidate_indexes),
        unmatched_reference_subtitles=len(unmatched_reference_indexes),
    )


def get_display_intervals(
    speech_intervals: Sequence[tuple[float, float]],
    audio_duration_seconds: float,
    settings: TimingSettings | None = None,
) -> list[tuple[float, float]]:
    """Pad speech intervals into neighboring silence without overlap.

    Arguments:
        speech_intervals: chronologically ordered speech start and end times
        audio_duration_seconds: complete source duration
        settings: optional display-timing settings
    Returns:
        display intervals corresponding one-to-one with the speech intervals
    Raises:
        ValueError: if source duration or speech timing is invalid
    """
    if not isfinite(audio_duration_seconds) or audio_duration_seconds <= 0.0:
        raise ValueError("Audio duration must be finite and positive.")
    if settings is None:
        settings = TimingSettings()
    if not speech_intervals:
        return []

    previous_end = -1.0
    for start_seconds, end_seconds in speech_intervals:
        if not isfinite(start_seconds) or not isfinite(end_seconds):
            raise ValueError("Merged subtitle speech timing must be finite.")
        if end_seconds <= start_seconds:
            raise ValueError("Merged subtitle speech duration must be positive.")
        if start_seconds < previous_end:
            raise ValueError("Merged subtitle speech intervals must not overlap.")
        if start_seconds < 0.0 or end_seconds > audio_duration_seconds:
            raise ValueError("Merged subtitle speech interval exceeds the audio.")
        previous_end = end_seconds

    output_intervals = []
    for segment_idx, speech_interval in enumerate(speech_intervals):
        speech_start_seconds, speech_end_seconds = speech_interval
        lower_bound = 0.0
        if segment_idx > 0:
            lower_bound = (
                speech_intervals[segment_idx - 1][1] + speech_start_seconds
            ) / 2
        upper_bound = audio_duration_seconds
        if segment_idx + 1 < len(speech_intervals):
            upper_bound = (
                speech_end_seconds + speech_intervals[segment_idx + 1][0]
            ) / 2

        display_start_seconds = max(
            lower_bound, speech_start_seconds - settings.lead_in_seconds
        )
        display_end_seconds = min(
            upper_bound, speech_end_seconds + settings.lead_out_seconds
        )
        required_seconds = settings.minimum_duration_seconds - (
            display_end_seconds - display_start_seconds
        )
        if required_seconds > 0.0:
            available_before = display_start_seconds - lower_bound
            available_after = upper_bound - display_end_seconds
            padding_before = min(required_seconds / 2, available_before)
            padding_after = min(required_seconds - padding_before, available_after)
            padding_before += min(
                required_seconds - padding_before - padding_after,
                available_before - padding_before,
            )
            display_start_seconds -= padding_before
            display_end_seconds += padding_after

        output_intervals.append((display_start_seconds, display_end_seconds))
    return output_intervals


def get_reference_for_alignment(
    artifact: AlignmentArtifact, reference: Series
) -> Series:
    """Select reference subtitles owned by the artifact's VAD block cores.

    Arguments:
        artifact: alignment artifact whose processed block range is authoritative
        reference: complete independent reference series
    Returns:
        reference subtitles whose midpoint lies within a processed block core
    """
    return Series(
        events=[
            subtitle for _, subtitle in _get_reference_selection(artifact, reference)
        ]
    )


def retime_alignment(
    artifact: AlignmentArtifact, settings: TimingSettings
) -> AlignmentArtifact:
    """Recalculate artifact display bounds from fixed CTC speech bounds.

    Arguments:
        artifact: reference-free artifact whose text and speech timing remain fixed
        settings: global display-timing policy to apply
    Returns:
        validated artifact with updated display bounds and timing metadata
    """
    artifact_data = artifact.model_dump(mode="python")
    artifact_data["timing"] = settings
    artifact_data["blocks"] = _get_blocks_with_display_timing(
        artifact.blocks, artifact.audio_duration_ms / 1000, settings
    )
    return AlignmentArtifact.model_validate(artifact_data)


def _get_blocks_with_display_timing(
    blocks: Sequence[AlignmentBlock],
    audio_duration_seconds: float,
    settings: TimingSettings,
) -> tuple[AlignmentBlock, ...]:
    """Apply globally calculated display bounds to alignment blocks.

    Arguments:
        blocks: alignment blocks containing fixed speech-timed subtitles
        audio_duration_seconds: complete source duration
        settings: display-timing settings to apply
    Returns:
        validated alignment blocks with updated display bounds
    """
    subtitles = [subtitle for block in blocks for subtitle in block.subtitles]
    display_intervals = get_display_intervals(
        [
            (subtitle.speech_start_ms / 1000, subtitle.speech_end_ms / 1000)
            for subtitle in subtitles
        ],
        audio_duration_seconds,
        settings,
    )
    display_bounds = {
        subtitle.index: (round(start * 1000), round(end * 1000))
        for subtitle, (start, end) in zip(subtitles, display_intervals, strict=True)
    }
    output_blocks = []
    for block in blocks:
        block_data = block.model_dump(mode="python")
        block_data["subtitles"] = tuple(
            {
                **subtitle.model_dump(mode="python"),
                "start_ms": display_bounds[subtitle.index][0],
                "end_ms": display_bounds[subtitle.index][1],
            }
            for subtitle in block.subtitles
        )
        output_blocks.append(AlignmentBlock.model_validate(block_data))
    return tuple(output_blocks)


def _get_candidate_series(
    artifact: AlignmentArtifact, settings: TimingSettings | None
) -> Series:
    """Get candidate subtitles using stored or recalculated display timing.

    Arguments:
        artifact: alignment artifact containing candidate subtitles
        settings: display-timing settings, or None to use stored timing
    Returns:
        candidate subtitle series
    """
    if settings is None:
        return artifact.get_series()
    return retime_alignment(artifact, settings).get_series()


def _get_event_index_groups(
    diff: SeriesDiff,
) -> tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]:
    """Consolidate line diff messages into subtitle event groups.

    Arguments:
        diff: line-level subtitle diff
    Returns:
        connected candidate and reference event-index groups
    """
    groups: list[tuple[set[int], set[int]]] = []
    for message in diff.get_messages(include_equal=True):
        candidate_indexes, reference_indexes = diff.get_event_indices(message)
        overlapping_group_indexes = [
            group_index
            for group_index, (group_candidates, group_references) in enumerate(groups)
            if not group_candidates.isdisjoint(candidate_indexes)
            or not group_references.isdisjoint(reference_indexes)
        ]
        if not overlapping_group_indexes:
            groups.append((set(candidate_indexes), set(reference_indexes)))
            continue

        group_index = overlapping_group_indexes[0]
        groups[group_index][0].update(candidate_indexes)
        groups[group_index][1].update(reference_indexes)
        for overlapping_group_index in reversed(overlapping_group_indexes[1:]):
            other_candidate_indexes, other_reference_indexes = groups.pop(
                overlapping_group_index
            )
            groups[group_index][0].update(other_candidate_indexes)
            groups[group_index][1].update(other_reference_indexes)

    return tuple(
        (tuple(sorted(candidate_indexes)), tuple(sorted(reference_indexes)))
        for candidate_indexes, reference_indexes in groups
    )


def _get_reference_selection(
    artifact: AlignmentArtifact, reference: Series
) -> tuple[tuple[int, Subtitle], ...]:
    """Select reference subtitles and retain their original indexes.

    Arguments:
        artifact: alignment artifact whose processed block range is authoritative
        reference: complete independent reference series
    Returns:
        selected original indexes and reference subtitles
    """
    core_ranges = tuple(
        (block.core_start_ms, block.core_end_ms) for block in artifact.blocks
    )
    return tuple(
        (index, subtitle)
        for index, subtitle in enumerate(reference)
        if any(
            start_ms <= (subtitle.start + subtitle.end) / 2 < end_ms
            for start_ms, end_ms in core_ranges
        )
    )


def _get_speech_series(artifact: AlignmentArtifact) -> Series:
    """Get merged text at immutable CTC speech bounds for evaluation pairing.

    Arguments:
        artifact: alignment artifact containing merged subtitles
    Returns:
        merged subtitle series using immutable speech bounds
    """
    return Series(
        events=[
            Subtitle(
                start=subtitle.speech_start_ms,
                end=subtitle.speech_end_ms,
                text=subtitle.text,
            )
            for block in artifact.blocks
            for subtitle in block.subtitles
        ]
    )


def _get_timing_pair(
    candidate: Series,
    reference: Series,
    candidate_indexes: tuple[int, ...],
    reference_indexes: tuple[int, ...],
    original_reference_indexes: tuple[int, ...],
) -> TimingPair:
    """Get overlap metrics for one text-aligned group.

    Arguments:
        candidate: complete candidate subtitle series
        reference: selected reference subtitle series
        candidate_indexes: candidate event indexes in the aligned group
        reference_indexes: selected-reference event indexes in the aligned group
        original_reference_indexes: original index of each selected reference event
    Returns:
        timing comparison for the aligned group
    """
    candidate_start_ms = min(candidate[index].start for index in candidate_indexes)
    candidate_end_ms = max(candidate[index].end for index in candidate_indexes)
    reference_start_ms = min(reference[index].start for index in reference_indexes)
    reference_end_ms = max(reference[index].end for index in reference_indexes)
    intersection_ms = max(
        0,
        min(candidate_end_ms, reference_end_ms)
        - max(candidate_start_ms, reference_start_ms),
    )
    union_ms = max(candidate_end_ms, reference_end_ms) - min(
        candidate_start_ms, reference_start_ms
    )
    return TimingPair(
        candidate_indexes=tuple(index + 1 for index in candidate_indexes),
        reference_indexes=tuple(
            original_reference_indexes[index] + 1 for index in reference_indexes
        ),
        candidate_start_ms=candidate_start_ms,
        candidate_end_ms=candidate_end_ms,
        reference_start_ms=reference_start_ms,
        reference_end_ms=reference_end_ms,
        intersection_ms=intersection_ms,
        union_ms=union_ms,
    )
