#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for block-level transcription punctuation."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Prompt
from scinoephile.llms._text_validation import get_text_mismatch_details

__all__ = ["BlockPunctuationPrompt"]


@dataclass(frozen=True, slots=True, kw_only=True)
class BlockPunctuationPrompt(Prompt):
    """Text and field aliases for block-level punctuation."""

    guides: str = "guides"
    """Name of guide subtitles field in query."""
    guides_desc: str = "Complete indexed guide subtitles for one query window."
    """Description of guide subtitles field in query."""
    targets: str = "targets"
    """Name of delineated target subtitles field in query."""
    targets_desc: str = "Complete indexed delineated targets for one query window."
    """Description of delineated target subtitles field in query."""
    first_owned_index: str = "first_owned_index"
    """Name of first owned local index field in query."""
    first_owned_index_desc: str = "First local target index owned by this window."
    """Description of first owned local index field in query."""
    last_owned_index: str = "last_owned_index"
    """Name of last owned local index field in query."""
    last_owned_index_desc: str = "Last local target index owned by this window."
    """Description of last owned local index field in query."""
    changes: str = "changes"
    """Name of sparse punctuation changes field in answer."""
    changes_desc: str = "Only target subtitles whose punctuation must change."
    """Description of sparse punctuation changes field in answer."""
    index: str = "index"
    """Name of index field in subtitle items."""
    index_desc: str = "One-based guide subtitle index."
    """Description of subtitle item indexes."""
    text: str = "text"
    """Name of text field in subtitle items."""
    guide_text_desc: str = "Guide subtitle text."
    """Description of guide subtitle text."""
    target_text_desc: str = "Delineated target subtitle text."
    """Description of delineated target subtitle text."""
    change_text_desc: str = "Replacement punctuated text for this changed index."
    """Description of changed punctuated target text."""
    guide_indices_err: str = (
        "Query guide indexes must be consecutive, ordered, and begin at 1."
    )
    """Error when query guide indexes are invalid."""
    target_indices_err: str = (
        "Query target indexes must correspond exactly to query guide indexes."
    )
    """Error when query target indexes do not match guides."""
    owned_indices_err: str = (
        "Query owned indexes must either both be omitted or define an ordered "
        "inclusive range within the query indexes."
    )
    """Error when query owned indexes are invalid."""
    change_indices_err: str = (
        "Answer change indexes must be unique and in ascending order."
    )
    """Error when answer change indexes are invalid."""
    change_index_missing_err: str = (
        "Every answer change index must correspond to a query guide index."
    )
    """Error when an answer change index is absent from the guide."""
    change_index_not_owned_err: str = (
        "Every answer change index must be within the query's owned index range."
    )
    """Error when an answer changes a context-only index."""
    leading_closing_punctuation_err_tpl: str = (
        "Final owned target indexes {indexes} begin with closing sentence "
        "punctuation. Remove that stranded leading punctuation, or place equivalent "
        "punctuation at the end of the appropriate owned target."
    )
    """Error template when final owned text begins with closing punctuation."""
    punctuation_only_target_err_tpl: str = (
        "Final owned target indexes {indexes} contain punctuation or whitespace but "
        "no target characters. Return those indexes with empty text."
    )
    """Error template when final owned text contains only punctuation."""
    half_width_sentence_punctuation_err_tpl: str = (
        "Final owned target indexes {indexes} contain Hanzi together with half-width "
        "sentence punctuation {characters}. Replace it with the corresponding "
        "full-width Chinese punctuation without changing target characters."
    )
    """Error template when Hanzi text contains half-width sentence punctuation."""
    interrogative_target_err_tpl: str = (
        "Final owned target indexes {indexes} have both a question guide and a "
        "strong Cantonese interrogative cue, but contain no question mark. "
        "Use appropriate full-width question punctuation without changing target "
        "characters."
    )
    """Error template when a strongly supported question lacks a question mark."""
    target_chars_changed_err_tpl: str = (
        "Punctuation change at index {index} does not preserve its target "
        "characters after removing punctuation and whitespace. The first mismatch "
        "is at zero-based character offset {offset}: expected {expected_character}, "
        "received {received_character}.\nExpected context: {expected_context}\n"
        "Received context: {received_context}\nExpected: {expected}\n"
        "Received: {received}"
    )
    """Error template when a punctuation change alters target characters."""
    validate_output_quality: bool = False
    """Whether to reject deterministic punctuation-layout defects."""

    def target_chars_changed_err(self, index: int, expected: str, received: str) -> str:
        """Get an error for changed target characters at one index.

        Arguments:
            index: one-based guide subtitle index
            expected: expected target characters
            received: received target characters
        Returns:
            formatted error message
        """
        return self.target_chars_changed_err_tpl.format(
            index=index,
            expected=expected,
            received=received,
            **get_text_mismatch_details(expected, received),
        )
