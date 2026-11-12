#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Filter OCR concerns and assemble subtitle blocks for the editor."""

from __future__ import annotations

from scinoephile.operations.subtitle_search import parse_block_query
from scinoephile.web.blocks import SubtitleBlock

from .concerns import FILTER_OPTIONS, get_review_status
from .session import OcrValidationSession

__all__ = ["get_filtered_blocks"]


def get_filtered_blocks(
    session: OcrValidationSession, status: str, query: str
) -> tuple[list[SubtitleBlock[int]], dict[str, int], int]:
    """Filter the track by concern, text, subtitle number, or block number.

    Arguments:
        session: current OCR validation session
        status: requested concern status
        query: search text, subtitle number, or a block selector
    Returns:
        matching blocks, status counts within the search, and total validated rows
    """
    concerns = session.subtitle_concerns()
    counts = dict.fromkeys(("all", *FILTER_OPTIONS), 0)
    block_query = parse_block_query(query)
    query = query.casefold()
    blocks = []
    for number, (first, last) in enumerate(session.block_ranges, 1):
        if block_query is not None and block_query != number:
            continue
        visible = []
        for index in range(first, last):
            entry = session.entries[index]
            if (
                block_query is None
                and query not in f"{entry.index} {entry.text}".casefold()
            ):
                continue
            kind = get_review_status(concerns[index])
            counts["all"] += 1
            counts[kind] += 1
            if kind != "done":
                counts["needs-review"] += 1
            if status in {"all", kind} or (status == "needs-review" and kind != "done"):
                visible.append(index)
        if visible:
            blocks.append(
                SubtitleBlock(
                    number=number,
                    first_index=first + 1,
                    last_index=last,
                    rows=visible,
                    start=session.entries[first].start,
                    end=max(entry.end for entry in session.entries[first:last]),
                )
            )
    return blocks, counts, concerns.count(None)
