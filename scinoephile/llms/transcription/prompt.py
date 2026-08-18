#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for transcription from aligned ASR sources."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Prompt

__all__ = ["TranscriptionPrompt"]


@dataclass(frozen=True, slots=True, kw_only=True)
class TranscriptionPrompt(Prompt):
    """Text and aliases for transcription."""

    sources: str = "sources"
    """Name of aligned transcription source rows field."""
    sources_desc: str = (
        "One or more named equal-status ASR rows aligned by Unicode column."
    )
    """Description of aligned transcription source rows field."""
    source_name: str = "name"
    """Name of transcription source name field."""
    source_name_desc: str = "Stable name identifying one ASR source."
    """Description of transcription source name field."""
    source_text: str = "text"
    """Name of aligned transcription row text field."""
    source_text_desc: str = (
        "One character, fullwidth gap, or fullwidth pause marker per alignment column."
    )
    """Description of aligned transcription row text field."""
    speaker: str = "speaker"
    """Name of speaker row field."""
    speaker_desc: str = (
        "Column-aligned fullwidth speaker labels and gap or timed-pause markers."
    )
    """Description of speaker row field."""
    answer_text: str = "text"
    """Name of consensus text field in answer."""
    answer_text_desc: str = (
        "Complete consensus transcript with a fullwidth vertical bar after every "
        "display subtitle, or an empty string when no identifiable speech is present."
    )
    """Description of consensus text field in answer."""

    source_name_err: str = (
        "ASR source names must be nonblank and unique within the query."
    )
    """Error when source names are blank or duplicated."""
    reference_source_err: str = (
        "Transcription queries may contain ASR sources only, not a reference or guide."
    )
    """Error when a reference-like source is included."""
    row_length_err: str = (
        "All ASR and speaker rows in a query must have equal nonzero lengths."
    )
    """Error when aligned row lengths differ."""
    reference_marker_err: str = (
        "Transcription queries must not contain reference boundary markers."
    )
    """Error when an aligned row contains a reference boundary marker."""
    speaker_character_err: str = (
        "Speaker rows may contain only fullwidth speaker labels, fullwidth asterisks, "
        "fullwidth gaps, and fullwidth timed-pause markers."
    )
    """Error when a speaker row contains an unknown annotation."""
    transcript_empty_err: str = "Transcription queries must contain transcribed text."
    """Error when every ASR row contains only gaps."""
    answer_text_err: str = (
        "Answer text must be empty, or contain nonblank subtitles separated and "
        "terminated by fullwidth vertical bars without alignment or speaker "
        "annotations."
    )
    """Error when answer text or subtitle boundaries are invalid."""
    answer_punctuation_err: str = (
        "Answer text must not contain punctuation or symbol characters other than "
        "fullwidth subtitle boundaries."
    )
    """Error when punctuation appears in answer text."""
    subtitle_length_err_tpl: str = (
        "Answer subtitle indexes {indexes} exceed the maximum of "
        "{max_characters} nonwhitespace characters."
    )
    """Error template when answer subtitles exceed the configured maximum length."""
    consensus_omission_err_tpl: str = (
        "The answer omitted or replaced {count} consecutive high-confidence "
        "majority ASR columns ({consensus}); no more than {maximum} consecutive "
        "columns may be omitted or replaced. Re-read that aligned span and return "
        "the complete transcript in order."
    )
    """Error template when an answer omits a long consensus span."""

    def consensus_omission_err(
        self, consensus: str, maximum_unpreserved_columns: int
    ) -> str:
        """Get an error for a long unpreserved majority span.

        Arguments:
            consensus: representative text of the unpreserved majority span
            maximum_unpreserved_columns: maximum permitted consecutive omissions
        Returns:
            formatted error message
        """
        return self.consensus_omission_err_tpl.format(
            consensus=consensus,
            count=len(consensus),
            maximum=maximum_unpreserved_columns,
        )

    def subtitle_length_err(self, indexes: list[int], max_characters: int) -> str:
        """Get an error for subtitles exceeding the configured maximum length.

        Arguments:
            indexes: one-based indexes of subtitles that are too long
            max_characters: maximum permitted nonwhitespace characters
        Returns:
            formatted error message
        """
        return self.subtitle_length_err_tpl.format(
            indexes=", ".join(str(index) for index in indexes),
            max_characters=max_characters,
        )
