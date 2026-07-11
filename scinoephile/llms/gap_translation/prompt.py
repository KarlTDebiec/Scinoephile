#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for gap translation matters."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Prompt

__all__ = ["GapTranslationPrompt"]


@dataclass(frozen=True, slots=True, kw_only=True)
class GapTranslationPrompt(Prompt):
    """Text for LLM correspondence for gap translation matters."""

    # Query fields
    targets: str = "targets"
    """Name of targets field in query."""

    targets_desc: str = "Existing target subtitles, indexed by guide position."
    """Description of targets field in query."""

    guides: str = "guides"
    """Name of guides field in query."""

    guides_desc: str = "Complete guide subtitles, in order."
    """Description of guides field in query."""

    # Answer fields
    outputs: str = "outputs"
    """Name of outputs field in answer."""

    outputs_desc: str = "Translations for guide indexes missing from targets."
    """Description of outputs field in answer."""

    # Subtitle fields
    index: str = "index"
    """Name of index field in target, guide, and output items."""

    index_desc: str = "One-based subtitle index."
    """Description of index field in target, guide, and output items."""

    text: str = "text"
    """Name of text field in target, guide, and output items."""

    target_text_desc: str = "Existing target subtitle text."
    """Description of text field in target items."""

    guide_text_desc: str = "Guide subtitle text."
    """Description of text field in guide items."""

    output_text_desc: str = (
        "Translated target subtitle text, or an empty string if none is needed."
    )
    """Description of text field in output items."""

    # Query validation errors
    guide_indices_err: str = (
        "Query guide indexes must be consecutive, ordered, and begin at 1."
    )
    """Error when guide indexes are invalid."""

    target_indices_err: str = (
        "Query target indexes must be unique and in ascending order."
    )
    """Error when target indexes are invalid."""

    target_index_missing_err: str = (
        "Every query target index must correspond to a guide index."
    )
    """Error when a target index is absent from the guides."""

    target_gap_missing_err: str = (
        "Query targets must omit at least one guide index for translation."
    )
    """Error when targets contain every guide index."""

    # Answer validation errors
    output_indices_err: str = (
        "Answer output indexes must be unique and in ascending order."
    )
    """Error when output indexes are invalid."""

    # Test case validation errors
    output_indices_mismatch_err: str = (
        "Answer output indexes must exactly match guide indexes missing from targets."
    )
    """Error when output indexes do not match target gaps."""

    # Dictionary tool
    dictionary_tool_name: str = ""
    """Name of dictionary lookup tool."""
    dictionary_tool_description: str = ""
    """Description of dictionary lookup tool."""
    dictionary_tool_query_description: str = ""
    """Description of dictionary lookup query."""
