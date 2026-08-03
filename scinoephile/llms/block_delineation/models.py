#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for block-level delineation test cases."""

from __future__ import annotations

from collections.abc import Mapping
from typing import ClassVar, Self, cast

from pydantic import Field, ValidationInfo, model_validator

from scinoephile.core.llms import Answer, Query, TestCase, TestCaseSubtitle
from scinoephile.core.llms.models import LLMModel
from scinoephile.core.text import remove_punc_and_whitespace

from .prompt import (
    AdvisoryBlockDelineationPrompt,
    BlockDelineationPrompt,
    CandidateBlockDelineationPrompt,
)

__all__ = [
    "AdvisoryBlockDelineationBoundary",
    "AdvisoryBlockDelineationBoundarySuggestion",
    "AdvisoryBlockDelineationQuery",
    "AdvisoryBlockDelineationTestCase",
    "BlockDelineationAnswer",
    "BlockDelineationBoundary",
    "BlockDelineationBoundaryCandidate",
    "BlockDelineationBoundaryChange",
    "BlockDelineationQuery",
    "BlockDelineationSubtitle",
    "BlockDelineationTestCase",
    "CandidateBlockDelineationBoundary",
    "CandidateBlockDelineationQuery",
    "CandidateBlockDelineationTestCase",
]


_BASE_PROMPT = BlockDelineationPrompt()
_ADVISORY_PROMPT = AdvisoryBlockDelineationPrompt()

_LEADING_CLOSING_PUNCTUATION = set(",.!?;:，。！？；：、")
"""Sentence punctuation that must not begin reconstructed target text."""
_TRAILING_OPENING_PUNCTUATION = set("([{<（［｛〈《「『【〔〖〘〚‘“")
"""Opening punctuation that must not end reconstructed target text."""


class BlockDelineationSubtitle(TestCaseSubtitle):
    """Indexed block subtitle text without a length restriction."""

    text: str
    """Subtitle text."""


class BlockDelineationBoundaryChange(LLMModel):
    """Signed movement of one boundary on the immutable target character tape."""

    index: int = Field(ge=1)
    """One-based target index immediately before the boundary."""
    shift: int
    """Signed character count by which to move the boundary."""


class BlockDelineationBoundaryCandidate(LLMModel):
    """One timing-supported candidate position for an editable boundary."""

    shift: int
    """Signed movement relative to the preliminary boundary."""
    offset: int = Field(ge=0)
    """Cumulative Unicode-character offset on the local target tape."""
    left_context: str
    """Target text immediately before the candidate cut."""
    right_context: str
    """Target text immediately after the candidate cut."""
    timing_delta_ms: int | None = None
    """Candidate time minus the guide boundary time, in milliseconds."""
    pause_ms: int | None = Field(default=None, ge=0)
    """Nonnegative audio gap following the transcription unit, in milliseconds."""


class AdvisoryBlockDelineationBoundarySuggestion(BlockDelineationBoundaryCandidate):
    """One ranked, non-binding timing-supported boundary suggestion."""

    rank: int = Field(ge=1)
    """One-based evidence rank, with lower ranks representing stronger evidence."""


class BlockDelineationBoundary(LLMModel):
    """Original position and legal shift range of one editable boundary."""

    index: int = Field(ge=1)
    """One-based target index immediately before the boundary."""
    original_offset: int = Field(ge=0)
    """Original cumulative Unicode-character offset of the boundary."""
    minimum_shift: int
    """Minimum inclusive legal shift relative to the original offset."""
    maximum_shift: int
    """Maximum inclusive legal shift relative to the original offset."""


class AdvisoryBlockDelineationBoundary(BlockDelineationBoundary):
    """Editable boundary with ranked, non-binding timing suggestions."""

    suggestions: list[AdvisoryBlockDelineationBoundarySuggestion] = Field(
        default_factory=list
    )
    """Ranked timing-supported suggestions, or empty when evidence is weak."""


class CandidateBlockDelineationBoundary(BlockDelineationBoundary):
    """Editable boundary with timing-supported candidate cuts."""

    candidates: list[BlockDelineationBoundaryCandidate] = Field(min_length=1)
    """Timing-supported candidate cuts for this boundary."""


class BlockDelineationQuery(Query):
    """Complete guides and timing-based initial targets for one query window."""

    prompt: ClassVar[BlockDelineationPrompt] = _BASE_PROMPT
    """Text and field aliases for block-level delineation."""
    guides: list[BlockDelineationSubtitle] = Field(min_length=1)
    """Complete guide subtitles in index order."""
    targets: list[BlockDelineationSubtitle] = Field(min_length=1)
    """Complete initial target assignment in guide-index order."""
    first_owned_index: int | None = Field(default=None, ge=1)
    """First local target index whose following boundary this window owns."""
    last_owned_index: int | None = Field(default=None, ge=1)
    """Last local target index whose following boundary this window owns."""
    boundaries: list[BlockDelineationBoundary] = Field(default_factory=list)
    """Original offsets and legal shift ranges of every editable boundary."""

    @property
    def owned_index_range(self) -> range:
        """Get the inclusive local target-index range owned by this query."""
        first_index = self.first_owned_index or 1
        last_index = self.last_owned_index or len(self.targets)
        return range(first_index, last_index + 1)

    @property
    def owned_boundary_index_range(self) -> range:
        """Get local boundary indexes that this query may change."""
        first_index = self.first_owned_index or 1
        last_index = self.last_owned_index or len(self.targets)
        return range(first_index, min(last_index, len(self.targets) - 1) + 1)

    @model_validator(mode="before")
    @classmethod
    def populate_boundary_constraints(cls, value: object) -> object:
        """Populate boundary metadata when loading queries from older storage.

        Arguments:
            value: raw query data
        Returns:
            query data with deterministic editable-boundary constraints
        """
        if not isinstance(value, Mapping):
            return value
        boundary_keys = {"boundaries", cls.prompt.boundaries}
        if any(key in value for key in boundary_keys):
            return value

        targets_value = value.get(cls.prompt.targets, value.get("targets"))
        if not isinstance(targets_value, list) or not targets_value:
            return value
        target_text_values = [
            (
                target_value.get(cls.prompt.text, target_value.get("text"))
                if isinstance(target_value, Mapping)
                else target_value.text
                if isinstance(target_value, BlockDelineationSubtitle)
                else None
            )
            for target_value in targets_value
        ]
        if not all(isinstance(text_value, str) for text_value in target_text_values):
            return value
        target_texts = cast("list[str]", target_text_values)

        first_owned_index = value.get(
            cls.prompt.first_owned_index, value.get("first_owned_index", 1)
        )
        last_owned_index = value.get(
            cls.prompt.last_owned_index,
            value.get("last_owned_index", len(target_texts)),
        )
        if first_owned_index is None:
            first_owned_index = 1
        if last_owned_index is None:
            last_owned_index = len(target_texts)
        if not isinstance(first_owned_index, int) or not isinstance(
            last_owned_index, int
        ):
            return value

        constraints = cls._get_boundary_constraint_values(
            target_texts, first_owned_index, last_owned_index
        )
        updated_value = dict(value)
        updated_value[cls.prompt.boundaries] = [
            {
                cls.prompt.index: index,
                cls.prompt.original_offset: original_offset,
                cls.prompt.minimum_shift: minimum_shift,
                cls.prompt.maximum_shift: maximum_shift,
            }
            for index, original_offset, minimum_shift, maximum_shift in constraints
        ]
        return updated_value

    @model_validator(mode="after")
    def validate_indices(self) -> Self:
        """Ensure guide and target indexes correspond exactly."""
        guide_indexes = [guide.index for guide in self.guides]
        if guide_indexes != list(range(1, len(guide_indexes) + 1)):
            raise ValueError(self.prompt.guide_indices_err)
        target_indexes = [target.index for target in self.targets]
        if target_indexes != guide_indexes:
            raise ValueError(self.prompt.target_indices_err)
        if (self.first_owned_index is None) != (self.last_owned_index is None):
            raise ValueError(self.prompt.owned_indices_err)
        if self.first_owned_index is not None and (
            self.last_owned_index is None
            or self.first_owned_index > self.last_owned_index
            or self.last_owned_index > len(guide_indexes)
        ):
            raise ValueError(self.prompt.owned_indices_err)
        expected_boundaries = self._get_boundary_constraint_values(
            [target.text for target in self.targets],
            self.first_owned_index or 1,
            self.last_owned_index or len(self.targets),
        )
        received_boundaries = [
            (
                boundary.index,
                boundary.original_offset,
                boundary.minimum_shift,
                boundary.maximum_shift,
            )
            for boundary in self.boundaries
        ]
        if received_boundaries != expected_boundaries:
            raise ValueError(self.prompt.boundary_constraints_err)
        return self

    @staticmethod
    def _get_boundary_constraint_values(
        target_texts: list[str], first_owned_index: int, last_owned_index: int
    ) -> list[tuple[int, int, int, int]]:
        """Get deterministic editable-boundary constraint values.

        Arguments:
            target_texts: preliminary target texts in index order
            first_owned_index: first one-based editable boundary index
            last_owned_index: last one-based owned target or boundary index
        Returns:
            index, original offset, minimum shift, and maximum shift tuples
        """
        last_boundary_index = min(last_owned_index, len(target_texts) - 1)
        if first_owned_index > last_boundary_index:
            return []

        offsets = [0]
        for text in target_texts:
            offsets.append(offsets[-1] + len(text))
        return [
            (index, offsets[index], -offsets[index], offsets[-1] - offsets[index])
            for index in range(first_owned_index, last_boundary_index + 1)
        ]


class CandidateBlockDelineationQuery(BlockDelineationQuery):
    """Block delineation query restricted to supplied candidate cuts."""

    prompt: ClassVar[CandidateBlockDelineationPrompt] = (
        CandidateBlockDelineationPrompt()
    )
    """Text and field aliases for candidate block delineation."""
    boundaries: list[CandidateBlockDelineationBoundary] = Field(default_factory=list)
    """Editable boundaries and their timing-supported candidate cuts."""

    @model_validator(mode="after")
    def validate_boundary_candidates(self) -> Self:
        """Ensure each candidate list is ordered, complete, and internally valid."""
        for boundary in self.boundaries:
            shifts = [candidate.shift for candidate in boundary.candidates]
            if (
                shifts != sorted(set(shifts))
                or 0 not in shifts
                or any(
                    candidate.shift < boundary.minimum_shift
                    or candidate.shift > boundary.maximum_shift
                    or candidate.offset != boundary.original_offset + candidate.shift
                    for candidate in boundary.candidates
                )
            ):
                raise ValueError(self.prompt.boundary_candidates_err)
        return self


class AdvisoryBlockDelineationQuery(BlockDelineationQuery):
    """Block delineation query with non-binding timing-supported suggestions."""

    prompt: ClassVar[AdvisoryBlockDelineationPrompt] = _ADVISORY_PROMPT
    """Text and field aliases for advisory block delineation."""
    boundaries: list[AdvisoryBlockDelineationBoundary] = Field(default_factory=list)
    """Editable boundaries and their ranked timing-supported suggestions."""

    @model_validator(mode="after")
    def validate_boundary_suggestions(self) -> Self:
        """Ensure suggestions are ranked, complete, and internally valid."""
        for boundary in self.boundaries:
            ranks = [suggestion.rank for suggestion in boundary.suggestions]
            shifts = [suggestion.shift for suggestion in boundary.suggestions]
            if (
                ranks != list(range(1, len(ranks) + 1))
                or len(shifts) != len(set(shifts))
                or bool(shifts)
                and 0 not in shifts
                or any(
                    suggestion.shift < boundary.minimum_shift
                    or suggestion.shift > boundary.maximum_shift
                    or suggestion.offset != boundary.original_offset + suggestion.shift
                    for suggestion in boundary.suggestions
                )
            ):
                raise ValueError(self.prompt.boundary_suggestions_err)
        return self


type _LegacyTextAnswerData = tuple[
    BlockDelineationQuery, Mapping[str, object], str, list[str], list[str]
]
"""Parsed legacy replacement-text answer data used during migration."""


class BlockDelineationAnswer(Answer):
    """Sparse boundary movements for one query window."""

    prompt: ClassVar[BlockDelineationPrompt] = _BASE_PROMPT
    """Text and field aliases for block-level delineation."""
    changes: list[BlockDelineationBoundaryChange] = Field(default_factory=list)
    """Only target boundaries whose position must change."""

    @model_validator(mode="after")
    def validate_change_indices(self) -> Self:
        """Ensure sparse change indexes are ordered, unique, and nonzero."""
        indexes = [change.index for change in self.changes]
        if indexes != sorted(set(indexes)):
            raise ValueError(self.prompt.change_indices_err)
        if any(
            isinstance(change, BlockDelineationBoundaryChange) and not change.shift
            for change in self.changes
        ):
            raise ValueError(self.prompt.change_shift_zero_err)
        return self


class BlockDelineationTestCase(TestCase):
    """Block-delineation query and optional sparse answer."""

    query_cls: ClassVar[type[BlockDelineationQuery]] = BlockDelineationQuery
    """Query model class."""
    answer_cls: ClassVar[type[BlockDelineationAnswer]] = BlockDelineationAnswer
    """Answer model class."""
    prompt: ClassVar[BlockDelineationPrompt] = _BASE_PROMPT
    """Text and field aliases for block-level delineation."""
    query: BlockDelineationQuery
    """Complete guide and initial target block."""
    answer: BlockDelineationAnswer | None = None
    """Sparse delineation changes, if available."""

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty based on whether boundaries change.

        Returns:
            minimum difficulty
        """
        min_difficulty = super().get_min_difficulty()
        if self.answer is not None and self.answer.changes:
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    def get_no_op_answer(self) -> BlockDelineationAnswer:
        """Get a sparse answer that preserves the initial assignment.

        Returns:
            empty sparse-change answer
        """
        return self.answer_cls()

    def get_output_texts(self) -> list[str]:
        """Apply the answer to the immutable target character tape.

        Returns:
            complete target text after boundary changes
        """
        output = [target.text for target in self.query.targets]
        if self.answer is None or not self.answer.changes:
            return output

        first_change = self.answer.changes[0]
        if isinstance(first_change, BlockDelineationSubtitle):
            for change in cast("list[BlockDelineationSubtitle]", self.answer.changes):
                output[change.index - 1] = change.text
            return output

        character_tape = "".join(output)
        boundary_offsets = self._get_shifted_boundary_offsets(
            output, cast("list[BlockDelineationBoundaryChange]", self.answer.changes)
        )
        return [
            character_tape[start:end]
            for start, end in zip(
                boundary_offsets[:-1], boundary_offsets[1:], strict=True
            )
        ]

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_text_changes(cls, value: object) -> object:
        """Convert legacy replacement-text answers into boundary movements.

        Arguments:
            value: raw test-case data
        Returns:
            data using the current boundary-movement answer schema
        """
        legacy_data = cls._get_legacy_text_answer_data(value)
        if legacy_data is None:
            return value
        query, answer_value, changes_key, initial_texts, output_texts = legacy_data

        expected = "".join(initial_texts)
        received = "".join(output_texts)
        if expected != received:
            raise ValueError(cls.prompt.target_chars_changed_err(1, expected, received))

        initial_offsets = cls._get_text_offsets(initial_texts)
        output_offsets = cls._get_text_offsets(output_texts)
        converted_changes = []
        for index in query.owned_boundary_index_range:
            shift = output_offsets[index] - initial_offsets[index]
            if shift:
                converted_changes.append(
                    {cls.prompt.index: index, cls.prompt.shift: shift}
                )

        converted_answer = dict(answer_value)
        converted_answer.pop(changes_key, None)
        converted_answer[cls.prompt.changes] = converted_changes
        converted_value = dict(cast("Mapping[str, object]", value))
        converted_value["answer"] = converted_answer
        return converted_value

    @model_validator(mode="after")
    def validate_reconstructed_block(self) -> Self:
        """Ensure sparse changes define valid noncrossing target boundaries."""
        if self.answer is None:
            return self

        change_indexes = {change.index for change in self.answer.changes}
        if self.prompt.shift is None:
            if not change_indexes <= {target.index for target in self.query.targets}:
                raise ValueError(self.prompt.change_index_missing_err)
            target_text_by_index = {
                target.index: target.text for target in self.query.targets
            }
            output_text_by_index = dict(target_text_by_index)
            output_text_by_index.update(
                {
                    change.index: change.text
                    for change in cast(
                        "list[BlockDelineationSubtitle]", self.answer.changes
                    )
                }
            )
            expected = "".join(target_text_by_index.values())
            received = "".join(output_text_by_index.values())
            if expected != received:
                raise ValueError(
                    self.prompt.target_chars_changed_err(1, expected, received)
                )
            return self

        owned_boundary_indexes = set(self.query.owned_boundary_index_range)
        self.answer.changes = [
            change
            for change in self.answer.changes
            if change.index in owned_boundary_indexes
        ]
        target_texts = [target.text for target in self.query.targets]
        self._get_shifted_boundary_offsets(target_texts, self.answer.changes)
        return self

    @model_validator(mode="after")
    def validate_output_quality(self, info: ValidationInfo) -> Self:
        """Reject deterministic defects around reconstructed owned boundaries.

        Arguments:
            info: Pydantic validation context
        Returns:
            validated test case
        """
        context = info.context
        if (
            self.answer is None
            or not self.prompt.validate_output_quality
            or (
                isinstance(context, dict)
                and context.get("skip_output_quality_validation") is True
            )
        ):
            return self

        boundary_indexes = list(self.query.owned_boundary_index_range)
        if not boundary_indexes:
            return self
        output = self.get_output_texts()
        left_indexes = set(boundary_indexes)
        right_indexes = {index + 1 for index in boundary_indexes}
        affected_indexes = sorted(left_indexes | right_indexes)
        leading_closing_indexes: list[int] = []
        trailing_opening_indexes: list[int] = []
        punctuation_only_indexes: list[int] = []
        for index in affected_indexes:
            text = output[index - 1]
            stripped = text.strip()
            if text and not remove_punc_and_whitespace(text):
                punctuation_only_indexes.append(index)
                continue
            if (
                index in right_indexes
                and stripped
                and stripped[0] in _LEADING_CLOSING_PUNCTUATION
            ):
                leading_closing_indexes.append(index)
            if (
                index in left_indexes
                and stripped
                and stripped[-1] in _TRAILING_OPENING_PUNCTUATION
            ):
                trailing_opening_indexes.append(index)

        errors: list[str] = []
        if leading_closing_indexes:
            indexes = ", ".join(map(str, leading_closing_indexes))
            errors.append(
                self.prompt.leading_closing_punctuation_err_tpl.format(indexes=indexes)
            )
        if trailing_opening_indexes:
            indexes = ", ".join(map(str, trailing_opening_indexes))
            errors.append(
                self.prompt.trailing_opening_punctuation_err_tpl.format(indexes=indexes)
            )
        if punctuation_only_indexes:
            indexes = ", ".join(map(str, punctuation_only_indexes))
            errors.append(
                self.prompt.punctuation_only_target_err_tpl.format(indexes=indexes)
            )
        if errors:
            raise ValueError("\n".join(errors))
        return self

    @classmethod
    def _get_legacy_text_answer_data(
        cls, value: object
    ) -> _LegacyTextAnswerData | None:
        """Parse replacement-text answer data when it uses the legacy schema.

        Arguments:
            value: raw test-case data
        Returns:
            parsed migration inputs, or None when the answer is not legacy text
        """
        shift_field = cls.prompt.shift
        if shift_field is None or not isinstance(value, Mapping):
            return None
        value_mapping = cast("Mapping[str, object]", value)
        answer_value = value_mapping.get("answer")
        query_value = value_mapping.get("query")
        if not isinstance(answer_value, Mapping) or query_value is None:
            return None
        answer_mapping = cast("Mapping[str, object]", answer_value)

        changes_key = cls.prompt.changes
        if changes_key not in answer_mapping and "changes" in answer_mapping:
            changes_key = "changes"
        changes_value = answer_mapping.get(changes_key)
        if (
            not isinstance(changes_value, list)
            or not changes_value
            or not all(isinstance(change, Mapping) for change in changes_value)
        ):
            return None
        shift_keys = {"shift", shift_field}
        if any(
            any(shift_key in change for shift_key in shift_keys)
            for change in cast("list[Mapping[str, object]]", changes_value)
        ):
            return None

        query = cls.query_cls.model_validate(query_value)
        initial_texts = [target.text for target in query.targets]
        output_texts = list(initial_texts)
        for change_value in cast("list[Mapping[str, object]]", changes_value):
            index_value = change_value.get(cls.prompt.index)
            if index_value is None:
                index_value = change_value.get("index")
            text_value = change_value.get(cls.prompt.text)
            if text_value is None:
                text_value = change_value.get("text")
            if not isinstance(index_value, int) or not isinstance(text_value, str):
                return None
            if index_value < 1 or index_value > len(output_texts):
                raise ValueError(cls.prompt.change_index_missing_err)
            output_texts[index_value - 1] = text_value
        return query, answer_mapping, changes_key, initial_texts, output_texts

    def _get_shifted_boundary_offsets(
        self, texts: list[str], changes: list[BlockDelineationBoundaryChange]
    ) -> list[int]:
        """Apply explicit shifts and collapse preliminary cuts they cross.

        Returned shifts are simultaneous anchors relative to the preliminary
        boundaries. Unchanged boundaries between two anchors retain their original
        offsets when possible and collapse onto an anchor when it crosses them.

        Arguments:
            texts: preliminary target texts in index order
            changes: sparse explicit boundary shifts
        Returns:
            complete nondecreasing boundary offsets
        Raises:
            ValueError: if explicit shifted boundaries cross one another or the tape
        """
        original_boundary_offsets = self._get_text_offsets(texts)
        boundary_offsets = list(original_boundary_offsets)
        for change in changes:
            boundary_offsets[change.index] += change.shift

        anchor_indexes = [0, *(change.index for change in changes), len(texts)]
        for position in range(1, len(anchor_indexes) - 1):
            index = anchor_indexes[position]
            offset = boundary_offsets[index]
            previous_offset = boundary_offsets[anchor_indexes[position - 1]]
            next_offset = boundary_offsets[anchor_indexes[position + 1]]
            if not previous_offset <= offset <= next_offset:
                raise ValueError(
                    self.prompt.boundary_shift_invalid_err(
                        index,
                        offset,
                        original_boundary_offsets[index],
                        previous_offset,
                        next_offset,
                    )
                )
        for previous_index, next_index in zip(
            anchor_indexes[:-1], anchor_indexes[1:], strict=True
        ):
            previous_offset = boundary_offsets[previous_index]
            next_offset = boundary_offsets[next_index]
            for index in range(previous_index + 1, next_index):
                boundary_offsets[index] = min(
                    max(boundary_offsets[index], previous_offset), next_offset
                )
        return boundary_offsets

    @staticmethod
    def _get_text_offsets(texts: list[str]) -> list[int]:
        """Get cumulative character offsets for target text segments.

        Arguments:
            texts: target texts in index order
        Returns:
            zero followed by cumulative character offsets
        """
        offsets = [0]
        for text in texts:
            offsets.append(offsets[-1] + len(text))
        return offsets


class AdvisoryBlockDelineationTestCase(BlockDelineationTestCase):
    """Unrestricted block delineation with advisory timing suggestions."""

    query_cls: ClassVar[type[AdvisoryBlockDelineationQuery]] = (
        AdvisoryBlockDelineationQuery
    )
    """Query model class."""
    prompt: ClassVar[AdvisoryBlockDelineationPrompt] = (
        AdvisoryBlockDelineationQuery.prompt
    )
    """Text and field aliases for advisory block delineation."""
    query: AdvisoryBlockDelineationQuery
    """Guide, preliminary targets, legal shifts, and advisory timing cuts."""


class CandidateBlockDelineationTestCase(BlockDelineationTestCase):
    """Candidate-restricted block-delineation query and sparse answer."""

    query_cls: ClassVar[type[CandidateBlockDelineationQuery]] = (
        CandidateBlockDelineationQuery
    )
    """Query model class."""
    prompt: ClassVar[CandidateBlockDelineationPrompt] = (
        CandidateBlockDelineationQuery.prompt
    )
    """Text and field aliases for candidate block delineation."""
    query: CandidateBlockDelineationQuery
    """Guide, preliminary targets, and candidate cuts."""

    @model_validator(mode="after")
    def validate_candidate_shifts(self) -> Self:
        """Ensure every returned shift selects a supplied candidate cut."""
        if self.answer is None:
            return self
        boundary_by_index = {
            boundary.index: boundary for boundary in self.query.boundaries
        }
        for change in self.answer.changes:
            candidate_shifts = [
                candidate.shift
                for candidate in boundary_by_index[change.index].candidates
            ]
            if change.shift not in candidate_shifts:
                raise ValueError(
                    self.prompt.change_shift_not_candidate_err_tpl.format(
                        index=change.index, candidate_shifts=candidate_shifts
                    )
                )
        return self
