#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""In-process dictionary tools for 粤文/中文 LLM workflows."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path

from scinoephile.core.dictionaries import DictionaryLookupResult, LookupDirection
from scinoephile.core.llms.tools import LLMToolSpec, ToolHandler

from .dictionaries.constants import MAX_LOOKUP_LIMIT
from .dictionaries.service import CmnYueDictionaryService

__all__ = [
    "LOOKUP_TOOL_NAME",
    "get_dictionary_tooling",
    "lookup_dictionary",
]

LOOKUP_TOOL_NAME = "lookup_dictionary"
"""Tool name for generic dictionary lookups."""

logger = getLogger(__name__)
"""Module logger."""


def _entry_to_dict(result: DictionaryLookupResult) -> dict[str, object]:
    """Convert one lookup result into a JSON-serializable payload.

    Arguments:
        result: source-tagged dictionary lookup result
    Returns:
        serialized lookup result
    """
    entry = result.entry
    return {
        "source": {
            "id": result.source_id,
            "shortname": result.source.shortname,
            "name": result.source.name,
        },
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


def lookup_dictionary(
    query: str,
    direction: str = LookupDirection.CMN_TO_YUE.value,
    limit: int = 10,
    *,
    database_paths: list[Path] | None = None,
    sources: list[str] | None = None,
) -> dict[str, object]:
    """Lookup entries in installed dictionary data.

    Arguments:
        query: input query string
        direction: lookup direction
        limit: max entries to return
        database_paths: explicit database paths to search
        sources: optional source filters
    Returns:
        lookup response payload
    """
    normalized_query = str(query).strip()
    normalized_sources = [source.strip() for source in sources or [] if source.strip()]
    if not normalized_query:
        return {
            "query": normalized_query,
            "direction": direction,
            "sources": normalized_sources,
            "result_count": 0,
            "entries": [],
            "error": "query must be non-empty",
        }

    try:
        direction_enum = LookupDirection(direction.strip())
    except ValueError:
        return {
            "query": normalized_query,
            "direction": direction,
            "sources": normalized_sources,
            "result_count": 0,
            "entries": [],
            "error": "direction must be 'cmn_to_yue' or 'yue_to_cmn'",
        }

    service = CmnYueDictionaryService(database_paths=database_paths)
    try:
        results = service.lookup(
            query=normalized_query,
            direction=direction_enum,
            limit=min(MAX_LOOKUP_LIMIT, max(1, int(limit))),
            source_ids=normalized_sources or None,
        )
    except (FileNotFoundError, ValueError) as exc:
        logger.warning("Dictionary lookup unavailable: %s", exc)
        return {
            "query": normalized_query,
            "direction": direction_enum.value,
            "sources": normalized_sources,
            "result_count": 0,
            "entries": [],
            "error": str(exc),
        }
    logger.info(
        "Dictionary lookup: query=%r direction=%s source_count=%d result_count=%d",
        normalized_query,
        direction_enum.value,
        len(normalized_sources),
        len(results),
    )
    return {
        "query": normalized_query,
        "direction": direction_enum.value,
        "sources": normalized_sources,
        "result_count": len(results),
        "entries": [_entry_to_dict(result) for result in results],
    }


def _lookup_dictionary_from_args(
    arguments: dict[str, object],
) -> dict[str, object]:
    """Execute generic dictionary lookup from parsed tool-call arguments.

    Arguments:
        arguments: decoded tool-call JSON arguments
    Returns:
        lookup response payload
    """
    query = str(arguments.get("query", "")).strip()
    direction = str(
        arguments.get(
            "direction",
            LookupDirection.CMN_TO_YUE.value,
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

    sources_raw = arguments.get("sources", [])
    if isinstance(sources_raw, list):
        sources = [str(source).strip() for source in sources_raw if str(source).strip()]
    elif isinstance(sources_raw, str) and sources_raw.strip():
        sources = [sources_raw.strip()]
    else:
        sources = []

    return lookup_dictionary(
        query=query,
        direction=direction,
        limit=limit,
        sources=sources,
    )


def get_dictionary_tooling() -> tuple[list[LLMToolSpec], dict[str, ToolHandler]]:
    """Get generic dictionary tool definitions and handlers for LLM providers.

    Returns:
        tool definitions and corresponding tool handlers
    """
    tools: list[LLMToolSpec] = [
        {
            "name": LOOKUP_TOOL_NAME,
            "description": (
                "Lookup Cantonese <-> Mandarin entries from installed "
                "Scinoephile dictionary sources."
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
                            LookupDirection.CMN_TO_YUE.value,
                            LookupDirection.YUE_TO_CMN.value,
                        ],
                        "default": LookupDirection.CMN_TO_YUE.value,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of entries to return.",
                        "minimum": 1,
                        "maximum": 400,
                        "default": 10,
                    },
                    "sources": {
                        "type": "array",
                        "description": (
                            "Optional list of source ids to search, such as 'cuhk'."
                        ),
                        "items": {
                            "type": "string",
                        },
                    },
                },
            },
        }
    ]
    handlers: dict[str, ToolHandler] = {
        LOOKUP_TOOL_NAME: _lookup_dictionary_from_args,
    }
    return tools, handlers
