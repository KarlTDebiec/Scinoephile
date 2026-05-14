#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to interactions with LLMs.

Package hierarchy (modules may import from any above):
* models / prompt / tool
* answer / query / tool_box
* llm_provider / test_case
* manager / openai_provider_base / queryer
* operation_spec / utils
* processor
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .answer import Answer
from .llm_provider import ChatCompletionKwargs, LLMProvider
from .manager import Manager, TestCaseClsKwargs
from .operation_spec import OperationSpec
from .processor import Processor
from .prompt import Prompt
from .query import Query
from .queryer import Queryer
from .test_case import TestCase
from .tool import Tool
from .tool_box import ToolBox

__all__ = [
    "Answer",
    "ChatCompletionKwargs",
    "LLMProvider",
    "Manager",
    "OpenAIProviderBase",
    "OperationSpec",
    "Processor",
    "Prompt",
    "Query",
    "Queryer",
    "TestCaseClsKwargs",
    "TestCase",
    "Tool",
    "ToolBox",
]

if TYPE_CHECKING:
    from .openai_provider_base import OpenAIProviderBase


def __getattr__(name: str) -> object:
    """Import optional LLM provider implementations on demand.

    Arguments:
        name: requested module attribute name
    Returns:
        requested optional component
    Raises:
        AttributeError: if the requested attribute is not exported here
    """
    if name == "OpenAIProviderBase":
        from .openai_provider_base import OpenAIProviderBase  # noqa: PLC0415

        return OpenAIProviderBase
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
