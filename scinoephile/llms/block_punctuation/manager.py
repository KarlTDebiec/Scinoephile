#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific block-punctuation LLM classes."""

from __future__ import annotations

from functools import cache
from typing import ClassVar

from scinoephile.core.llms import Answer, Manager, PromptModelField, Query, TestCase
from scinoephile.core.llms.models import LLMModel

from .models import (
    BlockPunctuationAnswer,
    BlockPunctuationQuery,
    BlockPunctuationSubtitle,
    BlockPunctuationTestCase,
    PositionalBlockPunctuationAnswer,
    PositionalBlockPunctuationChange,
    PositionalBlockPunctuationEdit,
    PositionalBlockPunctuationTarget,
    PositionalBlockPunctuationTestCase,
)
from .prompt import BlockPunctuationPrompt, PositionalBlockPunctuationPrompt

__all__ = ["BlockPunctuationManager", "PositionalBlockPunctuationManager"]


class BlockPunctuationManager(Manager[BlockPunctuationTestCase]):
    """Factories for prompt-specific block-punctuation LLM classes."""

    operation: ClassVar[str] = "block-punctuation"
    """Stable operation identifier used in persistence."""
    base_prompt: ClassVar[BlockPunctuationPrompt] = BlockPunctuationTestCase.prompt
    """Base prompt defining persisted field names."""
    test_case_base_cls: ClassVar[type[TestCase]] = BlockPunctuationTestCase
    """Static test-case model defining block punctuation's semantic shape."""

    @classmethod
    @cache
    def get_answer_cls(cls, prompt: BlockPunctuationPrompt) -> type[Answer]:
        """Get answer class with prompt-specific field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            answer model class
        """
        change_cls = cls.get_change_cls(prompt)
        return cls.create_prompt_model(
            BlockPunctuationAnswer,
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
    def get_change_cls(
        cls, prompt: BlockPunctuationPrompt
    ) -> type[BlockPunctuationSubtitle]:
        """Get sparse-change item class with prompt-specific aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            sparse-change item model class
        """
        return cls.create_prompt_model(
            BlockPunctuationSubtitle,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index, description=prompt.index_desc
                ),
                "text": PromptModelField(
                    alias=prompt.text, description=prompt.change_text_desc
                ),
            },
            name="BlockPunctuationChange",
        )

    @classmethod
    @cache
    def get_guide_cls(
        cls, prompt: BlockPunctuationPrompt
    ) -> type[BlockPunctuationSubtitle]:
        """Get guide item class with prompt-specific aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            guide item model class
        """
        return cls.create_prompt_model(
            BlockPunctuationSubtitle,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index, description=prompt.index_desc
                ),
                "text": PromptModelField(
                    alias=prompt.text, description=prompt.guide_text_desc
                ),
            },
            name="BlockPunctuationGuide",
        )

    @classmethod
    @cache
    def get_query_cls(cls, prompt: BlockPunctuationPrompt) -> type[Query]:
        """Get query class with prompt-specific field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            query model class
        """
        guide_cls = cls.get_guide_cls(prompt)
        target_cls = cls.get_target_cls(prompt)
        return cls.create_prompt_model(
            BlockPunctuationQuery,
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
            },
        )

    @classmethod
    @cache
    def get_target_cls(
        cls, prompt: BlockPunctuationPrompt
    ) -> type[BlockPunctuationSubtitle]:
        """Get delineated-target item class with prompt-specific aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            delineated-target item model class
        """
        return cls.create_prompt_model(
            BlockPunctuationSubtitle,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index, description=prompt.index_desc
                ),
                "text": PromptModelField(
                    alias=prompt.text, description=prompt.target_text_desc
                ),
            },
            name="BlockPunctuationTarget",
        )


class PositionalBlockPunctuationManager(BlockPunctuationManager):
    """Factories for prompt-specific positional block-punctuation classes."""

    operation: ClassVar[str] = "positional-block-punctuation"
    """Stable operation identifier used in persistence."""
    base_prompt: ClassVar[PositionalBlockPunctuationPrompt] = (
        PositionalBlockPunctuationTestCase.prompt
    )
    """Base prompt defining persisted field names."""
    test_case_base_cls: ClassVar[type[TestCase]] = PositionalBlockPunctuationTestCase
    """Static test-case model defining positional punctuation's semantic shape."""

    @classmethod
    @cache
    def get_edit_cls(
        cls, prompt: PositionalBlockPunctuationPrompt
    ) -> type[PositionalBlockPunctuationEdit]:
        """Get positional punctuation-edit class with prompt-specific aliases."""
        return cls.create_prompt_model(
            PositionalBlockPunctuationEdit,
            prompt,
            {
                "position": PromptModelField(
                    alias=prompt.position, description=prompt.position_desc
                ),
                "punctuation": PromptModelField(
                    alias=prompt.punctuation, description=prompt.punctuation_desc
                ),
            },
            name="PositionalBlockPunctuationEdit",
        )

    @classmethod
    @cache
    def get_change_cls(cls, prompt: PositionalBlockPunctuationPrompt) -> type[LLMModel]:
        """Get positional target-change class with prompt-specific aliases."""
        edit_cls = cls.get_edit_cls(prompt)
        return cls.create_prompt_model(
            PositionalBlockPunctuationChange,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index, description=prompt.index_desc
                ),
                "edits": PromptModelField(
                    alias=prompt.edits,
                    annotation=list[edit_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.edits_desc,
                ),
            },
            name="PositionalBlockPunctuationChange",
        )

    @classmethod
    @cache
    def get_answer_cls(cls, prompt: PositionalBlockPunctuationPrompt) -> type[Answer]:
        """Get positional answer class with prompt-specific aliases."""
        change_cls = cls.get_change_cls(prompt)
        return cls.create_prompt_model(
            PositionalBlockPunctuationAnswer,
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
    def get_target_cls(
        cls, prompt: PositionalBlockPunctuationPrompt
    ) -> type[PositionalBlockPunctuationTarget]:
        """Get counted immutable-target class with prompt-specific aliases."""
        target_cls = cls.create_prompt_model(
            PositionalBlockPunctuationTarget,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index, description=prompt.index_desc
                ),
                "text": PromptModelField(
                    alias=prompt.text, description=prompt.target_text_desc
                ),
                "character_count": PromptModelField(
                    alias=prompt.character_count,
                    description=prompt.character_count_desc,
                ),
            },
            name="PositionalBlockPunctuationTarget",
        )
        target_cls.prompt = prompt
        return target_cls
