#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for merging aligned transcription sources into subtitles."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Prompt

__all__ = ["AlignedTranscriptionMergePrompt"]


@dataclass(frozen=True, slots=True, kw_only=True)
class AlignedTranscriptionMergePrompt(Prompt):
    """Text and aliases for aligned transcription merging."""

    max_subtitle_characters: int = 20
    """Maximum nonwhitespace characters permitted in one subtitle."""
    minimum_consensus_coverage: float = 0.9
    """Minimum answer-length coverage relative to strict-majority ASR evidence."""
    sources: str = "sources"
    """Name of aligned transcription source rows field."""
    sources_desc: str = "Named equal-status ASR rows aligned by Unicode column."
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
    """Name of speaker and voice-activity row field."""
    speaker_desc: str = (
        "Column-aligned fullwidth speaker labels, unattributed-speech markers, and "
        "gap or timed-pause markers."
    )
    """Description of speaker and voice-activity row field."""
    subtitles: str = "subtitles"
    """Name of merged consensus subtitles field in answer."""
    subtitles_desc: str = (
        "Complete ordered consensus transcript divided into display subtitles."
    )
    """Description of merged consensus subtitles field in answer."""
    subtitle_index: str = "index"
    """Name of consensus subtitle index field."""
    subtitle_index_desc: str = "One-based consensus subtitle index."
    """Description of consensus subtitle index field."""
    subtitle_text: str = "text"
    """Name of consensus subtitle text field."""
    subtitle_text_desc: str = (
        "Complete punctuated consensus subtitle text without alignment annotations."
    )
    """Description of consensus subtitle text field."""

    source_name_err: str = (
        "ASR source names must be nonblank and unique within the query."
    )
    """Error when source names are blank or duplicated."""
    reference_source_err: str = (
        "Aligned transcription merge queries may contain ASR sources only, not a "
        "reference or guide."
    )
    """Error when a reference-like source is included."""
    row_length_err: str = (
        "All ASR and speaker rows in a query must have equal nonzero lengths."
    )
    """Error when aligned row lengths differ."""
    reference_marker_err: str = (
        "Aligned transcription merge queries must not contain reference boundary "
        "markers."
    )
    """Error when an aligned row contains a reference boundary marker."""
    speaker_character_err: str = (
        "Speaker rows may contain only fullwidth speaker labels, fullwidth asterisks, "
        "fullwidth gaps, and fullwidth timed-pause markers."
    )
    """Error when a speaker row contains an unknown annotation."""
    transcript_empty_err: str = (
        "Aligned transcription merge queries must contain transcribed text."
    )
    """Error when every ASR row contains only gaps."""
    subtitle_indices_err: str = (
        "Answer subtitle indexes must be consecutive, ordered, and begin at 1."
    )
    """Error when answer subtitle indexes are invalid."""
    subtitle_text_err: str = "Every answer subtitle must contain nonblank text."
    """Error when an answer subtitle is blank."""
    subtitle_annotation_err: str = (
        "Answer subtitles must not contain alignment or speaker annotation characters."
    )
    """Error when answer text contains an alignment annotation."""
    subtitle_length_err_tpl: str = (
        "Answer subtitle indexes {indexes} exceed the maximum of "
        "{max_characters} nonwhitespace characters."
    )
    """Error template when answer subtitles exceed the configured maximum length."""
    consensus_coverage_err_tpl: str = (
        "The answer preserves only {coverage:.1%} of the high-confidence majority "
        "ASR character sequence; it must preserve at least {minimum:.1%}. The answer "
        "likely omitted consensus speech. Re-read every aligned column and return the "
        "complete transcript."
    )
    """Error template when answer coverage suggests omitted consensus speech."""

    def consensus_coverage_err(self, coverage: float) -> str:
        """Get an error for insufficient exact-majority ASR character coverage.

        Arguments:
            coverage: proportion of the majority sequence preserved in the answer
        Returns:
            formatted error message
        """
        return self.consensus_coverage_err_tpl.format(
            coverage=coverage, minimum=self.minimum_consensus_coverage
        )

    def subtitle_length_err(self, indexes: list[int]) -> str:
        """Get an error for subtitles exceeding the configured maximum length.

        Arguments:
            indexes: one-based indexes of subtitles that are too long
        Returns:
            formatted error message
        """
        return self.subtitle_length_err_tpl.format(
            indexes=", ".join(str(index) for index in indexes),
            max_characters=self.max_subtitle_characters,
        )
