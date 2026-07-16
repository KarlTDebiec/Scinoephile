#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for punctuation."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Prompt

__all__ = ["PunctuationPrompt"]


@dataclass(frozen=True, slots=True, kw_only=True)
class PunctuationPrompt(Prompt):
    """Text for LLM correspondence for punctuation."""

    # Query fields
    ref_sub: str = "ref_sub"
    """Name of reference subtitle field in query."""

    ref_sub_desc: str = "Reference subtitle text"
    """Description of reference subtitle field in query."""

    target_subs: str = "target_subs"
    """Name of target subtitles field in query."""

    target_subs_desc: str = "Target subtitle texts to combine and punctuate"
    """Description of target subtitles field in query."""

    # Query validation errors
    ref_sub_missing_err: str = "Reference subtitle text is required."
    """Error when reference subtitle field is missing from query."""

    target_subs_missing_err: str = "Target subtitle texts are required."
    """Error when target subtitles field is missing from query."""

    # Answer fields
    target_sub_punctuated: str = "target_sub_punctuated"
    """Name of punctuated target subtitle field in answer."""

    target_sub_punctuated_desc: str = "Combined and punctuated target subtitle text"
    """Description of punctuated target subtitle field in answer."""

    # Answer validation errors
    target_sub_punctuated_missing_err: str = (
        "Combined and punctuated target subtitle text is required."
    )
    """Error when punctuated target subtitle field is missing from answer."""

    # Test case validation errors
    target_chars_changed_err_tpl: str = (
        "Answer's punctuated target subtitle stripped of punctuation and whitespace "
        "does not match query's target subtitles concatenated:\n"
        "Expected: {expected}\n"
        "Received: {received}"
    )
    """Error when punctuated target characters do not match target subtitles."""

    def target_chars_changed_err(self, expected: str, received: str) -> str:
        """Error when punctuated target characters do not match target subtitles.

        Arguments:
            expected: expected target subtitle characters
            received: received punctuated target subtitle characters
        Returns:
            error message
        """
        return self.target_chars_changed_err_tpl.format(
            expected=expected,
            received=received,
        )
