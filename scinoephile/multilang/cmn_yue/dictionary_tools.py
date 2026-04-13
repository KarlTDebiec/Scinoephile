#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""In-process CUHK dictionary tools for 粤文/中文 LLM workflows."""

from __future__ import annotations

from logging import getLogger

from scinoephile.core.llms.tools import LLMToolSpec, ToolHandler
from scinoephile.multilang.dictionaries import DictionaryEntry

from .dictionaries.cuhk import CuhkDictionaryService

__all__ = [
    "CUHK_LOOKUP_TOOL_NAME",
    "get_cuhk_dictionary_tooling",
    "lookup_cuhk_dictionary",
]

CUHK_LOOKUP_TOOL_NAME = "lookup_cuhk_dictionary"
"""Tool name for CUHK dictionary lookups."""

logger = getLogger(__name__)
"""Module logger."""


def _entry_to_dict(entry: DictionaryEntry) -> dict[str, object]:
    """Convert one dictionary entry into a JSON-serializable payload.

    Arguments:
        entry: dictionary entry
    Returns:
        serialized dictionary entry
    """
    return {
        "traditional": entry.traditional,
        "simplified": entry.simplified,
        "pinyin": entry.pinyin,
        "jyutping": entry.jyutping,
        "frequency": entry.frequency,
        "definitions": [
            {
                "label": definition.label,
                "text": definition.text,
            }
            for definition in entry.definitions
        ],
    }


def lookup_cuhk_dictionary(
    query: str,
    *,
    auto_build_missing: bool = False,
) -> dict[str, object]:
    """Lookup entries in CUHK dictionary data.

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
        entries = service.lookup_inferred(query=normalized_query)
    except (FileNotFoundError, ValueError) as exc:
        logger.warning("CUHK dictionary lookup failed: %s", exc)
        return {
            "query": normalized_query,
            "result_count": 0,
            "entries": [],
            "error": str(exc),
        }
    logger.info(
        "CUHK dictionary lookup: query=%r result_count=%d",
        normalized_query,
        len(entries),
    )
    return {
        "query": normalized_query,
        "result_count": len(entries),
        "entries": [_entry_to_dict(entry) for entry in entries],
    }


def _lookup_cuhk_dictionary_from_args(
    arguments: dict[str, object],
) -> dict[str, object]:
    """Execute CUHK dictionary lookup from parsed tool-call arguments.

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
    return lookup_cuhk_dictionary(
        query=query,
        auto_build_missing=False,
    )


def get_cuhk_dictionary_tooling() -> tuple[list[LLMToolSpec], dict[str, ToolHandler]]:
    """Get CUHK dictionary tool definitions and handlers for LLM providers.

    Returns:
        tool definitions and corresponding tool handlers
    """
    tools: list[LLMToolSpec] = [
        {
            "name": CUHK_LOOKUP_TOOL_NAME,
            "description": (
                "Lookup Cantonese <-> Mandarin entries from the CUHK "
                "現代標準漢語與粵語對照資料庫 dictionary. "
                "The tool automatically infers whether the query is Hanzi, "
                "pinyin, or jyutping."
            ),
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "required": ["query"],
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Mandarin or Cantonese lookup query in Hanzi, "
                            "pinyin, or jyutping."
                        ),
                    },
                },
            },
        }
    ]
    handlers: dict[str, ToolHandler] = {
        CUHK_LOOKUP_TOOL_NAME: _lookup_cuhk_dictionary_from_args,
    }
    return tools, handlers
