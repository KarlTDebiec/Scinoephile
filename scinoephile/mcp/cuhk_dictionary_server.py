#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MCP server exposing CUHK dictionary lookup tools."""

from __future__ import annotations

from typing import Literal

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError as exc:
    if exc.name is None or (
        exc.name != "mcp" and not exc.name.startswith("mcp.")
    ):
        raise

    # In some test runners, the local `test/mcp` package name can shadow the
    # third-party `mcp` dependency during import. Provide a minimal shim so
    # module import and unit tests still work; real MCP serving requires the
    # actual dependency.
    class FastMCP:  # pragma: no cover - exercised only in import-fallback path
        """Minimal fallback shim for test environments without importable MCP."""

        def __init__(self, _name: str, instructions: str = ""):
            self.instructions = instructions

        def tool(self, **_kwargs):
            """Return no-op decorator."""

            def decorator(func):
                return func

            return decorator

        def run(self, transport: str = "stdio"):
            """Raise clear runtime error if MCP dependency is unavailable."""
            raise ModuleNotFoundError(
                "Unable to import mcp.server.fastmcp. "
                "Install `mcp` and ensure it is not shadowed by local packages."
            )

from scinoephile.lang.yue.dictionaries import (
    CuhkDictionaryService,
    DictionaryEntry,
    LookupDirection,
)

__all__ = [
    "mcp",
    "main",
    "run",
]

mcp = FastMCP(
    "scinoephile-cuhk-dictionary",
    instructions=(
        "Provide Mandarin <-> Cantonese dictionary lookups from the "
        "CUHK 現代標準漢語與粵語對照資料庫."
    ),
)


def _entry_to_dict(entry: DictionaryEntry) -> dict[str, object]:
    """Convert dictionary entry to JSON-serializable structure.

    Arguments:
        entry: dictionary entry
    Returns:
        serialized entry
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


@mcp.tool(
    name="build_cuhk_dictionary_data",
    description=(
        "Build local CUHK dictionary cache and SQLite data. "
        "This operation may take a long time on first run."
    ),
)
def build_cuhk_dictionary_data(force_rebuild: bool = False) -> dict[str, object]:
    """Build CUHK dictionary cache.

    Arguments:
        force_rebuild: whether to rebuild from scratch
    Returns:
        build summary
    """
    service = CuhkDictionaryService(auto_build_missing=False)
    database_path = service.build(force_rebuild=force_rebuild)
    return {
        "database_path": str(database_path),
        "rebuilt": force_rebuild,
    }


@mcp.tool(
    name="lookup_cuhk_dictionary",
    description=(
        "Lookup CUHK dictionary entries in either Mandarin->Cantonese or "
        "Cantonese->Mandarin direction."
    ),
)
def lookup_cuhk_dictionary(
    query: str,
    direction: Literal[
        "mandarin_to_cantonese",
        "cantonese_to_mandarin",
    ] = "mandarin_to_cantonese",
    limit: int = 10,
    auto_build_missing: bool = False,
) -> dict[str, object]:
    """Lookup CUHK dictionary entries.

    Arguments:
        query: input query string
        direction: lookup direction
        limit: maximum number of entries to return
        auto_build_missing: automatically build CUHK data if missing
    Returns:
        lookup response payload
    """
    service = CuhkDictionaryService(auto_build_missing=auto_build_missing)
    direction_enum = LookupDirection(direction)
    entries = service.lookup(
        query=query,
        direction=direction_enum,
        limit=max(1, limit),
    )
    return {
        "query": query,
        "direction": direction_enum.value,
        "result_count": len(entries),
        "entries": [_entry_to_dict(entry) for entry in entries],
    }


def run(
    transport: Literal[
        "stdio",
        "sse",
        "streamable-http",
    ] = "stdio",
):
    """Run MCP server.

    Arguments:
        transport: MCP transport to use
    """
    mcp.run(transport=transport)


def main():
    """Run MCP server over stdio."""
    run("stdio")


if __name__ == "__main__":
    main()
