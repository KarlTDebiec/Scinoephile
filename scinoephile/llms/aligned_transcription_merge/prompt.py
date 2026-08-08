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
    """Minimum sequence-aligned preservation of strict-majority ASR evidence."""
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
    language_trace: str = "language"
    """Name of spoken-language annotation row field."""
    language_trace_desc: str = (
        "Optional column-aligned fullwidth spoken-language labels and gaps."
    )
    """Description of spoken-language annotation row field."""
    singing_trace: str = "singing"
    """Name of singing annotation row field."""
    singing_trace_desc: str = (
        "Optional column-aligned singing labels, gaps, and timed pauses."
    )
    """Description of singing annotation row field."""
    music_trace: str = "music"
    """Name of music annotation row field."""
    music_trace_desc: str = (
        "Optional column-aligned music labels, gaps, and timed pauses."
    )
    """Description of music annotation row field."""
    answer_text: str = "text"
    """Name of merged consensus text field in answer."""
    answer_text_desc: str = (
        "Complete consensus transcript with a fullwidth vertical bar after every "
        "display subtitle, or an empty string when no speech has sufficient "
        "cross-source support."
    )
    """Description of merged consensus text field in answer."""

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
    language_character_err: str = (
        "Language rows may contain only defined fullwidth language labels, gaps, "
        "and timed-pause markers."
    )
    """Error when a language row contains an unknown annotation."""
    audio_event_character_err: str = (
        "Audio-event rows may contain only their defined fullwidth label, gaps, and "
        "timed-pause markers."
    )
    """Error when an audio-event row contains an unknown annotation."""
    transcript_empty_err: str = (
        "Aligned transcription merge queries must contain transcribed text."
    )
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
    consensus_coverage_err_tpl: str = (
        "The answer preserves only {coverage:.1%} of the sequence-aligned "
        "high-confidence majority ASR columns; it must preserve at least "
        "{minimum:.1%}. The answer likely omitted or replaced consensus speech. "
        "Re-read every aligned column and return the complete transcript in order."
    )
    """Error template when answer coverage suggests omitted consensus speech."""

    def consensus_coverage_err(self, coverage: float) -> str:
        """Get an error for insufficient sequence-aligned majority coverage.

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
