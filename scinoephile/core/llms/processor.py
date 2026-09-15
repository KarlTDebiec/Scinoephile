#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Base processor for LLM workflows."""

from __future__ import annotations

from abc import ABC
from pathlib import Path
from typing import TypedDict

from scinoephile.common.validation import val_output_path

from .llm_provider import LLMProvider
from .manager import Manager
from .prompt import Prompt
from .queryer import Queryer
from .test_case import TestCase
from .tool_box import ToolBox
from .utils import load_test_cases_from_json, save_test_cases_to_json

__all__ = ["Processor", "ProcessorKwargs"]


class ProcessorKwargs(TypedDict, total=False):
    """Keyword arguments commonly forwarded to Processor initialization."""

    additional_context: str | None
    """Additional context to include in the system prompt."""

    auto_verify: bool
    """Whether generated test cases should be marked verified."""

    cache_root_path: Path | None
    """Root directory beneath which to cache LLM responses."""

    no_op: bool
    """Whether to use neutral answers instead of querying an LLM."""

    overwrite_cache: bool
    """Whether matching LLM response cache files should be replaced."""

    prune_test_cases: bool
    """Whether to remove persisted test cases not encountered in the current run."""

    current_test_cases_path: Path | None
    """Current configuration's test-case JSON path."""

    tool_box: ToolBox | None
    """Available tools and handlers."""


class Processor(ABC):
    """Base processor for LLM workflows."""

    manager_cls: type[Manager] | None = None
    """Manager class used to construct test case models."""

    prompt: Prompt
    """Text for LLM correspondence."""
    test_case_cls: type[TestCase]
    """Test-case class for the configured prompt."""

    def __init__(
        self,
        prompt: Prompt,
        shared_test_cases: list[TestCase] | None = None,
        current_test_cases_path: Path | None = None,
        *,
        provider: LLMProvider,
        additional_context: str | None = None,
        auto_verify: bool = False,
        cache_root_path: Path | None = None,
        no_op: bool = False,
        overwrite_cache: bool = False,
        prune_test_cases: bool = False,
        tool_box: ToolBox | None = None,
    ):
        """Initialize.

        Arguments:
            prompt: text for LLM correspondence
            shared_test_cases: known test cases shared across configurations
            current_test_cases_path: current configuration's test-case JSON path
            provider: provider to use for queries
            additional_context: additional context to include in the system prompt
            auto_verify: automatically verify test cases if they meet selected criteria
            cache_root_path: root directory beneath which to cache LLM responses
            no_op: use neutral answers instead of querying the LLM
            overwrite_cache: whether to replace matching LLM response cache files
            prune_test_cases: remove persisted cases not encountered in this run
            tool_box: available tools and handlers
        Raises:
            ValueError: if a value is invalid
        """
        self.prompt = prompt
        if self.manager_cls is None:
            raise ValueError("manager_cls must be set on Processor subclasses.")
        self.test_case_cls = self.manager_cls.get_test_case_cls(self.prompt)

        if current_test_cases_path is not None:
            current_test_cases_path = val_output_path(
                current_test_cases_path, exist_ok=True
            )
        current_test_cases = []
        if current_test_cases_path is not None and current_test_cases_path.exists():
            current_test_cases = load_test_cases_from_json(
                current_test_cases_path, self.manager_cls, self.prompt
            )
        verified_test_cases = [
            test_case
            for test_case in [*(shared_test_cases or []), *current_test_cases]
            if test_case.verified
        ]
        self._current_test_cases_by_key = {
            test_case.query.key: test_case for test_case in current_test_cases
        }
        """Current configuration's in-memory test cases keyed by query."""
        self.current_test_cases_path = current_test_cases_path
        """Current configuration's test-case JSON path."""
        self.prune_test_cases = prune_test_cases
        """Whether to remove persisted cases not encountered in the current run."""

        self.queryer = Queryer(
            self.test_case_cls,
            verified_test_cases=verified_test_cases,
            provider=provider,
            cache_root_path=cache_root_path,
            additional_context=additional_context,
            auto_verify=auto_verify,
            no_op=no_op,
            overwrite_cache=overwrite_cache,
            tool_box=tool_box,
        )
        """LLM queryer."""

    def save_encountered_test_cases(self):
        """Persist encountered test cases."""
        if self.current_test_cases_path is None or self.manager_cls is None:
            return

        # Update the in-memory collection, optionally pruning unencountered cases
        if self.prune_test_cases:
            self._current_test_cases_by_key.clear()
        self._current_test_cases_by_key.update(self.queryer.encountered_test_cases)

        save_test_cases_to_json(
            self.current_test_cases_path,
            self._current_test_cases_by_key.values(),
            self.manager_cls,
        )
