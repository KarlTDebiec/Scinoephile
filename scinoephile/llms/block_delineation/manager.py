#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific block-delineation LLM classes."""

from __future__ import annotations

from functools import cache
from typing import ClassVar

from scinoephile.core.llms import Answer, Manager, PromptModelField, Query, TestCase
from scinoephile.core.llms.models import LLMModel

from .models import (
    AdvisoryBlockDelineationBoundary,
    AdvisoryBlockDelineationBoundarySuggestion,
    AdvisoryBlockDelineationQuery,
    AdvisoryBlockDelineationTestCase,
    BlockDelineationAnswer,
    BlockDelineationBoundary,
    BlockDelineationBoundaryCandidate,
    BlockDelineationBoundaryChange,
    BlockDelineationQuery,
    BlockDelineationSubtitle,
    BlockDelineationTestCase,
    CandidateBlockDelineationBoundary,
    CandidateBlockDelineationQuery,
    CandidateBlockDelineationTestCase,
)
from .prompt import (
    AdvisoryBlockDelineationPrompt,
    BlockDelineationPrompt,
    CandidateBlockDelineationPrompt,
)

__all__ = [
    "AdvisoryBlockDelineationManager",
    "BlockDelineationManager",
    "CandidateBlockDelineationManager",
]


class BlockDelineationManager(Manager[BlockDelineationTestCase]):
    """Factories for prompt-specific block-delineation LLM classes."""

    operation: ClassVar[str] = "block-delineation"
    """Stable operation identifier used in persistence."""
    base_prompt: ClassVar[BlockDelineationPrompt] = BlockDelineationTestCase.prompt
    """Base prompt defining persisted field names."""
    test_case_base_cls: ClassVar[type[TestCase]] = BlockDelineationTestCase
    """Static test-case model defining block delineation's semantic shape."""

    @classmethod
    @cache
    def get_answer_cls(cls, prompt: BlockDelineationPrompt) -> type[Answer]:
        """Get answer class with prompt-specific field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            answer model class
        """
        change_cls = cls.get_change_cls(prompt)
        return cls.create_prompt_model(
            BlockDelineationAnswer,
            prompt,
            {
                "changes": PromptModelField(
                    alias=prompt.changes,
                    annotation=list[change_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.changes_desc,
                )
            },
        )

    @classmethod
    @cache
    def get_change_cls(cls, prompt: BlockDelineationPrompt) -> type[LLMModel]:
        """Get sparse-change item class with prompt-specific aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            sparse-change item model class
        """
        fields = {
            "index": PromptModelField(alias=prompt.index, description=prompt.index_desc)
        }
        if prompt.shift is None:
            fields["text"] = PromptModelField(
                alias=prompt.text, description=prompt.change_text_desc
            )
            base_cls: type[LLMModel] = BlockDelineationSubtitle
            name = "BlockDelineationTextChange"
        else:
            fields["shift"] = PromptModelField(
                alias=prompt.shift, description=prompt.shift_desc
            )
            base_cls = BlockDelineationBoundaryChange
            name = "BlockDelineationBoundaryChange"
        return cls.create_prompt_model(base_cls, prompt, fields, name=name)

    @classmethod
    @cache
    def get_boundary_cls(
        cls, prompt: BlockDelineationPrompt
    ) -> type[BlockDelineationBoundary]:
        """Get editable-boundary item class with prompt-specific aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            editable-boundary item model class
        """
        return cls.create_prompt_model(
            BlockDelineationBoundary,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index, description=prompt.index_desc
                ),
                "original_offset": PromptModelField(
                    alias=prompt.original_offset,
                    description=prompt.original_offset_desc,
                ),
                "minimum_shift": PromptModelField(
                    alias=prompt.minimum_shift, description=prompt.minimum_shift_desc
                ),
                "maximum_shift": PromptModelField(
                    alias=prompt.maximum_shift, description=prompt.maximum_shift_desc
                ),
            },
            name="BlockDelineationBoundary",
        )

    @classmethod
    @cache
    def get_guide_cls(
        cls, prompt: BlockDelineationPrompt
    ) -> type[BlockDelineationSubtitle]:
        """Get guide item class with prompt-specific aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            guide item model class
        """
        return cls.create_prompt_model(
            BlockDelineationSubtitle,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index, description=prompt.index_desc
                ),
                "text": PromptModelField(
                    alias=prompt.text, description=prompt.guide_text_desc
                ),
            },
            name="BlockDelineationGuide",
        )

    @classmethod
    @cache
    def get_query_cls(cls, prompt: BlockDelineationPrompt) -> type[Query]:
        """Get query class with prompt-specific field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            query model class
        """
        guide_cls = cls.get_guide_cls(prompt)
        target_cls = cls.get_target_cls(prompt)
        boundary_cls = cls.get_boundary_cls(prompt)
        return cls.create_prompt_model(
            BlockDelineationQuery,
            prompt,
            {
                "guides": PromptModelField(
                    alias=prompt.guides,
                    annotation=list[guide_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.guides_desc,
                ),
                "targets": PromptModelField(
                    alias=prompt.targets,
                    annotation=list[target_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.targets_desc,
                ),
                "first_owned_index": PromptModelField(
                    alias=prompt.first_owned_index,
                    description=prompt.first_owned_index_desc,
                ),
                "last_owned_index": PromptModelField(
                    alias=prompt.last_owned_index,
                    description=prompt.last_owned_index_desc,
                ),
                "boundaries": PromptModelField(
                    alias=prompt.boundaries,
                    annotation=list[boundary_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.boundaries_desc,
                ),
            },
        )

    @classmethod
    @cache
    def get_target_cls(
        cls, prompt: BlockDelineationPrompt
    ) -> type[BlockDelineationSubtitle]:
        """Get initial-target item class with prompt-specific aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            initial-target item model class
        """
        return cls.create_prompt_model(
            BlockDelineationSubtitle,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index, description=prompt.index_desc
                ),
                "text": PromptModelField(
                    alias=prompt.text, description=prompt.target_text_desc
                ),
            },
            name="BlockDelineationTarget",
        )


class AdvisoryBlockDelineationManager(BlockDelineationManager):
    """Factories for block delineation with advisory timing suggestions."""

    operation: ClassVar[str] = "advisory-block-delineation"
    """Stable operation identifier used in persistence."""
    base_prompt: ClassVar[AdvisoryBlockDelineationPrompt] = (
        AdvisoryBlockDelineationTestCase.prompt
    )
    """Base prompt defining persisted field names."""
    test_case_base_cls: ClassVar[type[TestCase]] = AdvisoryBlockDelineationTestCase
    """Static test-case model defining advisory delineation's semantic shape."""

    @classmethod
    @cache
    def get_boundary_cls(
        cls, prompt: AdvisoryBlockDelineationPrompt
    ) -> type[AdvisoryBlockDelineationBoundary]:
        """Get advisory boundary class with prompt-specific aliases."""
        suggestion_cls = cls.get_boundary_suggestion_cls(prompt)
        return cls.create_prompt_model(
            AdvisoryBlockDelineationBoundary,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index, description=prompt.index_desc
                ),
                "original_offset": PromptModelField(
                    alias=prompt.original_offset,
                    description=prompt.original_offset_desc,
                ),
                "minimum_shift": PromptModelField(
                    alias=prompt.minimum_shift, description=prompt.minimum_shift_desc
                ),
                "maximum_shift": PromptModelField(
                    alias=prompt.maximum_shift, description=prompt.maximum_shift_desc
                ),
                "suggestions": PromptModelField(
                    alias=prompt.suggestions,
                    annotation=list[suggestion_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.suggestions_desc,
                ),
            },
            name="AdvisoryBlockDelineationBoundary",
        )

    @classmethod
    @cache
    def get_boundary_suggestion_cls(
        cls, prompt: AdvisoryBlockDelineationPrompt
    ) -> type[AdvisoryBlockDelineationBoundarySuggestion]:
        """Get timing-suggestion class with prompt-specific aliases."""
        return cls.create_prompt_model(
            AdvisoryBlockDelineationBoundarySuggestion,
            prompt,
            {
                "rank": PromptModelField(
                    alias=prompt.suggestion_rank,
                    description=prompt.suggestion_rank_desc,
                ),
                "shift": PromptModelField(
                    alias=prompt.shift or "shift", description=prompt.shift_desc
                ),
                "offset": PromptModelField(
                    alias=prompt.suggestion_offset,
                    description=prompt.suggestion_offset_desc,
                ),
                "left_context": PromptModelField(
                    alias=prompt.suggestion_left_context,
                    description=prompt.suggestion_left_context_desc,
                ),
                "right_context": PromptModelField(
                    alias=prompt.suggestion_right_context,
                    description=prompt.suggestion_right_context_desc,
                ),
                "timing_delta_ms": PromptModelField(
                    alias=prompt.suggestion_timing_delta_ms,
                    description=prompt.suggestion_timing_delta_ms_desc,
                ),
                "pause_ms": PromptModelField(
                    alias=prompt.suggestion_pause_ms,
                    description=prompt.suggestion_pause_ms_desc,
                ),
            },
            name="AdvisoryBlockDelineationBoundarySuggestion",
        )

    @classmethod
    @cache
    def get_query_cls(cls, prompt: AdvisoryBlockDelineationPrompt) -> type[Query]:
        """Get advisory block query class with prompt-specific aliases."""
        guide_cls = cls.get_guide_cls(prompt)
        target_cls = cls.get_target_cls(prompt)
        boundary_cls = cls.get_boundary_cls(prompt)
        return cls.create_prompt_model(
            AdvisoryBlockDelineationQuery,
            prompt,
            {
                "guides": PromptModelField(
                    alias=prompt.guides,
                    annotation=list[guide_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.guides_desc,
                ),
                "targets": PromptModelField(
                    alias=prompt.targets,
                    annotation=list[target_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.targets_desc,
                ),
                "first_owned_index": PromptModelField(
                    alias=prompt.first_owned_index,
                    description=prompt.first_owned_index_desc,
                ),
                "last_owned_index": PromptModelField(
                    alias=prompt.last_owned_index,
                    description=prompt.last_owned_index_desc,
                ),
                "boundaries": PromptModelField(
                    alias=prompt.boundaries,
                    annotation=list[boundary_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.boundaries_desc,
                ),
            },
        )


class CandidateBlockDelineationManager(BlockDelineationManager):
    """Factories for prompt-specific candidate block-delineation classes."""

    operation: ClassVar[str] = "candidate-block-delineation"
    """Stable operation identifier used in persistence."""
    base_prompt: ClassVar[CandidateBlockDelineationPrompt] = (
        CandidateBlockDelineationTestCase.prompt
    )
    """Base prompt defining persisted field names."""
    test_case_base_cls: ClassVar[type[TestCase]] = CandidateBlockDelineationTestCase
    """Static test-case model defining candidate delineation's semantic shape."""

    @classmethod
    @cache
    def get_boundary_candidate_cls(
        cls, prompt: CandidateBlockDelineationPrompt
    ) -> type[BlockDelineationBoundaryCandidate]:
        """Get candidate-cut class with prompt-specific aliases."""
        return cls.create_prompt_model(
            BlockDelineationBoundaryCandidate,
            prompt,
            {
                "shift": PromptModelField(
                    alias=prompt.shift or "shift", description=prompt.shift_desc
                ),
                "offset": PromptModelField(
                    alias=prompt.candidate_offset,
                    description=prompt.candidate_offset_desc,
                ),
                "left_context": PromptModelField(
                    alias=prompt.candidate_left_context,
                    description=prompt.candidate_left_context_desc,
                ),
                "right_context": PromptModelField(
                    alias=prompt.candidate_right_context,
                    description=prompt.candidate_right_context_desc,
                ),
                "timing_delta_ms": PromptModelField(
                    alias=prompt.candidate_timing_delta_ms,
                    description=prompt.candidate_timing_delta_ms_desc,
                ),
                "pause_ms": PromptModelField(
                    alias=prompt.candidate_pause_ms,
                    description=prompt.candidate_pause_ms_desc,
                ),
            },
            name="BlockDelineationBoundaryCandidate",
        )

    @classmethod
    @cache
    def get_boundary_cls(
        cls, prompt: CandidateBlockDelineationPrompt
    ) -> type[CandidateBlockDelineationBoundary]:
        """Get candidate-bearing boundary class with prompt-specific aliases."""
        candidate_cls = cls.get_boundary_candidate_cls(prompt)
        return cls.create_prompt_model(
            CandidateBlockDelineationBoundary,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index, description=prompt.index_desc
                ),
                "original_offset": PromptModelField(
                    alias=prompt.original_offset,
                    description=prompt.original_offset_desc,
                ),
                "minimum_shift": PromptModelField(
                    alias=prompt.minimum_shift, description=prompt.minimum_shift_desc
                ),
                "maximum_shift": PromptModelField(
                    alias=prompt.maximum_shift, description=prompt.maximum_shift_desc
                ),
                "candidates": PromptModelField(
                    alias=prompt.candidates,
                    annotation=list[candidate_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.candidates_desc,
                ),
            },
            name="CandidateBlockDelineationBoundary",
        )

    @classmethod
    @cache
    def get_query_cls(cls, prompt: CandidateBlockDelineationPrompt) -> type[Query]:
        """Get candidate block query class with prompt-specific aliases."""
        guide_cls = cls.get_guide_cls(prompt)
        target_cls = cls.get_target_cls(prompt)
        boundary_cls = cls.get_boundary_cls(prompt)
        return cls.create_prompt_model(
            CandidateBlockDelineationQuery,
            prompt,
            {
                "guides": PromptModelField(
                    alias=prompt.guides,
                    annotation=list[guide_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.guides_desc,
                ),
                "targets": PromptModelField(
                    alias=prompt.targets,
                    annotation=list[target_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.targets_desc,
                ),
                "first_owned_index": PromptModelField(
                    alias=prompt.first_owned_index,
                    description=prompt.first_owned_index_desc,
                ),
                "last_owned_index": PromptModelField(
                    alias=prompt.last_owned_index,
                    description=prompt.last_owned_index_desc,
                ),
                "boundaries": PromptModelField(
                    alias=prompt.boundaries,
                    annotation=list[boundary_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.boundaries_desc,
                ),
            },
        )
