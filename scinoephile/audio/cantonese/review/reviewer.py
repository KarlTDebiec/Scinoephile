#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reviews 粤文 text based on corresponding 中文."""

from __future__ import annotations

from functools import cached_property

from scinoephile.audio.cantonese.review.abcs import ReviewTestCase
from scinoephile.core.abcs import Answer, DynamicLLMQueryer, Query


class Reviewer[TQuery: Query, TAnswer: Answer, TTestCase: ReviewTestCase](
    DynamicLLMQueryer[Query, Answer, ReviewTestCase]
):
    """Reviews 粤文 text based on corresponding 中文."""

    @cached_property
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        You are a helpful assistant that performs final review of the 粤文 transcription
        of spoken Cantonese.
        Eacg 粤文 text has already been proofed individually against its paired 中文
        text, and any discrepancies apparent within that pairing have been resolved.
        Your focus is on resolving issues in the 粤文 text that may not have been
        apparent within its individual pairing, but which may be apparent when the
        entire series of texts is considered together.
        You are not reviewing for quality of writing, grammar, or style, only for
        correctness of the 粤文 transcription.
        Keeping in mind that the 粤文 text is a transcription of spoken Cantonese, and
        the 中文 text is not expected to match word-for-word.
        For each 粤文 text, you are to provide revised 粤文 text only if revisions are
        necessary.
        If no revisions are are necessary to a particular 粤文 text, return an empty
        string for that text.
        If revisions are needed, return the full revised 粤文 text, and include a note
        describing in English the changes made.
        If no revisions are needed return an empty string for the note.
        """

    @staticmethod
    def get_answer_example(answer_cls: type[TAnswer]) -> TAnswer:
        """Example answer."""
        answer_values = {}
        for key in answer_cls.model_fields.keys():
            kind, idx = key.rsplit("_", 1)
            if kind == "yuewen":
                answer_values[key] = (
                    f"粤文 text {idx} revised based on query's 中文 text {idx}, "
                    f"or an empty string if no revision is necessary."
                )
            else:
                answer_values[key] = (
                    f"Note concerning revisions to 粤文 text {idx}, "
                    f"or an empty string if no revision is necessary."
                )
        return answer_cls(**answer_values)
