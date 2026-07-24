#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Base processor for LLM workflows."""

from __future__ import annotations

from abc import ABC
from pathlib import Path
from typing import TypedDict

from scinoephile.core.paths import get_runtime_cache_dir_path

from .llm_provider import LLMProvider
from .manager import Manager
from .prompt import Prompt
from .queryer import Queryer
from .test_case import TestCase
from .tool_box import ToolBox
from .utils import load_test_cases, save_test_cases_to_json

__all__ = [
    "Processor",
    "ProcessorKwargs",
]


class ProcessorKwargs(TypedDict, total=False):
    """Keyword arguments commonly forwarded to Processor initialization."""

    additional_context: str | None
    """Additional context to include in the system prompt."""

    auto_verify: bool
    """Whether generated test cases should be marked verified."""

    cache_dir_path: Path | None
    """Directory in which to cache LLM responses."""

    overwrite_cache: bool
    """Whether matching LLM response cache files should be replaced."""

    prune_test_cases: bool
    """Whether to remove persisted test cases not encountered in the current run."""

    test_case_path: Path | None
    """Path where test cases are persisted."""

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
        test_cases: list[TestCase] | None = None,
        test_case_path: Path | None = None,
        *,
        provider: LLMProvider,
        additional_context: str | None = None,
        auto_verify: bool = False,
        cache_dir_path: Path | None = None,
        overwrite_cache: bool = False,
        prune_test_cases: bool = False,
        tool_box: ToolBox | None = None,
    ):
        """Initialize.

        Arguments:
            prompt: text for LLM correspondence
            test_cases: test cases
            test_case_path: path to file containing test cases
            provider: provider to use for queries
            additional_context: additional context to include in the system prompt
            auto_verify: automatically verify test cases if they meet selected criteria
            cache_dir_path: directory in which to cache LLM responses
            overwrite_cache: whether to replace matching LLM response cache files
            prune_test_cases: remove persisted cases not encountered in this run
            tool_box: available tools and handlers
        """
        self.prompt = prompt
        if self.manager_cls is None:
            raise ValueError("manager_cls must be set on Processor subclasses.")
        self.test_case_cls = self.manager_cls.get_test_case_cls(self.prompt)

        test_cases, test_case_path = load_test_cases(
            self.manager_cls,
            self.prompt,
            test_cases=test_cases,
            test_case_path=test_case_path,
        )
        self.test_case_path = test_case_path
        """Path to file containing test cases."""
        self.prune_test_cases = prune_test_cases
        """Whether to remove persisted cases not encountered in the current run."""

        if cache_dir_path is None:
            cache_dir_path = get_runtime_cache_dir_path("llm")
        self.queryer = Queryer(
            self.test_case_cls,
            verified_test_cases=[tc for tc in test_cases if tc.verified],
            provider=provider,
            cache_dir_path=cache_dir_path,
            additional_context=additional_context,
            auto_verify=auto_verify,
            overwrite_cache=overwrite_cache,
            tool_box=tool_box,
        )
        """LLM queryer."""

    def save_test_cases(self):
        """Persist encountered test cases."""
        if self.test_case_path is None or self.manager_cls is None:
            return
        save_test_cases_to_json(
            self.test_case_path,
            self.queryer.encountered_test_cases.values(),
            self.manager_cls,
            prune=self.prune_test_cases,
        )
