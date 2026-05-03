#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to interactions with LLMs."""

from __future__ import annotations

import importlib as _importlib
from collections.abc import Callable
from typing import Any

from .answer import Answer
from .llm_provider import ChatCompletionKwargs, LLMProvider
from .manager import Manager, TestCaseClsKwargs
from .openai_provider_base import OpenAIProviderBase
from .processor import Processor
from .prompt import Prompt
from .query import Query
from .queryer import Queryer
from .test_case import TestCase
from .tool import Tool
from .tool_box import ToolBox

_FUNCTION_EXPORT_MODULES = {
    "load_test_cases_from_json": ".utils",
    "save_test_cases_to_json": ".utils",
}

load_test_cases_from_json: Callable[..., Any]
"""Load test cases from a JSON file."""
save_test_cases_to_json: Callable[..., Any]
"""Save test cases to a JSON file."""

__all__ = [
    "Answer",
    "ChatCompletionKwargs",
    "LLMProvider",
    "Manager",
    "OpenAIProviderBase",
    "Processor",
    "Prompt",
    "Query",
    "Queryer",
    "TestCaseClsKwargs",
    "TestCase",
    "Tool",
    "ToolBox",
    "load_test_cases_from_json",
    "save_test_cases_to_json",
]


def __getattr__(name: str) -> object:
    """Load compatibility function exports lazily.

    Arguments:
        name: requested attribute name
    Returns:
        requested exported function
    Raises:
        AttributeError: if the attribute is not a lazy function export
    """
    if name not in _FUNCTION_EXPORT_MODULES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = _importlib.import_module(_FUNCTION_EXPORT_MODULES[name], __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value
