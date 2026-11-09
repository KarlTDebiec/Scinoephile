#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific proofreading audit models."""

from __future__ import annotations

from functools import cache
from typing import ClassVar

from scinoephile.core.llms import Manager, TestCase

from .models import ReviewAuditAnswer, ReviewAuditQuery, ReviewAuditTestCase
from .prompt import ReviewAuditPrompt

__all__ = ["ReviewAuditManager"]


class ReviewAuditManager(Manager[ReviewAuditTestCase]):
    """Bind an audit prompt to models with a fixed JSON schema."""

    operation: ClassVar[str] = ReviewAuditTestCase.operation
    """Stable operation identifier used in persistence."""
    base_prompt: ClassVar[ReviewAuditPrompt] = ReviewAuditTestCase.prompt
    """Base prompt defining the expected audit prompt type."""
    test_case_base_cls: ClassVar[type[TestCase]] = ReviewAuditTestCase
    """Static test-case model defining the audit schema."""

    @classmethod
    @cache
    def get_answer_cls(cls, prompt: ReviewAuditPrompt) -> type[ReviewAuditAnswer]:
        """Get the answer model bound to the audit prompt.

        Arguments:
            prompt: text for LLM correspondence
        Returns:
            prompt-specific answer model class
        """
        return cls.create_prompt_model(ReviewAuditAnswer, prompt, {})

    @classmethod
    @cache
    def get_query_cls(cls, prompt: ReviewAuditPrompt) -> type[ReviewAuditQuery]:
        """Get the query model bound to the audit prompt.

        Arguments:
            prompt: text for LLM correspondence
        Returns:
            prompt-specific query model class
        """
        return cls.create_prompt_model(ReviewAuditQuery, prompt, {})
