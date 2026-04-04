#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to interactions with LLMs."""

from __future__ import annotations

from . import llm_provider as _llm_provider
from . import manager as _manager
from . import tools as _tools
from . import utils as _utils
from .answer import Answer
from .llm_provider import LLMProvider
from .manager import Manager
from .processor import Processor
from .prompt import Prompt
from .query import Query
from .queryer import Queryer
from .test_case import TestCase

ChatCompletionKwargs = _llm_provider.ChatCompletionKwargs
LLMToolSpec = _tools.LLMToolSpec
TestCaseClsKwargs = _manager.TestCaseClsKwargs
ToolHandler = _tools.ToolHandler
load_test_cases_from_json = _utils.load_test_cases_from_json
save_test_cases_to_json = _utils.save_test_cases_to_json

__all__ = [
    "Answer",
    "ChatCompletionKwargs",
    "LLMProvider",
    "LLMToolSpec",
    "Manager",
    "Processor",
    "Prompt",
    "Query",
    "Queryer",
    "TestCaseClsKwargs",
    "TestCase",
    "ToolHandler",
    "load_test_cases_from_json",
    "save_test_cases_to_json",
]
