#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""In-process CUHK dictionary tools for 粤文/中文 LLM workflows."""

from __future__ import annotations

from logging import getLogger

from scinoephile.core.llms.tools import LLMToolSpec, ToolHandler
from scinoephile.multilang.dictionaries import DictionaryEntry
from scinoephile.multilang.dictionaries.sqlite_store import (
    CMN_TO_YUE_LOOKUP,
    SUPPORTED_LOOKUP_DIRECTIONS,
    YUE_TO_CMN_LOOKUP,
)

from .dictionaries.cuhk import CuhkDictionaryService
from .dictionaries.cuhk.constants import MAX_LOOKUP_LIMIT

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
    direction: str = CMN_TO_YUE_LOOKUP,
    limit: int = 10,
    *,
    auto_build_missing: bool = False,
) -> dict[str, object]:
    """Lookup entries in CUHK dictionary data.

    Arguments:
        query: input query string
        direction: lookup direction
        limit: max entries to return
        auto_build_missing: build database automatically if missing
    Returns:
        lookup response payload
    """
    normalized_query = str(query).strip()
    if not normalized_query:
        return {
            "query": normalized_query,
            "direction": direction,
            "result_count": 0,
            "entries": [],
            "error": "query must be non-empty",
        }

    try:
        direction = direction.strip()
    except AttributeError:
        direction = ""
    if direction not in SUPPORTED_LOOKUP_DIRECTIONS:
        return {
            "query": normalized_query,
            "direction": direction,
            "result_count": 0,
            "entries": [],
            "error": "direction must be 'cmn_to_yue' or 'yue_to_cmn'",
        }

    service = CuhkDictionaryService(auto_build_missing=auto_build_missing)
    try:
        entries = service.lookup(
            query=normalized_query,
            direction=direction,
            limit=min(MAX_LOOKUP_LIMIT, max(1, int(limit))),
        )
    except FileNotFoundError as exc:
        logger.warning("CUHK dictionary lookup unavailable: %s", exc)
        return {
            "query": normalized_query,
            "direction": direction,
            "result_count": 0,
            "entries": [],
            "error": str(exc),
        }
    logger.info(
        "CUHK dictionary lookup: query=%r direction=%s result_count=%d",
        normalized_query,
        direction,
        len(entries),
    )
    return {
        "query": normalized_query,
        "direction": direction,
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
    query = str(arguments.get("query", "")).strip()
    direction = str(
        arguments.get(
            "direction",
            CMN_TO_YUE_LOOKUP,
        )
    )

    limit_raw = arguments.get("limit", 10)
    if isinstance(limit_raw, int):
        limit = limit_raw
    elif isinstance(limit_raw, str):
        try:
            limit = int(limit_raw)
        except ValueError:
            limit = 10
    else:
        limit = 10

    return lookup_cuhk_dictionary(
        query=query,
        direction=direction,
        limit=limit,
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
                "現代標準漢語與粵語對照資料庫 dictionary."
            ),
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "required": ["query", "direction", "limit"],
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Mandarin or Cantonese lookup query.",
                    },
                    "direction": {
                        "type": "string",
                        "description": "Lookup direction.",
                        "enum": [
                            CMN_TO_YUE_LOOKUP,
                            YUE_TO_CMN_LOOKUP,
                        ],
                        "default": CMN_TO_YUE_LOOKUP,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of entries to return.",
                        "minimum": 1,
                        "maximum": 400,
                        "default": 10,
                    },
                },
            },
        }
    ]
    handlers: dict[str, ToolHandler] = {
        CUHK_LOOKUP_TOOL_NAME: _lookup_cuhk_dictionary_from_args,
    }
    return tools, handlers
