#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for translation matters."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Prompt

__all__ = ["TranslationPrompt"]


@dataclass(frozen=True, slots=True, kw_only=True)
class TranslationPrompt(Prompt):
    """Text for LLM correspondence for translation matters."""

    # Query fields
    subtitles: str = "subtitles"
    """Name of subtitles field in query."""

    subtitles_desc: str = "Subtitles to translate, in order."
    """Description of subtitles field in query."""

    # Answer fields
    outputs: str = "outputs"
    """Name of outputs field in answer."""

    outputs_desc: str = "Translated subtitles, in order."
    """Description of outputs field in answer."""

    # Subtitle fields
    index: str = "index"
    """Name of index field in subtitle and output items."""

    index_desc: str = "One-based subtitle index."
    """Description of index field in subtitle and output items."""

    text: str = "text"
    """Name of text field in subtitle and output items."""

    subtitle_text_desc: str = "Subtitle text to translate."
    """Description of text field in subtitle items."""

    output_text_desc: str = "Translated subtitle text."
    """Description of text field in output items."""

    # Query errors
    subtitle_indices_err: str = (
        "Query subtitle indexes must be consecutive, ordered, and begin at 1."
    )
    """Error when query subtitle indexes are invalid."""

    # Answer errors
    output_indices_err: str = (
        "Answer output indexes must be consecutive, ordered, and begin at 1."
    )
    """Error when answer output indexes are invalid."""

    # Test case errors
    output_correspondence_err: str = (
        "Answer output indexes must correspond exactly to query subtitle indexes."
    )
    """Error when answer outputs do not correspond to query subtitles."""

    # Dictionary tool
    dictionary_tool_name: str = ""
    """Name of dictionary lookup tool."""
    dictionary_tool_description: str = ""
    """Description of dictionary lookup tool."""
    dictionary_tool_query_description: str = ""
    """Description of dictionary lookup query."""
