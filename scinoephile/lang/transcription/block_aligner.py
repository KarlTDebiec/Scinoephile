#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Align and punctuate a complete transcription block using sparse LLM changes."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from logging import getLogger
from math import ceil, floor
from typing import cast

from pydantic import ValidationError

from scinoephile.audio.subtitles import AudioSeries, AudioSubtitle
from scinoephile.core import ScinoephileError
from scinoephile.core.llms import Processor, TestCase, TestCaseSubtitle
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.core.synchronization import SyncGroup
from scinoephile.core.text import replace_control_characters
from scinoephile.llms.block_delineation import (
    BlockDelineationAnswer,
    BlockDelineationProcessor,
    BlockDelineationTestCase,
)
from scinoephile.llms.block_punctuation import (
    BlockPunctuationAnswer,
    BlockPunctuationProcessor,
    BlockPunctuationTestCase,
)

from .alignment import TranscriptionAlignment

__all__ = ["BlockTranscriptionAligner"]


logger = getLogger(__name__)

_MAX_UNSPLIT_SUBTITLES = 15
"""Largest block aligned in one LLM query."""
_EDGE_OWNED_SUBTITLES = 12
"""Nominal number of subtitles owned by first and last windows."""
_INTERIOR_OWNED_SUBTITLES = 9
"""Nominal number of subtitles owned by interior windows."""
_CONTEXT_SUBTITLES = 3
"""Number of neighboring subtitles supplied as context on each available side."""
_BOUNDARY_FLEXIBILITY = 3
"""Maximum nominal ownership-boundary movement when preferring timing gaps."""
_MIN_OWNED_SUBTITLES = 6
"""Minimum ownership retained after timing-gap boundary selection."""


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
        delineation_processor: BlockDelineationProcessor,
        punctuation_processor: BlockPunctuationProcessor,
        *,
        fallback_to_no_op: bool = False,
    ):
        """Initialize.

        Arguments:
            delineation_processor: processor for block delineation queries
            punctuation_processor: processor for block punctuation queries
            fallback_to_no_op: whether invalid answers fall back to sparse no-op
        """
        self.delineation_processor = delineation_processor
        """Redistribute target characters across all guide indexes in one query."""
        self.punctuation_processor = punctuation_processor
        """Punctuate all delineated target subtitles in one query."""
        self.fallback_to_no_op = fallback_to_no_op
        """Whether exhausted invalid answers fall back to sparse no-op answers."""

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
        if not any(targets):
            self._set_output(alignment, targets)
            return alignment

        references = list(alignment.reference)
        delineated = targets
        if len(references) > 1:
            delineated = self._delineate(references, targets)
        punctuated = self._punctuate(references, delineated)
        self._set_output(alignment, punctuated)
        return alignment

    def update_all_test_cases(self):
        """Persist block test cases encountered during the current run."""
        self.delineation_processor.save_test_cases()
        self.punctuation_processor.save_test_cases()

    def _delineate(
        self, references: Sequence[Subtitle], targets: list[str]
    ) -> list[str]:
        """Delineate overlapping windows and reconcile their owned boundaries.

        Arguments:
            references: complete timed guide subtitles
            targets: timing-based initial target assignment by index
        Returns:
            delineated target text by index
        """
        windows = self._get_windows(references)
        target_offsets = self._get_text_offsets(targets)
        boundary_offsets: list[int | None] = [None] * (len(targets) - 1)
        for window_index, window in enumerate(windows, 1):
            local_targets = targets[window.start : window.end]
            output = self._delineate_window(
                [reference.text for reference in references[window.start : window.end]],
                local_targets,
                first_owned_index=window.first_owned_index,
                last_owned_index=(
                    min(window.owned_end, len(targets) - 1) - window.start
                ),
                window_index=window_index,
            )
            local_offsets = self._get_text_offsets(output)
            window_offset = target_offsets[window.start]
            for boundary_index in range(
                window.owned_start, min(window.owned_end, len(targets) - 1)
            ):
                local_boundary_index = boundary_index - window.start
                boundary_offsets[boundary_index] = (
                    window_offset + local_offsets[local_boundary_index + 1]
                )

        if any(offset is None for offset in boundary_offsets):
            raise ScinoephileError(
                "Unable to reconcile block delineation: a subtitle boundary was "
                "not owned by any query window."
            )
        resolved_offsets = cast("list[int]", boundary_offsets)
        if resolved_offsets != sorted(resolved_offsets):
            message = (
                "Overlapping block-delineation windows produced crossing subtitle "
                "boundaries."
            )
            if not self.fallback_to_no_op:
                raise ScinoephileError(message)
            logger.warning(f"{message} Falling back to the timing-based assignment.")
            return list(targets)

        character_tape = "".join(targets)
        slice_starts = [0, *resolved_offsets]
        slice_ends = [*resolved_offsets, len(character_tape)]
        return [
            character_tape[start:end]
            for start, end in zip(slice_starts, slice_ends, strict=True)
        ]

    def _delineate_window(
        self,
        guides: list[str],
        targets: list[str],
        first_owned_index: int,
        last_owned_index: int,
        window_index: int,
    ) -> list[str]:
        """Delineate one query window using sparse replacements.

        Arguments:
            guides: local guide text by index
            targets: local preliminary target text by index
            first_owned_index: first local index whose following boundary is owned
            last_owned_index: last local index whose following boundary is owned
            window_index: one-based window number for diagnostics
        Returns:
            complete locally delineated target text
        """
        test_case_cls = self.delineation_processor.test_case_cls
        query = test_case_cls.query_cls.model_validate(
            {
                "guides": self._get_indexed_items(guides),
                "targets": self._get_indexed_items(targets),
                "first_owned_index": first_owned_index,
                "last_owned_index": last_owned_index,
            }
        )
        test_case = test_case_cls(query=query)
        test_case = cast(
            BlockDelineationTestCase,
            self._query_with_fallback(
                self.delineation_processor,
                test_case,
                f"block delineation window {window_index}",
            ),
        )
        answer = cast(BlockDelineationAnswer, test_case.answer)
        return self._apply_changes(targets, answer.changes)

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
        query = test_case_cls.query_cls.model_validate(
            {
                "guides": self._get_indexed_items(guides),
                "targets": self._get_indexed_items(targets),
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
        answer = cast(BlockPunctuationAnswer, test_case.answer)
        return self._apply_changes(targets, answer.changes)

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

        window_count = max(
            2,
            (subtitle_count - 6 + _INTERIOR_OWNED_SUBTITLES // 2)
            // _INTERIOR_OWNED_SUBTITLES,
        )
        ideal_sizes = [
            _EDGE_OWNED_SUBTITLES,
            *([_INTERIOR_OWNED_SUBTITLES] * (window_count - 2)),
            _EDGE_OWNED_SUBTITLES,
        ]
        size_delta = subtitle_count - sum(ideal_sizes)
        if window_count == 2 and size_delta < 0:
            ideal_sizes = [subtitle_count // 2, subtitle_count - subtitle_count // 2]
        elif size_delta > 0:
            interior_indexes = list(range(1, window_count - 1))
            while size_delta and any(
                ideal_sizes[index] < _MAX_UNSPLIT_SUBTITLES
                for index in interior_indexes
            ):
                for index in interior_indexes:
                    if ideal_sizes[index] >= _MAX_UNSPLIT_SUBTITLES:
                        continue
                    ideal_sizes[index] += 1
                    size_delta -= 1
                    if not size_delta:
                        break
            for index in (window_count - 1, 0):
                expansion = min(size_delta, _MAX_UNSPLIT_SUBTITLES - ideal_sizes[index])
                ideal_sizes[index] += expansion
                size_delta -= expansion
        elif size_delta < 0:
            shrinkable_indexes = [window_count - 1, *range(window_count - 2, 0, -1), 0]
            for index in shrinkable_indexes:
                reduction = min(-size_delta, ideal_sizes[index] - _MIN_OWNED_SUBTITLES)
                ideal_sizes[index] -= reduction
                size_delta += reduction
                if not size_delta:
                    break
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
            minimum_cut = max(
                previous_cut + _MIN_OWNED_SUBTITLES,
                subtitle_count - remaining_groups * _MAX_UNSPLIT_SUBTITLES,
                ceil(ideal_cut - _BOUNDARY_FLEXIBILITY),
            )
            maximum_cut = min(
                previous_cut + _MAX_UNSPLIT_SUBTITLES,
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
        except ValidationError as exc:
            if not self.fallback_to_no_op:
                raise

            fallback_test_case = type(test_case).model_validate(
                {
                    **test_case.model_dump(mode="json"),
                    "answer": test_case.get_no_op_answer().model_dump(mode="json"),
                    "few_shot": False,
                    "verified": False,
                }
            )
            processor.queryer.log_encountered_test_case(fallback_test_case)
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
