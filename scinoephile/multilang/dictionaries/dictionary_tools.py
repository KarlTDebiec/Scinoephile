#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""In-process dictionary tools for 粤文/中文 LLM workflows."""

from __future__ import annotations

from logging import getLogger
from typing import TypedDict

from scinoephile.core.llms.tools import LLMToolSpec, ToolHandler
from scinoephile.multilang.dictionaries.cuhk import CuhkDictionaryService

from .dictionary_tool_prompt import DictionaryToolPrompt
from .serialization import dictionary_entry_to_dict

__all__ = [
    "DictionaryToolPrompt",
    "get_dictionary_tools",
    "lookup_dictionary",
]
logger = getLogger(__name__)
"""Module logger."""


class DictionaryLookupResponse(TypedDict, total=False):
    """Dictionary tool response payload."""

    query: str
    """Lookup query."""

    result_count: int
    """Number of matching entries returned."""

    entries: list[dict[str, str | float | list[dict[str, str]]]]
    """Serialized dictionary entries."""

    error: str
    """Error message when lookup fails."""


def lookup_dictionary(
    query: str,
    *,
    auto_build_missing: bool = False,
) -> DictionaryLookupResponse:
    """Lookup entries in local dictionary data.

    Arguments:
        query: input query string
        auto_build_missing: build database automatically if missing
    Returns:
        lookup response payload
    """
    normalized_query = str(query).strip()
    if not normalized_query:
        return {
            "query": normalized_query,
            "result_count": 0,
            "entries": [],
            "error": "query must be non-empty",
        }

    service = CuhkDictionaryService(auto_build_missing=auto_build_missing)
    try:
        entries = service.lookup(query=normalized_query)
    except (FileNotFoundError, ValueError) as exc:
        logger.warning(f"Dictionary lookup failed: {exc}")
        return {
            "query": normalized_query,
            "result_count": 0,
            "entries": [],
            "error": str(exc),
        }
    logger.info(
        f"Dictionary lookup: query={normalized_query!r} result_count={len(entries)}"
    )
    return {
        "query": normalized_query,
        "result_count": len(entries),
        "entries": [dictionary_entry_to_dict(entry) for entry in entries],
    }


def _lookup_dictionary_from_args(
    arguments: dict[str, object],
) -> DictionaryLookupResponse:
    """Execute dictionary lookup from parsed tool-call arguments.

    Arguments:
        arguments: decoded tool-call JSON arguments
    Returns:
        lookup response payload
    """
    allowed_arguments = {"query"}
    unexpected_arguments = sorted(set(arguments) - allowed_arguments)
    if unexpected_arguments:
        query = str(arguments.get("query", "")).strip()
        return {
            "query": query,
            "result_count": 0,
            "entries": [],
            "error": ("unexpected arguments: " + ", ".join(unexpected_arguments)),
        }

    query = str(arguments.get("query", "")).strip()
    return lookup_dictionary(
        query=query,
        auto_build_missing=False,
    )


def get_dictionary_tools(
    prompt_cls: type[DictionaryToolPrompt],
) -> tuple[list[LLMToolSpec], dict[str, ToolHandler]]:
    """Get dictionary tool definitions and handlers for LLM providers.

    Arguments:
        prompt_cls: prompt class providing dictionary tool text
    Returns:
        tool definitions and corresponding tool handlers
    """
    tools: list[LLMToolSpec] = [
        {
            "name": prompt_cls.dictionary_tool_name,
            "description": prompt_cls.dictionary_tool_description,
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "required": ["query"],
                "properties": {
                    "query": {
                        "type": "string",
                        "description": prompt_cls.dictionary_tool_query_description,
                    },
                },
            },
        }
    ]
    handlers: dict[str, ToolHandler] = {
        prompt_cls.dictionary_tool_name: _lookup_dictionary_from_args,
    }
    return tools, handlers
