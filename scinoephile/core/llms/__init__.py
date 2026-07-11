#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to interactions with LLMs.

Package hierarchy (modules may import from any above):
* models / prompt / test_case_subtitle / tool
* answer / query / tool_box
* llm_provider / test_case
* manager / openai_provider_base / queryer
* utils
* processor
"""

from __future__ import annotations

from .answer import Answer
from .llm_provider import ChatCompletionKwargs, LLMProvider
from .manager import Manager
from .openai_provider_base import OpenAIProviderBase
from .processor import Processor, ProcessorKwargs
from .prompt import Prompt, PromptLocalizationFields
from .query import Query
from .queryer import Queryer
from .test_case import TestCase
from .test_case_subtitle import AnnotatedTestCaseSubtitle, TestCaseSubtitle
from .tool import Tool
from .tool_box import ToolBox

__all__ = [
    "AnnotatedTestCaseSubtitle",
    "Answer",
    "ChatCompletionKwargs",
    "LLMProvider",
    "Manager",
    "OpenAIProviderBase",
    "Processor",
    "ProcessorKwargs",
    "Prompt",
    "PromptLocalizationFields",
    "Query",
    "Queryer",
    "TestCase",
    "TestCaseSubtitle",
    "Tool",
    "ToolBox",
]
