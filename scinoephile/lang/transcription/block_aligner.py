#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Align and punctuate a complete transcription block using sparse LLM changes."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import groupby
from logging import getLogger
from math import ceil, floor
from typing import cast

from pydantic import ValidationError

from scinoephile.audio.subtitles import AudioSeries, AudioSubtitle
from scinoephile.core import ScinoephileError
from scinoephile.core.llms import Processor, TestCase, TestCaseSubtitle
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.core.synchronization import SyncGroup
from scinoephile.core.text import remove_punc_and_whitespace, replace_control_characters
from scinoephile.llms.block_delineation import (
    AdvisoryBlockDelineationProcessor,
    BlockDelineationProcessor,
    BlockDelineationTestCase,
    CandidateBlockDelineationProcessor,
)
from scinoephile.llms.block_punctuation import (
    BlockPunctuationProcessor,
    BlockPunctuationTestCase,
    PositionalBlockPunctuationProcessor,
)

from .alignment import TranscriptionAlignment

__all__ = ["BlockTranscriptionAligner"]


logger = getLogger(__name__)

_MAX_UNSPLIT_SUBTITLES = 12
"""Largest block aligned in one LLM query."""
_MAX_EDGE_OWNED_SUBTITLES = 12
"""Maximum subtitles owned by first and last windows."""
_MAX_INTERIOR_OWNED_SUBTITLES = 9
"""Maximum subtitles owned by interior windows."""
_CONTEXT_SUBTITLES = 3
"""Number of neighboring subtitles supplied as context on each available side."""
_BOUNDARY_FLEXIBILITY = 3
"""Maximum nominal ownership-boundary movement when preferring timing gaps."""
_MIN_OWNED_SUBTITLES = 6
"""Minimum ownership retained after timing-gap boundary selection."""
_MAX_PUNCTUATION_REPEAT_RUN_LENGTH = 32
"""Longest identical-character run included in a punctuation query."""
_MAX_CANDIDATE_DISTANCE = 24
"""Largest character distance considered for a timing-supported candidate cut."""
_CANDIDATE_CONTEXT_CHARACTERS = 8
"""Target characters shown on each side of a candidate cut."""
_MIN_ADVISORY_TIMING_IMPROVEMENT_MS = 500
"""Minimum timing improvement for highlighting an alternative boundary cut."""
_MAX_ADVISORY_MISSING_BASELINE_TIMING_DELTA_MS = 750
"""Largest guide-time distance when the preliminary cut has no timing record."""
_MAX_ADVISORY_PAUSE_TIMING_DELTA_MS = 400
"""Largest guide-time distance for highlighting a pause-supported cut."""
_MIN_ADVISORY_PAUSE_MS = 200
"""Minimum audio pause for independently highlighting a boundary cut."""


@dataclass(frozen=True, slots=True)
class _TimingBoundary:
    """Character offset and audio evidence after one transcription unit."""

    offset: int
    """Cumulative character offset on the complete target tape."""
    time: float
    """End time of the transcription unit."""
    pause: float
    """Nonnegative gap before the following transcription unit."""


@dataclass(frozen=True, slots=True)
class _AlignmentWindow:
    """One overlapping LLM query window and its exclusively owned outputs."""

    start: int
    """Zero-based inclusive query start index."""
    end: int
    """Zero-based exclusive query end index."""
    owned_start: int
    """Zero-based inclusive owned output start index."""
    owned_end: int
    """Zero-based exclusive owned output end index."""

    @property
    def first_owned_index(self) -> int:
        """Get the one-based local index of the first owned output."""
        return self.owned_start - self.start + 1

    @property
    def last_owned_index(self) -> int:
        """Get the one-based local index of the last owned output."""
        return self.owned_end - self.start


class BlockTranscriptionAligner:
    """Align and punctuate a transcription using overlapping block windows."""

    def __init__(
        self,
        delineation_processor: (
            AdvisoryBlockDelineationProcessor
            | BlockDelineationProcessor
            | CandidateBlockDelineationProcessor
        ),
        punctuation_processor: (
            BlockPunctuationProcessor | PositionalBlockPunctuationProcessor
        ),
        *,
        fallback_to_no_op: bool = False,
        gate_delineation_suggestions: bool = False,
        use_delineation_candidates: bool = False,
        use_delineation_suggestions: bool = False,
    ):
        """Initialize.

        Arguments:
            delineation_processor: processor for block delineation queries
            punctuation_processor: processor for block punctuation queries
            fallback_to_no_op: whether invalid answers fall back to sparse no-op
            gate_delineation_suggestions: whether weak timing suggestions are omitted
            use_delineation_candidates: whether boundary shifts must select from
                timing-supported candidate cuts
            use_delineation_suggestions: whether unrestricted boundaries include
                ranked timing-supported suggestions
        Raises:
            ValueError: if candidate restriction and advisory suggestions are both set
        """
        if use_delineation_candidates and use_delineation_suggestions:
            raise ValueError(
                "Delineation candidates and advisory suggestions are mutually "
                "exclusive."
            )
        if gate_delineation_suggestions and not use_delineation_suggestions:
            raise ValueError(
                "Delineation suggestions must be enabled before they can be gated."
            )
        self.delineation_processor = delineation_processor
        """Redistribute target characters across all guide indexes in one query."""
        self.punctuation_processor = punctuation_processor
        """Punctuate all delineated target subtitles in one query."""
        self.fallback_to_no_op = fallback_to_no_op
        """Whether exhausted invalid answers fall back to sparse no-op answers."""
        self.gate_delineation_suggestions = gate_delineation_suggestions
        """Whether weak advisory timing suggestions are omitted."""
        self.use_delineation_candidates = use_delineation_candidates
        """Whether delineation queries include timing-supported candidate cuts."""
        self.use_delineation_suggestions = use_delineation_suggestions
        """Whether delineation queries include advisory timing-supported cuts."""

    def align(
        self, reference_subs: Series, transcription_subs: AudioSeries
    ) -> TranscriptionAlignment:
        """Align and punctuate one complete transcription block.

        Arguments:
            reference_subs: guide subtitles for one block
            transcription_subs: raw timestamped transcription for the block
        Returns:
            guide-aligned sparse transcription
        """
        alignment = TranscriptionAlignment(reference_subs, transcription_subs)
        targets = [
            "".join(
                alignment.transcription[transcription_idx].text
                for transcription_idx in transcription_idxs
            )
            for _, transcription_idxs in alignment.sync_groups
        ]
        targets = [
            target if remove_punc_and_whitespace(target) else "" for target in targets
        ]
        if not any(targets):
            self._set_output(alignment, targets)
            return alignment

        references = list(alignment.reference)
        delineated = targets
        if len(references) > 1:
            timing_boundaries = (
                self._get_timing_boundaries(alignment, targets)
                if self.use_delineation_candidates or self.use_delineation_suggestions
                else []
            )
            delineated = self._delineate(
                references, targets, timing_boundaries=timing_boundaries
            )
        punctuated = self._punctuate(references, delineated)
        self._set_output(alignment, punctuated)
        return alignment

    def update_all_test_cases(self):
        """Persist block test cases encountered during the current run."""
        self.delineation_processor.save_encountered_test_cases()
        self.punctuation_processor.save_encountered_test_cases()

    def _delineate(
        self,
        references: Sequence[Subtitle],
        targets: list[str],
        *,
        timing_boundaries: Sequence[_TimingBoundary] = (),
    ) -> list[str]:
        """Delineate windows sequentially and retain their owned boundaries.

        Arguments:
            references: complete timed guide subtitles
            targets: timing-based initial target assignment by index
            timing_boundaries: transcription-unit cuts on the complete target tape
        Returns:
            delineated target text by index
        """
        windows = self._get_windows(references)
        character_tape = "".join(targets)
        boundary_offsets = self._get_text_offsets(targets)
        for window_index, window in enumerate(windows, 1):
            # Carry prior owned cuts into context and advance unresolved crossings
            for offset_index in range(1, len(boundary_offsets)):
                boundary_offsets[offset_index] = max(
                    boundary_offsets[offset_index], boundary_offsets[offset_index - 1]
                )
            local_targets = [
                character_tape[start:end]
                for start, end in zip(
                    boundary_offsets[window.start : window.end],
                    boundary_offsets[window.start + 1 : window.end + 1],
                    strict=True,
                )
            ]
            window_offset = boundary_offsets[window.start]
            output = self._delineate_window(
                references[window.start : window.end],
                local_targets,
                first_owned_index=window.first_owned_index,
                last_owned_index=(
                    min(window.owned_end, len(targets) - 1) - window.start
                ),
                window_index=window_index,
                window_offset=window_offset,
                timing_boundaries=timing_boundaries,
            )
            local_offsets = self._get_text_offsets(output)
            for boundary_index in range(
                window.owned_start, min(window.owned_end, len(targets) - 1)
            ):
                local_boundary_index = boundary_index - window.start
                proposed_offset = (
                    window_offset + local_offsets[local_boundary_index + 1]
                )
                boundary_offsets[boundary_index + 1] = max(
                    proposed_offset, boundary_offsets[boundary_index]
                )

        return [
            character_tape[start:end]
            for start, end in zip(
                boundary_offsets[:-1], boundary_offsets[1:], strict=True
            )
        ]

    def _delineate_window(
        self,
        references: Sequence[Subtitle],
        targets: list[str],
        first_owned_index: int,
        last_owned_index: int,
        window_index: int,
        window_offset: int,
        timing_boundaries: Sequence[_TimingBoundary],
    ) -> list[str]:
        """Delineate one query window using sparse boundary movements.

        Arguments:
            references: local timed guide subtitles by index
            targets: local preliminary target text by index
            first_owned_index: first local index whose following boundary is owned
            last_owned_index: last local index whose following boundary is owned
            window_index: one-based window number for diagnostics
            window_offset: character offset of the local tape in the complete tape
            timing_boundaries: transcription-unit cuts on the complete target tape
        Returns:
            complete locally delineated target text
        """
        test_case_cls = self.delineation_processor.test_case_cls
        query_data: dict[str, object] = {
            "guides": self._get_indexed_items(
                [reference.text for reference in references]
            ),
            "targets": self._get_indexed_items(targets),
            "first_owned_index": first_owned_index,
            "last_owned_index": last_owned_index,
        }
        if self.use_delineation_candidates:
            query_data["boundaries"] = self._get_candidate_boundary_values(
                references,
                targets,
                first_owned_index,
                last_owned_index,
                window_offset,
                timing_boundaries,
            )
        elif self.use_delineation_suggestions:
            query_data["boundaries"] = self._get_advisory_boundary_values(
                references,
                targets,
                first_owned_index,
                last_owned_index,
                window_offset,
                timing_boundaries,
                gated=self.gate_delineation_suggestions,
            )
        query = test_case_cls.query_cls.model_validate(query_data)
        test_case = test_case_cls(query=query)
        test_case = cast(
            BlockDelineationTestCase,
            self._query_with_fallback(
                self.delineation_processor,
                test_case,
                f"block delineation window {window_index}",
            ),
        )
        return test_case.get_output_texts()

    def _punctuate(
        self, references: Sequence[Subtitle], targets: list[str]
    ) -> list[str]:
        """Punctuate overlapping windows and retain only their owned outputs.

        Arguments:
            references: complete timed guide subtitles
            targets: delineated target text by index
        Returns:
            punctuated target text by index
        """
        output = list(targets)
        for window_index, window in enumerate(self._get_windows(references), 1):
            local_output = self._punctuate_window(
                [reference.text for reference in references[window.start : window.end]],
                targets[window.start : window.end],
                window,
                window_index,
            )
            for output_index in range(window.owned_start, window.owned_end):
                output[output_index] = local_output[output_index - window.start]
        return output

    def _punctuate_window(
        self,
        guides: list[str],
        targets: list[str],
        window: _AlignmentWindow,
        window_index: int,
    ) -> list[str]:
        """Punctuate one query window using sparse replacements.

        Arguments:
            guides: local guide text by index
            targets: local delineated target text by index
            window: query and ownership bounds
            window_index: one-based window number for diagnostics
        Returns:
            complete locally punctuated target text
        """
        test_case_cls = self.punctuation_processor.test_case_cls
        query_targets = targets.copy()
        masked_indexes: list[int] = []
        deterministic_empty_indexes: list[int] = []
        for index, target in enumerate(targets, 1):
            if not remove_punc_and_whitespace(target):
                query_targets[index - 1] = ""
                deterministic_empty_indexes.append(index)
                continue
            has_excessive_repeat_run = any(
                sum(1 for _ in characters) > _MAX_PUNCTUATION_REPEAT_RUN_LENGTH
                for _, characters in groupby(target)
            )
            if has_excessive_repeat_run:
                query_targets[index - 1] = ""
                masked_indexes.append(index)
        if masked_indexes:
            logger.info(
                "Keeping long repeated-character target indexes unchanged during "
                f"block punctuation window {window_index}: {masked_indexes}"
            )
        owned_indexes = set(
            range(window.first_owned_index, window.last_owned_index + 1)
        )
        if not any(
            query_targets[index - 1]
            for index in owned_indexes
            if index not in masked_indexes
        ):
            output = targets.copy()
            for index in owned_indexes & set(deterministic_empty_indexes):
                output[index - 1] = ""
            return output
        query = test_case_cls.query_cls.model_validate(
            {
                "guides": self._get_indexed_items(guides),
                "targets": self._get_indexed_items(query_targets),
                "first_owned_index": window.first_owned_index,
                "last_owned_index": window.last_owned_index,
            }
        )
        test_case = test_case_cls(query=query)
        test_case = cast(
            BlockPunctuationTestCase,
            self._query_with_fallback(
                self.punctuation_processor,
                test_case,
                f"block punctuation window {window_index}",
            ),
        )
        query_output = test_case.get_output_texts()
        output = targets.copy()
        for index in owned_indexes.difference(masked_indexes):
            output[index - 1] = query_output[index - 1]
        for index in owned_indexes & set(deterministic_empty_indexes):
            output[index - 1] = ""
        return output

    @staticmethod
    def _get_timing_boundaries(
        alignment: TranscriptionAlignment, targets: Sequence[str]
    ) -> list[_TimingBoundary]:
        """Get raw transcription-unit boundaries on the aligned character tape.

        Timing evidence is used only when guide-order alignment retains every raw
        transcription event in its original order. Otherwise candidate delineation
        safely exposes only each preliminary boundary.

        Arguments:
            alignment: preliminary timing alignment
            targets: preliminary target text by guide index
        Returns:
            ordered transcription-unit boundaries, or an empty list when the raw
            event order cannot be mapped exactly onto the target tape
        """
        transcription_indexes = [
            transcription_index
            for _, group_indexes in alignment.sync_groups
            for transcription_index in group_indexes
        ]
        if transcription_indexes != list(range(len(alignment.transcription))):
            return []

        raw_texts = [
            event.text if remove_punc_and_whitespace(event.text) else ""
            for event in alignment.transcription
        ]
        if "".join(raw_texts) != "".join(targets):
            return []

        boundaries_by_offset: dict[int, _TimingBoundary] = {}
        offset = 0
        for index, (event, text) in enumerate(
            zip(alignment.transcription, raw_texts, strict=True)
        ):
            offset += len(text)
            pause = 0.0
            if index + 1 < len(alignment.transcription):
                pause = max(0.0, alignment.transcription[index + 1].start - event.end)
            candidate = _TimingBoundary(offset, event.end, pause)
            existing = boundaries_by_offset.get(offset)
            if existing is None or candidate.pause > existing.pause:
                boundaries_by_offset[offset] = candidate
        return [boundaries_by_offset[offset] for offset in sorted(boundaries_by_offset)]

    @classmethod
    def _get_candidate_boundary_values(
        cls,
        references: Sequence[Subtitle],
        targets: Sequence[str],
        first_owned_index: int,
        last_owned_index: int,
        window_offset: int,
        timing_boundaries: Sequence[_TimingBoundary],
    ) -> list[dict[str, object]]:
        """Build compact candidate lists for each locally editable boundary.

        Arguments:
            references: local timed guide subtitles
            targets: local preliminary target text
            first_owned_index: first local editable boundary index
            last_owned_index: last local owned boundary index
            window_offset: local tape offset within the complete target tape
            timing_boundaries: transcription-unit cuts on the complete target tape
        Returns:
            candidate-bearing boundary mappings accepted by the query model
        """
        target_tape = "".join(targets)
        offsets = cls._get_text_offsets(targets)
        last_boundary_index = min(last_owned_index, len(targets) - 1)
        local_timing_boundaries = [
            _TimingBoundary(
                boundary.offset - window_offset, boundary.time, boundary.pause
            )
            for boundary in timing_boundaries
            if window_offset <= boundary.offset <= window_offset + len(target_tape)
        ]
        values: list[dict[str, object]] = []
        for index in range(first_owned_index, last_boundary_index + 1):
            original_offset = offsets[index]
            guide_boundary_time = references[index - 1].end
            nearby = [
                boundary
                for boundary in local_timing_boundaries
                if abs(boundary.offset - original_offset) <= _MAX_CANDIDATE_DISTANCE
            ]
            selected_offsets = {original_offset}
            selected_offsets.update(
                boundary.offset
                for boundary in sorted(
                    nearby,
                    key=lambda boundary: (
                        abs(boundary.time - guide_boundary_time),
                        abs(boundary.offset - original_offset),
                        boundary.offset,
                    ),
                )[:3]
            )
            selected_offsets.update(
                boundary.offset
                for boundary in sorted(
                    nearby,
                    key=lambda boundary: (
                        -boundary.pause,
                        abs(boundary.offset - original_offset),
                        boundary.offset,
                    ),
                )[:3]
            )
            selected_offsets.update(
                boundary.offset
                for boundary in sorted(
                    nearby,
                    key=lambda boundary: (
                        abs(boundary.offset - original_offset),
                        boundary.offset,
                    ),
                )[:2]
            )
            timing_by_offset = {
                boundary.offset: boundary for boundary in local_timing_boundaries
            }
            candidates = []
            for candidate_offset in sorted(selected_offsets):
                timing = timing_by_offset.get(candidate_offset)
                candidates.append(
                    {
                        "shift": candidate_offset - original_offset,
                        "offset": candidate_offset,
                        "left_context": target_tape[
                            max(
                                0, candidate_offset - _CANDIDATE_CONTEXT_CHARACTERS
                            ) : candidate_offset
                        ],
                        "right_context": target_tape[
                            candidate_offset : candidate_offset
                            + _CANDIDATE_CONTEXT_CHARACTERS
                        ],
                        "timing_delta_ms": (
                            round(timing.time - guide_boundary_time)
                            if timing is not None
                            else None
                        ),
                        "pause_ms": round(timing.pause) if timing is not None else None,
                    }
                )
            values.append(
                {
                    "index": index,
                    "original_offset": original_offset,
                    "minimum_shift": -original_offset,
                    "maximum_shift": len(target_tape) - original_offset,
                    "candidates": candidates,
                }
            )
        return values

    @classmethod
    def _get_advisory_boundary_values(
        cls,
        references: Sequence[Subtitle],
        targets: Sequence[str],
        first_owned_index: int,
        last_owned_index: int,
        window_offset: int,
        timing_boundaries: Sequence[_TimingBoundary],
        *,
        gated: bool = False,
    ) -> list[dict[str, object]]:
        """Build ranked, non-binding timing suggestions for editable boundaries.

        Arguments:
            references: local timed guide subtitles
            targets: local preliminary target text
            first_owned_index: first local editable boundary index
            last_owned_index: last local owned boundary index
            window_offset: local tape offset within the complete target tape
            timing_boundaries: transcription-unit cuts on the complete target tape
            gated: whether to omit suggestions without strong comparative evidence
        Returns:
            advisory boundary mappings accepted by the query model
        """
        candidate_values = cls._get_candidate_boundary_values(
            references,
            targets,
            first_owned_index,
            last_owned_index,
            window_offset,
            timing_boundaries,
        )
        values: list[dict[str, object]] = []
        for candidate_value in candidate_values:
            candidates = candidate_value["candidates"]
            if not isinstance(candidates, list):
                raise TypeError("Boundary candidates must be a list.")
            ranked_candidates = sorted(candidates, key=cls._get_suggestion_sort_key)
            if gated:
                ranked_candidates = cls._get_gated_suggestion_candidates(
                    ranked_candidates
                )
            suggestions = []
            for rank, candidate in enumerate(ranked_candidates, 1):
                if not isinstance(candidate, dict):
                    raise TypeError("Boundary candidate must be a mapping.")
                suggestions.append({"rank": rank, **candidate})
            values.append(
                {
                    key: value
                    for key, value in candidate_value.items()
                    if key != "candidates"
                }
                | {"suggestions": suggestions}
            )
        return values

    @staticmethod
    def _get_gated_suggestion_candidates(
        candidates: Sequence[object],
    ) -> list[dict[str, object]]:
        """Retain only the baseline and alternatives with strong timing evidence.

        Arguments:
            candidates: ranked boundary candidate mappings
        Returns:
            gated candidates, or an empty list when no alternative is strong
        Raises:
            TypeError: if candidate timing evidence does not have its expected type
        """
        if not all(isinstance(candidate, dict) for candidate in candidates):
            raise TypeError("Boundary candidates must be mappings.")
        candidate_values = cast("list[dict[str, object]]", candidates)
        original_candidate = next(
            candidate for candidate in candidate_values if candidate.get("shift") == 0
        )
        original_timing_delta_ms = original_candidate.get("timing_delta_ms")
        if original_timing_delta_ms is not None and not isinstance(
            original_timing_delta_ms, int
        ):
            raise TypeError("Original boundary timing delta must be an integer.")

        strong_candidates: list[dict[str, object]] = []
        for candidate in candidate_values:
            shift = candidate.get("shift")
            timing_delta_ms = candidate.get("timing_delta_ms")
            pause_ms = candidate.get("pause_ms")
            if shift == 0 or timing_delta_ms is None:
                continue
            if not isinstance(timing_delta_ms, int) or not isinstance(pause_ms, int):
                raise TypeError(
                    "Timed boundary candidates require integer timing evidence."
                )
            if original_timing_delta_ms is None:
                has_stronger_timing = (
                    abs(timing_delta_ms)
                    <= _MAX_ADVISORY_MISSING_BASELINE_TIMING_DELTA_MS
                )
            else:
                timing_improvement_ms = abs(original_timing_delta_ms) - abs(
                    timing_delta_ms
                )
                has_stronger_timing = (
                    timing_improvement_ms >= _MIN_ADVISORY_TIMING_IMPROVEMENT_MS
                )
            has_strong_pause = (
                abs(timing_delta_ms) <= _MAX_ADVISORY_PAUSE_TIMING_DELTA_MS
                and pause_ms >= _MIN_ADVISORY_PAUSE_MS
            )
            if has_stronger_timing or has_strong_pause:
                strong_candidates.append(candidate)
        if not strong_candidates:
            return []
        return [
            candidate
            for candidate in candidate_values
            if candidate is original_candidate or candidate in strong_candidates
        ]

    @staticmethod
    def _get_suggestion_sort_key(value: object) -> tuple[int, int, int, int, int]:
        """Get deterministic timing-evidence rank for one boundary suggestion.

        Arguments:
            value: candidate boundary mapping
        Returns:
            sort key prioritizing timing proximity, pauses, and local proximity
        Raises:
            TypeError: if candidate values do not have their expected types
        """
        if not isinstance(value, dict):
            raise TypeError("Boundary candidate must be a mapping.")
        timing_delta_ms = value.get("timing_delta_ms")
        pause_ms = value.get("pause_ms")
        shift = value.get("shift")
        offset = value.get("offset")
        if timing_delta_ms is not None and not isinstance(timing_delta_ms, int):
            raise TypeError("Boundary candidate timing delta must be an integer.")
        if pause_ms is not None and not isinstance(pause_ms, int):
            raise TypeError("Boundary candidate pause must be an integer.")
        if not isinstance(shift, int) or not isinstance(offset, int):
            raise TypeError("Boundary candidate shift and offset must be integers.")
        timing_missing = 0
        timing_distance = 0
        if timing_delta_ms is None:
            timing_missing = 1
        else:
            timing_distance = abs(timing_delta_ms)
        pause = pause_ms or 0
        return timing_missing, timing_distance, -pause, abs(shift), offset

    @classmethod
    def _get_windows(cls, references: Sequence[Subtitle]) -> list[_AlignmentWindow]:
        """Plan overlapping ownership windows around strong nearby timing gaps.

        Arguments:
            references: complete timed guide subtitles
        Returns:
            ordered query windows covering every output exactly once
        """
        subtitle_count = len(references)
        if subtitle_count <= _MAX_UNSPLIT_SUBTITLES:
            return [_AlignmentWindow(0, subtitle_count, 0, subtitle_count)]

        window_count = 2
        while subtitle_count > (
            2 * _MAX_EDGE_OWNED_SUBTITLES
            + (window_count - 2) * _MAX_INTERIOR_OWNED_SUBTITLES
        ):
            window_count += 1
        maximum_sizes = [
            _MAX_EDGE_OWNED_SUBTITLES,
            *([_MAX_INTERIOR_OWNED_SUBTITLES] * (window_count - 2)),
            _MAX_EDGE_OWNED_SUBTITLES,
        ]
        total_capacity = sum(maximum_sizes)
        ideal_sizes = [
            subtitle_count * maximum_size / total_capacity
            for maximum_size in maximum_sizes
        ]
        gaps = [
            references[index].start - references[index - 1].end
            for index in range(1, subtitle_count)
        ]

        cuts: list[int] = []
        cumulative_ideal = 0
        for cut_number, ideal_size in enumerate(ideal_sizes[:-1], 1):
            cumulative_ideal += ideal_size
            ideal_cut = cumulative_ideal
            remaining_groups = window_count - cut_number
            previous_cut = cuts[-1] if cuts else 0
            remaining_capacity = sum(maximum_sizes[cut_number:])
            minimum_cut = max(
                previous_cut + _MIN_OWNED_SUBTITLES,
                subtitle_count - remaining_capacity,
                ceil(ideal_cut - _BOUNDARY_FLEXIBILITY),
            )
            maximum_cut = min(
                previous_cut + maximum_sizes[cut_number - 1],
                subtitle_count - remaining_groups * _MIN_OWNED_SUBTITLES,
                floor(ideal_cut + _BOUNDARY_FLEXIBILITY),
            )
            candidates = range(minimum_cut, maximum_cut + 1)
            cut = max(
                candidates,
                key=lambda candidate: (
                    gaps[candidate - 1],
                    -abs(candidate - ideal_cut),
                    -candidate,
                ),
            )
            cuts.append(cut)

        ownership_starts = [0, *cuts]
        ownership_ends = [*cuts, subtitle_count]
        return [
            _AlignmentWindow(
                start=max(0, owned_start - _CONTEXT_SUBTITLES),
                end=min(subtitle_count, owned_end + _CONTEXT_SUBTITLES),
                owned_start=owned_start,
                owned_end=owned_end,
            )
            for owned_start, owned_end in zip(
                ownership_starts, ownership_ends, strict=True
            )
        ]

    @staticmethod
    def _get_text_offsets(texts: Sequence[str]) -> list[int]:
        """Get cumulative character offsets including both outer boundaries.

        Arguments:
            texts: text segments in order
        Returns:
            zero followed by cumulative character counts
        """
        offsets = [0]
        for text in texts:
            offsets.append(offsets[-1] + len(text))
        return offsets

    def _query_with_fallback(
        self, processor: Processor, test_case: TestCase, operation: str
    ) -> TestCase:
        """Query an operation and optionally persist a no-op after invalid answers.

        Arguments:
            processor: processor whose queryer should execute the test case
            test_case: unanswered block test case
            operation: human-readable operation name for logging
        Returns:
            answered LLM or no-op test case
        Raises:
            ValidationError: if answers remain invalid and fallback is disabled
        """
        try:
            return processor.queryer(test_case)
        except (ScinoephileError, ValidationError) as exc:
            if isinstance(exc, ScinoephileError) and not isinstance(
                exc.__cause__, ValidationError
            ):
                raise
            if not self.fallback_to_no_op:
                raise

            fallback_test_case = type(test_case).model_validate(
                {
                    **test_case.model_dump(mode="json"),
                    "answer": test_case.get_no_op_answer().model_dump(mode="json"),
                    "few_shot": False,
                    "verified": False,
                },
                context={"skip_output_quality_validation": True},
            )
            processor.queryer.log_encountered_test_case(
                fallback_test_case, skip_output_quality_validation=True
            )
            logger.warning(
                f"Falling back to an unverified no-op answer for {operation} after "
                f"invalid LLM responses: {exc}"
            )
            return fallback_test_case

    def _set_output(
        self, alignment: TranscriptionAlignment, output_texts: Sequence[str]
    ):
        """Replace alignment transcription with sparse guide-timed output.

        Arguments:
            alignment: alignment to update
            output_texts: complete output text by guide index
        """
        events: list[AudioSubtitle] = []
        sync_groups: list[SyncGroup] = []
        for reference_idx, (reference, output_text) in enumerate(
            zip(alignment.reference, output_texts, strict=True)
        ):
            normalized_output_text = replace_control_characters(output_text)
            if not normalized_output_text:
                sync_groups.append(([reference_idx], []))
                continue
            output_idx = len(events)
            events.append(
                AudioSubtitle(
                    start=reference.start,
                    end=reference.end,
                    text=normalized_output_text,
                )
            )
            sync_groups.append(([reference_idx], [output_idx]))

        alignment.transcription = AudioSeries(
            audio=alignment.transcription.audio, events=events
        )
        alignment._sync_groups_override = sync_groups

    @staticmethod
    def _apply_changes(
        targets: list[str], changes: Sequence[TestCaseSubtitle]
    ) -> list[str]:
        """Overlay sparse indexed changes onto complete target text.

        Arguments:
            targets: complete target text by guide index
            changes: sparse one-based target replacements
        Returns:
            complete target text with replacements applied
        """
        output = list(targets)
        for change in changes:
            output[change.index - 1] = change.text
        return output

    @staticmethod
    def _get_indexed_items(texts: Sequence[str]) -> list[dict[str, int | str]]:
        """Get one-based indexed text mappings.

        Arguments:
            texts: complete text sequence
        Returns:
            indexed mappings accepted by block query models
        """
        return [{"index": index, "text": text} for index, text in enumerate(texts, 1)]
