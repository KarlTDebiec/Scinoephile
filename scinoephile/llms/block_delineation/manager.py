#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific block-delineation LLM classes."""

from __future__ import annotations

from functools import cache
from typing import ClassVar

from scinoephile.core.llms import Answer, Manager, PromptModelField, Query, TestCase

from .models import (
    BlockDelineationAnswer,
    BlockDelineationQuery,
    BlockDelineationSubtitle,
    BlockDelineationTestCase,
)
from .prompt import BlockDelineationPrompt

__all__ = ["BlockDelineationManager"]


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
    def get_change_cls(
        cls, prompt: BlockDelineationPrompt
    ) -> type[BlockDelineationSubtitle]:
        """Get sparse-change item class with prompt-specific aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            sparse-change item model class
        """
        return cls.create_prompt_model(
            BlockDelineationSubtitle,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index, description=prompt.index_desc
                ),
                "text": PromptModelField(
                    alias=prompt.text, description=prompt.change_text_desc
                ),
            },
            name="BlockDelineationChange",
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
