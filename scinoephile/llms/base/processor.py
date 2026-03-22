#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Base processor for LLM workflows."""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from scinoephile.common.validation import val_output_path
from scinoephile.core.paths import get_runtime_cache_dir_path

from .queryer import Queryer
from .utils import load_test_cases_from_json

if TYPE_CHECKING:
    from pathlib import Path

    from .llm_provider import LLMToolSpec, ToolHandler
    from .manager import Manager
    from .prompt import Prompt
    from .test_case import TestCase

__all__ = ["Processor"]


class Processor(ABC):
    """Base processor for LLM workflows."""

    manager_cls: type[Manager] | None = None
    """Manager class used to construct test case models."""

    prompt_cls: type[Prompt]
    """Text for LLM correspondence."""

    def __init__(
        self,
        prompt_cls: type[Prompt],
        test_cases: list[TestCase] | None = None,
        test_case_path: Path | None = None,
        auto_verify: bool = False,
        tools: list[LLMToolSpec] | None = None,
        tool_handlers: dict[str, ToolHandler] | None = None,
    ):
        """Initialize.

        Arguments:
            prompt_cls: text for LLM correspondence
            test_cases: test cases
            test_case_path: path to file containing test cases
            auto_verify: automatically verify test cases if they meet selected criteria
            tools: available function-tool definitions
            tool_handlers: handlers for available function tools
        """
        self.prompt_cls = prompt_cls
        if self.manager_cls is None:
            raise ValueError("manager_cls must be set on Processor subclasses.")

        if test_cases is None:
            test_cases = []

        if test_case_path is not None:
            test_case_path = val_output_path(test_case_path, exist_ok=True)
            if test_case_path.exists():
                test_cases.extend(
                    load_test_cases_from_json(
                        test_case_path,
                        self.manager_cls,
                        prompt_cls=self.prompt_cls,
                    )
                )
        self.test_case_path = test_case_path
        """Path to file containing test cases."""

        queryer_cls = Queryer.get_queryer_cls(self.prompt_cls)
        self.queryer = queryer_cls(
            prompt_test_cases=[tc for tc in test_cases if tc.prompt],
            verified_test_cases=[tc for tc in test_cases if tc.verified],
            cache_dir_path=get_runtime_cache_dir_path("llm"),
            auto_verify=auto_verify,
            tools=tools,
            tool_handlers=tool_handlers,
        )
        """LLM queryer."""
