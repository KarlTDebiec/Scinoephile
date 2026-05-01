#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""In-process dictionary tools for 粤文/中文 LLM workflows."""

from __future__ import annotations

from logging import getLogger

from scinoephile.core.dictionaries import DictionaryLookupResponse, DictionaryToolPrompt
from scinoephile.core.dictionaries.serialization import dictionary_entry_to_dict
from scinoephile.core.llms.tool import Tool
from scinoephile.core.llms.tool_box import ToolBox
from scinoephile.dictionaries.lookup import lookup_dictionary_entries

__all__ = [
    "get_dictionary_tools",
    "lookup_dictionary",
]
logger = getLogger(__name__)
"""Module logger."""


def get_dictionary_tools(
    prompt_cls: type[DictionaryToolPrompt],
) -> ToolBox:
    """Get dictionary tool definitions and handlers for LLM providers.

    Arguments:
        prompt_cls: prompt class providing dictionary tool text
    Returns:
        tool box containing dictionary tooling
    """

    def lookup_dictionary_from_args(
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
        return lookup_dictionary(query=query, auto_build_missing=False)

    return ToolBox(
        [
            Tool(
                spec={
                    "name": prompt_cls.dictionary_tool_name,
                    "description": prompt_cls.dictionary_tool_description,
                    "parameters": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["query"],
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": (
                                    prompt_cls.dictionary_tool_query_description
                                ),
                            },
                        },
                    },
                },
                handler=lookup_dictionary_from_args,
            )
        ]
    )


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

    try:
        entries = lookup_dictionary_entries(
            query=normalized_query,
            limit=10,
            auto_build_missing=auto_build_missing,
        )
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
