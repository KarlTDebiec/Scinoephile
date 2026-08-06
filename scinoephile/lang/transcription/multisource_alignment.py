#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Cantonese-aware preparation and display of timed ASR alignments."""

from __future__ import annotations

import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import cache

import pycantonese

from scinoephile.analysis.multisequence_alignment import (
    TimedAlignmentColumn,
    TimedAlignmentSequence,
    TimedAlignmentToken,
    TimedMultiSequenceAligner,
    TimedMultiSequenceAlignment,
    get_timed_alignment_with_pauses,
)
from scinoephile.analysis.transcription_alignment import (
    TranscriptionAlignmentBlock,
    TranscriptionAlignmentColumn,
    TranscriptionAlignmentRow,
    TranscriptionAlignmentSubtitle,
)
from scinoephile.audio.classification import (
    AudioEvent,
    AudioEventDetectionResult,
    LanguageIdentificationResult,
)
from scinoephile.audio.diarization.models import SpeakerDiarizationResult
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.voice_activity_trace import VoiceActivityTrace
from scinoephile.core.subtitles.series import Series
from scinoephile.lang.zho.script.conversion import (
    OpenCCConfig,
    get_zho_converter,
    get_zho_text_converted,
)

__all__ = [
    "CantoneseTimedTokenSimilarity",
    "TimedMultisourceAlignmentChunk",
    "TimedMultisourceAlignmentSource",
    "get_timed_alignment_sequence",
    "get_timed_multisource_alignment_chunks",
    "get_timed_reference_alignment_sequence",
    "get_timed_reference_boundary_markers",
    "get_timed_text_alignment_sequence",
    "get_transcription_alignment_block",
    "render_timed_multisource_alignment",
]

_CANTONESE_EQUIVALENCE_GROUPS = (
    frozenset({"不", "唔"}),
    frozenset({"他", "佢", "她", "它"}),
    frozenset({"了", "咗"}),
    frozenset({"在", "喺"}),
    frozenset({"是", "係", "系"}),
    frozenset({"的", "嘅"}),
    frozenset({"這", "呢"}),
)
"""Common Mandarinized and Cantonese ASR substitutions."""

_ALIGNMENT_GAP_CHARACTER = "　"
"""Fullwidth ideographic space used for ordinary alignment gaps."""

_PAUSE_CHARACTER = "・"
"""Wide middle dot used for shared timed pauses."""

_VAD_SPEECH_CHARACTER = "＊"
"""Fullwidth marker for speech without an attributed speaker."""

_REFERENCE_BOUNDARY_CHARACTER = "｜"
"""Fullwidth marker for a reference subtitle boundary."""


@dataclass(frozen=True, slots=True, kw_only=True)
class CantoneseTimedTokenSimilarity:
    """Protein-matrix-style score for timed Cantonese character substitutions."""

    exact_score: float = 6.0
    """Lexical score for identical characters."""
    script_variant_score: float = 5.5
    """Lexical score for Simplified/Traditional variants."""
    cantonese_equivalent_score: float = 5.0
    """Lexical score for known Cantonese/standard-Chinese equivalents."""
    same_jyutping_score: float = 4.0
    """Lexical score for identical Cantonese pronunciations including tone."""
    same_jyutping_base_score: float = 3.0
    """Lexical score for identical Cantonese syllables with differing tone."""
    substitution_score: float = -2.0
    """Lexical score for otherwise unrelated characters."""
    timing_weight: float = 2.0
    """Maximum magnitude of the temporal contribution."""
    timing_tolerance_seconds: float = 1.0
    """Midpoint distance over which positive temporal support decays to zero."""

    def __call__(self, one: TimedAlignmentToken, two: TimedAlignmentToken) -> float:
        """Score two timestamped characters.

        Arguments:
            one: first timestamped character
            two: second timestamped character
        Returns:
            combined lexical and temporal substitution score
        """
        lexical_score = self._get_lexical_score(one.text, two.text)
        one_midpoint = (one.start_seconds + one.end_seconds) / 2
        two_midpoint = (two.start_seconds + two.end_seconds) / 2
        midpoint_distance = abs(one_midpoint - two_midpoint)
        scaled_distance = midpoint_distance / self.timing_tolerance_seconds
        temporal_score = self.timing_weight * max(-1.0, 1.0 - scaled_distance)
        return lexical_score + temporal_score

    def __post_init__(self):
        """Validate score ordering and timing configuration."""
        lexical_scores = (
            self.exact_score,
            self.script_variant_score,
            self.cantonese_equivalent_score,
            self.same_jyutping_score,
            self.same_jyutping_base_score,
            self.substitution_score,
        )
        if any(
            left < right
            for left, right in zip(lexical_scores, lexical_scores[1:], strict=False)
        ):
            raise ValueError("Cantonese alignment lexical scores must be descending.")
        if self.timing_weight < 0.0:
            raise ValueError("Cantonese alignment timing weight must be non-negative.")
        if self.timing_tolerance_seconds <= 0.0:
            raise ValueError("Cantonese alignment timing tolerance must be positive.")

    def _get_lexical_score(self, one: str, two: str) -> float:
        """Get the substitution-matrix component for two characters."""
        if one == two:
            return self.exact_score
        one_features = _get_character_features(one)
        two_features = _get_character_features(two)
        if one_features.script_forms.intersection(two_features.script_forms):
            return self.script_variant_score
        if one_features.equivalence_groups.intersection(
            two_features.equivalence_groups
        ):
            return self.cantonese_equivalent_score
        if one_features.jyutping and one_features.jyutping == two_features.jyutping:
            return self.same_jyutping_score
        if (
            one_features.jyutping_base
            and one_features.jyutping_base == two_features.jyutping_base
        ):
            return self.same_jyutping_base_score
        return self.substitution_score


@dataclass(frozen=True, slots=True)
class TimedMultisourceAlignmentChunk:
    """One rendered chunk of aligned ASR and speaker evidence."""

    index: int
    """One-based chunk index."""
    start_seconds: float
    """Approximate chunk start on the complete source timeline."""
    end_seconds: float
    """Approximate chunk end on the complete source timeline."""
    sources: tuple[TimedMultisourceAlignmentSource, ...]
    """Named aligned ASR source rows."""
    speaker: str
    """Aligned speaker and voice-activity annotation row."""
    language_trace: str | None
    """Aligned spoken-language annotation row, when available."""
    language_legend: Mapping[str, str]
    """Language display characters mapped to FireRed language labels."""
    singing_trace: str | None
    """Aligned singing annotation row, when available."""
    music_trace: str | None
    """Aligned music annotation row, when available."""


@dataclass(frozen=True, slots=True)
class TimedMultisourceAlignmentSource:
    """One named rendered source row in an alignment chunk."""

    name: str
    """Stable ASR source name."""
    text: str
    """Aligned display characters, fullwidth gaps, and timed pauses."""


@dataclass(frozen=True, slots=True)
class _CharacterFeatures:
    """Cached comparison features for one source character."""

    equivalence_groups: frozenset[int]
    """Known Cantonese equivalence-group indexes."""
    jyutping: str
    """Context-free Cantonese reading with tone, when available."""
    jyutping_base: str
    """Context-free Cantonese reading without tone, when available."""
    script_forms: frozenset[str]
    """Original, Simplified, and Traditional character forms."""


def get_timed_alignment_sequence(
    name: str, segments: Sequence[TranscribedSegment], *, offset_seconds: float = 0.0
) -> TimedAlignmentSequence:
    """Convert timestamped transcription output into alignable characters.

    Whitespace, punctuation, symbols, and controls are omitted. Multi-character
    ASR timing units are divided uniformly so their characters retain monotonic
    approximate positions without claiming unavailable timing precision.

    Arguments:
        name: stable transcription source name
        segments: timestamped transcription segments
        offset_seconds: source time corresponding to alignment-local zero
    Returns:
        named sequence of timestamped lexical characters
    Raises:
        ValueError: if the source offset is negative or exceeds segment timings
    """
    if offset_seconds < 0.0:
        raise ValueError("Transcription alignment offset must be non-negative.")
    timed_texts = []
    for segment in segments:
        if segment.words:
            timed_texts.extend(
                (word.text, word.start - offset_seconds, word.end - offset_seconds)
                for word in segment.words
            )
        else:
            timed_texts.append(
                (
                    segment.text,
                    segment.start - offset_seconds,
                    segment.end - offset_seconds,
                )
            )
    if any(start_seconds < 0.0 for _, start_seconds, _ in timed_texts):
        raise ValueError("Transcription alignment offset exceeds segment timing.")
    return TimedAlignmentSequence(
        name=name, tokens=_get_timed_alignment_tokens(timed_texts)
    )


def get_timed_multisource_alignment_chunks(
    alignment: TimedMultiSequenceAlignment,
    *,
    alignment_offset_seconds: float = 0.0,
    columns_per_chunk: int = 60,
    audio_events: AudioEventDetectionResult | None = None,
    classification_offset_seconds: float = 0.0,
    diarization: SpeakerDiarizationResult | None = None,
    diarization_offset_seconds: float = 0.0,
    language_identification: LanguageIdentificationResult | None = None,
    traditionalize: bool = False,
    voice_activity_offset_seconds: float = 0.0,
    voice_activity_trace: VoiceActivityTrace | None = None,
    voice_activity_threshold: float = 0.9,
) -> tuple[TimedMultisourceAlignmentChunk, ...]:
    """Render aligned source and annotation rows into structured chunks.

    Arguments:
        alignment: timed character alignment to render
        alignment_offset_seconds: source time corresponding to alignment-local zero
        columns_per_chunk: alignment columns included in each chunk
        audio_events: optional FireRed speech, singing, and music timeline
        classification_offset_seconds: source offset for alignment-local times
        diarization: optional exclusive pyannote speaker timeline
        diarization_offset_seconds: source offset for alignment-local times
        language_identification: optional FireRed spoken-language timeline
        traditionalize: whether to render source characters in Traditional Chinese
        voice_activity_offset_seconds: source offset for alignment-local times
        voice_activity_trace: optional pyannote voice-activity score trace
        voice_activity_threshold: minimum score rendered as unattributed speech
    Returns:
        structured aligned source and speaker chunks
    """
    _validate_render_arguments(
        alignment_offset_seconds,
        columns_per_chunk,
        diarization_offset_seconds,
        voice_activity_offset_seconds,
        voice_activity_threshold,
    )
    speaker_symbols = _get_speaker_symbols(diarization)
    language_symbols = _get_language_symbols(language_identification)
    language_legend = {
        symbol: language for language, symbol in language_symbols.items()
    }
    source_cells = tuple(
        _get_source_cells(alignment.columns, source_idx, traditionalize)
        for source_idx in range(len(alignment.source_names))
    )
    chunks = []
    for chunk_start in range(0, len(alignment.columns), columns_per_chunk):
        columns = alignment.columns[chunk_start : chunk_start + columns_per_chunk]
        if not columns:
            continue
        sources = tuple(
            TimedMultisourceAlignmentSource(
                name=source_name,
                text="".join(
                    source_cells[source_idx][chunk_start : chunk_start + len(columns)]
                ),
            )
            for source_idx, source_name in enumerate(alignment.source_names)
        )
        speaker = "".join(
            _get_annotation_cell(
                column,
                diarization,
                diarization_offset_seconds,
                speaker_symbols,
                voice_activity_trace,
                voice_activity_offset_seconds,
                voice_activity_threshold,
            )
            for column in columns
        )
        language_trace = None
        if language_identification is not None:
            language_trace = "".join(
                _get_language_cell(
                    column,
                    language_identification,
                    classification_offset_seconds,
                    language_symbols,
                )
                for column in columns
            )
        singing_trace = _get_event_row(
            columns,
            audio_events,
            AudioEvent.SINGING,
            "唱",
            classification_offset_seconds,
        )
        music_trace = _get_event_row(
            columns, audio_events, AudioEvent.MUSIC, "樂", classification_offset_seconds
        )
        chunks.append(
            TimedMultisourceAlignmentChunk(
                index=len(chunks) + 1,
                start_seconds=(
                    min(column.start_seconds for column in columns)
                    + alignment_offset_seconds
                ),
                end_seconds=(
                    max(column.end_seconds for column in columns)
                    + alignment_offset_seconds
                ),
                sources=sources,
                speaker=speaker,
                language_trace=language_trace,
                language_legend=language_legend,
                singing_trace=singing_trace,
                music_trace=music_trace,
            )
        )
    return tuple(chunks)


def get_timed_reference_alignment_sequence(
    name: str, series: Series, *, offset_seconds: float = 0.0
) -> TimedAlignmentSequence:
    """Convert subtitle reference text into approximately timed characters.

    Arguments:
        name: stable reference row name
        series: reference subtitles on the complete source timeline
        offset_seconds: source time corresponding to alignment-local zero
    Returns:
        named reference sequence with alignment-local character timings
    Raises:
        ValueError: if the source offset is negative
    """
    if offset_seconds < 0.0:
        raise ValueError("Reference alignment offset must be non-negative.")
    timed_texts = [
        (
            subtitle.text_with_newline,
            max(0.0, subtitle.start / 1000 - offset_seconds),
            max(0.0, subtitle.end / 1000 - offset_seconds),
        )
        for subtitle in series
    ]
    return TimedAlignmentSequence(
        name=name, tokens=_get_timed_alignment_tokens(timed_texts)
    )


def get_timed_reference_boundary_markers(
    series: Series, *, offset_seconds: float = 0.0
) -> tuple[tuple[float, str], ...]:
    """Get a fullwidth marker at the end of each reference subtitle.

    Arguments:
        series: reference subtitles on the complete source timeline
        offset_seconds: source time corresponding to alignment-local zero
    Returns:
        ordered local marker times and fullwidth boundary characters
    Raises:
        ValueError: if the source offset is negative
    """
    if offset_seconds < 0.0:
        raise ValueError("Reference alignment offset must be non-negative.")
    return tuple(
        (max(0.0, subtitle.end / 1000 - offset_seconds), _REFERENCE_BOUNDARY_CHARACTER)
        for subtitle in series
    )


def get_timed_text_alignment_sequence(
    name: str, text: str, *, start_seconds: float, end_seconds: float
) -> TimedAlignmentSequence:
    """Convert untimed text into characters with uniformly estimated timings.

    Arguments:
        name: stable source name
        text: untimed source text
        start_seconds: estimated local start time
        end_seconds: estimated local end time
    Returns:
        named lexical-character sequence spanning the estimated interval
    Raises:
        ValueError: if the estimated interval is invalid
    """
    if start_seconds < 0.0:
        raise ValueError("Text alignment start must be non-negative.")
    if end_seconds <= start_seconds:
        raise ValueError("Text alignment interval must be nonempty.")
    return TimedAlignmentSequence(
        name=name,
        tokens=_get_timed_alignment_tokens(((text, start_seconds, end_seconds),)),
    )


def get_transcription_alignment_block(
    alignment: TimedMultiSequenceAlignment,
    merged_segments: Sequence[TranscribedSegment],
    aligner: TimedMultiSequenceAligner,
    *,
    block_index: int,
    buffered_end_ms: int,
    buffered_start_ms: int,
    core_end_ms: int,
    core_start_ms: int,
    audio_events: AudioEventDetectionResult | None = None,
    diarization: SpeakerDiarizationResult | None = None,
    first_subtitle_index: int = 1,
    language_identification: LanguageIdentificationResult | None = None,
    pause_intervals_seconds: Sequence[tuple[float, float]] = (),
    source_errors: Mapping[str, str] | None = None,
    traditionalize: bool = False,
    voice_activity_trace: VoiceActivityTrace | None = None,
) -> TranscriptionAlignmentBlock:
    """Build one portable production alignment block.

    The input alignment must contain only successful ASR rows and lexical
    columns. The final merged row is projected onto that fixed profile before
    shared pauses are inserted, preserving the source-to-source alignment.

    Arguments:
        alignment: lexical multi-ASR alignment using block-local times
        merged_segments: core-owned merged segments using complete-source times
        aligner: aligner used to project the merged row onto the ASR profile
        block_index: one-based index in the complete VAD block plan
        buffered_end_ms: exclusive end of the ASR input interval
        buffered_start_ms: inclusive start of the ASR input interval
        core_end_ms: exclusive end of the block-owned interval
        core_start_ms: inclusive start of the block-owned interval
        audio_events: optional complete-source FireRed audio-event timeline
        diarization: optional complete-source speaker diarization
        first_subtitle_index: one-based global index for the first merged subtitle
        language_identification: optional complete-source FireRed language timeline
        pause_intervals_seconds: block-local VAD silence intervals
        source_errors: failed source names and messages
        traditionalize: whether to render lexical rows in Hong Kong Traditional
        voice_activity_trace: optional complete-source VAD score trace
    Returns:
        validated portable alignment block
    """
    if not merged_segments:
        raise ValueError("Alignment blocks require merged subtitle segments.")
    if any(column.is_pause or column.is_marker for column in alignment.columns):
        raise ValueError("Portable block construction requires lexical alignment.")

    offset_seconds = buffered_start_ms / 1000
    merged_sequence = get_timed_alignment_sequence(
        "merged", merged_segments, offset_seconds=offset_seconds
    )
    augmented = aligner.add_sequence(alignment, merged_sequence)
    augmented = get_timed_alignment_with_pauses(
        augmented,
        minimum_pause_seconds=0.25,
        pause_intervals_seconds=pause_intervals_seconds,
        pause_unit_seconds=0.25,
        source_names=alignment.source_names,
    )
    chunks = get_timed_multisource_alignment_chunks(
        augmented,
        alignment_offset_seconds=offset_seconds,
        audio_events=audio_events,
        classification_offset_seconds=offset_seconds,
        columns_per_chunk=max(len(augmented.columns), 1),
        diarization=diarization,
        diarization_offset_seconds=offset_seconds,
        language_identification=language_identification,
        traditionalize=traditionalize,
        voice_activity_offset_seconds=offset_seconds,
        voice_activity_trace=voice_activity_trace,
    )
    if len(chunks) != 1:
        raise RuntimeError("Portable alignment block did not render as one chunk.")
    chunk = chunks[0]
    rendered_rows = {source.name: source.text for source in chunk.sources}
    columns = tuple(
        TranscriptionAlignmentColumn(
            index=column_idx,
            start_ms=round((column.start_seconds + offset_seconds) * 1000),
            end_ms=round((column.end_seconds + offset_seconds) * 1000),
            kind="pause" if column.is_pause else "text",
        )
        for column_idx, column in enumerate(augmented.columns, start=1)
    )
    subtitles = tuple(
        _get_transcription_alignment_subtitle(
            segment, first_subtitle_index + segment_idx
        )
        for segment_idx, segment in enumerate(merged_segments)
    )
    return TranscriptionAlignmentBlock(
        index=block_index,
        core_start_ms=core_start_ms,
        core_end_ms=core_end_ms,
        buffered_start_ms=buffered_start_ms,
        buffered_end_ms=buffered_end_ms,
        columns=columns,
        rows=tuple(
            TranscriptionAlignmentRow(name=name, text=rendered_rows[name])
            for name in alignment.source_names
        ),
        speaker=chunk.speaker,
        language_trace=chunk.language_trace,
        language_legend=dict(chunk.language_legend),
        singing_trace=chunk.singing_trace,
        music_trace=chunk.music_trace,
        merged=rendered_rows[merged_sequence.name],
        subtitles=subtitles,
        source_errors=dict(source_errors or {}),
    )


def render_timed_multisource_alignment(
    alignment: TimedMultiSequenceAlignment,
    *,
    alignment_offset_seconds: float = 0.0,
    columns_per_chunk: int = 60,
    diarization: SpeakerDiarizationResult | None = None,
    diarization_offset_seconds: float = 0.0,
    primary_source_names: Sequence[str] | None = None,
    traditionalize: bool = False,
    voice_activity_offset_seconds: float = 0.0,
    voice_activity_trace: VoiceActivityTrace | None = None,
    voice_activity_threshold: float = 0.9,
) -> str:
    """Render aligned ASR rows with a separate speaker/VAD annotation row.

    Each display cell occupies two terminal columns. CJK text, fullwidth gaps, and
    annotation markers use their natural width; other characters are padded.

    Arguments:
        alignment: timed character alignment to render
        alignment_offset_seconds: source time corresponding to alignment-local zero
        columns_per_chunk: alignment columns shown in each stacked chunk
        diarization: optional exclusive pyannote speaker timeline
        diarization_offset_seconds: source offset for alignment-local times
        primary_source_names: rows rendered above speaker/VAD annotations
        traditionalize: whether to render source characters in Traditional Chinese
        voice_activity_offset_seconds: source offset for alignment-local times
        voice_activity_trace: optional pyannote voice-activity score trace
        voice_activity_threshold: minimum score rendered as unattributed speech
    Returns:
        human-readable stacked alignment
    """
    _validate_render_arguments(
        alignment_offset_seconds,
        columns_per_chunk,
        diarization_offset_seconds,
        voice_activity_offset_seconds,
        voice_activity_threshold,
    )

    if primary_source_names is None:
        primary_source_names = alignment.source_names
    primary_source_names = tuple(primary_source_names)
    if len(set(primary_source_names)) != len(primary_source_names):
        raise ValueError("Primary alignment source names must be unique.")
    if not set(primary_source_names).issubset(alignment.source_names):
        raise ValueError("Primary alignment source name is not present.")
    primary_source_indexes = tuple(
        alignment.source_names.index(name) for name in primary_source_names
    )
    secondary_source_indexes = tuple(
        source_idx
        for source_idx in range(len(alignment.source_names))
        if source_idx not in primary_source_indexes
    )
    row_names = [
        *primary_source_names,
        *(alignment.source_names[idx] for idx in secondary_source_indexes),
    ]
    include_annotation = diarization is not None or voice_activity_trace is not None
    if include_annotation:
        row_names.append("speaker")
    label_width = max(len(name) for name in row_names)
    speaker_symbols = _get_speaker_symbols(diarization)
    source_cells = tuple(
        _get_source_cells(alignment.columns, source_idx, traditionalize)
        for source_idx in range(len(alignment.source_names))
    )
    chunks = []
    for chunk_start in range(0, len(alignment.columns), columns_per_chunk):
        chunk = alignment.columns[chunk_start : chunk_start + columns_per_chunk]
        if not chunk:
            continue
        chunk_start_seconds = min(column.start_seconds for column in chunk)
        chunk_end_seconds = max(column.end_seconds for column in chunk)
        lines = [
            f"[{chunk_start + 1:04d}-{chunk_start + len(chunk):04d}] "
            f"{chunk_start_seconds + alignment_offset_seconds:07.3f}-"
            f"{chunk_end_seconds + alignment_offset_seconds:07.3f}s"
        ]
        lines.extend(
            _get_rendered_source_line(
                alignment,
                source_cells,
                source_idx,
                chunk_start,
                len(chunk),
                label_width,
            )
            for source_idx in primary_source_indexes
        )
        if include_annotation:
            annotation_cells = [
                _get_annotation_cell(
                    column,
                    diarization,
                    diarization_offset_seconds,
                    speaker_symbols,
                    voice_activity_trace,
                    voice_activity_offset_seconds,
                    voice_activity_threshold,
                )
                for column in chunk
            ]
            lines.append(
                f"{'speaker':<{label_width}}  "
                + "".join(_get_display_cell(cell) for cell in annotation_cells)
            )
        lines.extend(
            _get_rendered_source_line(
                alignment,
                source_cells,
                source_idx,
                chunk_start,
                len(chunk),
                label_width,
            )
            for source_idx in secondary_source_indexes
        )
        chunks.append("\n".join(lines))
    legend = _get_alignment_legend(alignment, include_annotation)
    return f"{legend}\n\n" + "\n\n".join(chunks)


def _get_alignment_legend(
    alignment: TimedMultiSequenceAlignment, include_annotation: bool
) -> str:
    """Get the legend for the annotations present in an alignment."""
    legend = (
        f"Legend: 「{_ALIGNMENT_GAP_CHARACTER}」=alignment gap; "
        f"{_PAUSE_CHARACTER}=timed pause"
    )
    if any(column.is_marker for column in alignment.columns):
        legend += f"; {_REFERENCE_BOUNDARY_CHARACTER}=reference subtitle boundary"
    if include_annotation:
        legend += (
            "; Ａ／Ｂ／…=exclusive speaker; "
            f"{_VAD_SPEECH_CHARACTER}=speech without speaker; "
            f"「{_ALIGNMENT_GAP_CHARACTER}」=no speech"
        )
    return legend


def _get_annotation_cell(
    column: TimedAlignmentColumn,
    diarization: SpeakerDiarizationResult | None,
    diarization_offset_seconds: float,
    speaker_symbols: dict[str, str],
    voice_activity_trace: VoiceActivityTrace | None,
    voice_activity_offset_seconds: float,
    voice_activity_threshold: float,
) -> str:
    """Get one speaker/VAD display character for an alignment column."""
    if column.is_marker:
        assert column.marker is not None
        return column.marker
    if column.is_pause:
        return _PAUSE_CHARACTER
    start_seconds = column.start_seconds
    end_seconds = column.end_seconds
    if diarization is not None:
        speaker = diarization.get_exclusive_speaker(
            start_seconds + diarization_offset_seconds,
            end_seconds + diarization_offset_seconds,
        )
        if speaker is not None:
            return speaker_symbols[speaker]
    if voice_activity_trace is not None:
        score = voice_activity_trace.get_mean_score(
            start_seconds + voice_activity_offset_seconds,
            end_seconds + voice_activity_offset_seconds,
        )
        if score is not None and score >= voice_activity_threshold:
            return _VAD_SPEECH_CHARACTER
    return _ALIGNMENT_GAP_CHARACTER


def _get_language_cell(
    column: TimedAlignmentColumn,
    language_identification: LanguageIdentificationResult,
    offset_seconds: float,
    language_symbols: Mapping[str, str],
) -> str:
    """Get one spoken-language display character for an alignment column."""
    if column.is_marker:
        return _get_column_marker(column)
    if column.is_pause:
        return _PAUSE_CHARACTER
    language = language_identification.get_language(
        column.start_seconds + offset_seconds, column.end_seconds + offset_seconds
    )
    if language is None:
        return _ALIGNMENT_GAP_CHARACTER
    return language_symbols[language]


def _get_event_row(
    columns: Sequence[TimedAlignmentColumn],
    audio_events: AudioEventDetectionResult | None,
    event: AudioEvent,
    marker: str,
    offset_seconds: float,
) -> str | None:
    """Get one independent binary audio-event annotation row."""
    if audio_events is None:
        return None
    cells = []
    for column in columns:
        if column.is_marker:
            cells.append(_get_column_marker(column))
        elif column.is_pause:
            cells.append(_PAUSE_CHARACTER)
        elif audio_events.has_event(
            event,
            column.start_seconds + offset_seconds,
            column.end_seconds + offset_seconds,
        ):
            cells.append(marker)
        else:
            cells.append(_ALIGNMENT_GAP_CHARACTER)
    return "".join(cells)


@cache
def _get_character_features(character: str) -> _CharacterFeatures:
    """Get reusable script, equivalence, and pronunciation features."""
    script_forms = {
        character,
        get_zho_converter("s2t").convert(character),
        get_zho_converter("t2s").convert(character),
    }
    equivalence_groups = frozenset(
        group_idx
        for group_idx, group in enumerate(_CANTONESE_EQUIVALENCE_GROUPS)
        if character in group or script_forms.intersection(group)
    )
    traditional_character = get_zho_converter("s2t").convert(character)
    jyutping = ""
    if len(traditional_character) == 1:
        _, raw_jyutping = pycantonese.characters_to_jyutping([traditional_character])[0]
        if raw_jyutping is not None:
            jyutping = raw_jyutping
    jyutping_base = jyutping.rstrip("123456")
    return _CharacterFeatures(
        equivalence_groups=equivalence_groups,
        jyutping=jyutping,
        jyutping_base=jyutping_base,
        script_forms=frozenset(script_forms),
    )


def _get_display_cell(character: str) -> str:
    """Pad one character to a two-terminal-column display cell."""
    if unicodedata.east_asian_width(character) in {"F", "W"}:
        return character
    return f"{character} "


def _get_speaker_symbols(
    diarization: SpeakerDiarizationResult | None,
) -> dict[str, str]:
    """Assign concise symbols to diarization labels by first appearance."""
    if diarization is None:
        return {}
    symbols = {}
    for turn in diarization.exclusive_turns:
        if turn.speaker in symbols:
            continue
        speaker_idx = len(symbols)
        if speaker_idx < 26:
            symbols[turn.speaker] = chr(ord("Ａ") + speaker_idx)
        else:
            symbols[turn.speaker] = _VAD_SPEECH_CHARACTER
    return symbols


def _get_language_symbols(
    language_identification: LanguageIdentificationResult | None,
) -> dict[str, str]:
    """Assign stable one-column symbols to FireRed language labels."""
    if language_identification is None:
        return {}
    preferred_symbols = {
        "zh-yue": "粵",
        "zh-mandarin": "普",
        "en": "英",
        "ja": "日",
        "ko": "韓",
    }
    symbols = {}
    used_symbols = set()
    languages = dict.fromkeys(span.language for span in language_identification.spans)
    for language in languages:
        symbol = preferred_symbols.get(language)
        if symbol is not None:
            symbols[language] = symbol
            used_symbols.add(symbol)
    fallback_symbols = (
        chr(ord("Ａ") + index)
        for index in range(26)
        if chr(ord("Ａ") + index) not in used_symbols
    )
    for language in languages:
        if language not in symbols:
            symbols[language] = next(fallback_symbols, "外")
    return symbols


def _get_rendered_source_line(
    alignment: TimedMultiSequenceAlignment,
    source_cells: tuple[tuple[str, ...], ...],
    source_idx: int,
    chunk_start: int,
    chunk_length: int,
    label_width: int,
) -> str:
    """Render one source row for one alignment chunk."""
    source_name = alignment.source_names[source_idx]
    cells = source_cells[source_idx][chunk_start : chunk_start + chunk_length]
    return f"{source_name:<{label_width}}  " + "".join(
        _get_display_cell(cell) for cell in cells
    )


def _get_source_cells(
    columns: Sequence[TimedAlignmentColumn], source_idx: int, traditionalize: bool
) -> tuple[str, ...]:
    """Get one source's display cells while preserving its alignment gaps."""
    tokens = tuple(column.tokens[source_idx] for column in columns)
    if not traditionalize:
        return tuple(
            _get_column_marker(column)
            if column.is_marker
            else _PAUSE_CHARACTER
            if column.is_pause
            else _ALIGNMENT_GAP_CHARACTER
            if token is None
            else token.text
            for column, token in zip(columns, tokens, strict=True)
        )

    source_text = "".join(token.text for token in tokens if token is not None)
    converted_text = get_zho_text_converted(source_text, OpenCCConfig.s2hk)
    if len(converted_text) != len(source_text):
        return tuple(
            _get_column_marker(column)
            if column.is_marker
            else _PAUSE_CHARACTER
            if column.is_pause
            else _ALIGNMENT_GAP_CHARACTER
            if token is None
            else get_zho_text_converted(token.text, OpenCCConfig.s2hk)
            for column, token in zip(columns, tokens, strict=True)
        )

    converted_characters = iter(converted_text)
    return tuple(
        _get_column_marker(column)
        if column.is_marker
        else _PAUSE_CHARACTER
        if column.is_pause
        else _ALIGNMENT_GAP_CHARACTER
        if token is None
        else next(converted_characters)
        for column, token in zip(columns, tokens, strict=True)
    )


def _get_transcription_alignment_subtitle(
    segment: TranscribedSegment, index: int
) -> TranscriptionAlignmentSubtitle:
    """Convert one final segment into a portable subtitle record.

    Arguments:
        segment: final segment with display timing and optional CTC words
        index: one-based global subtitle index
    Returns:
        portable subtitle retaining separate speech and display intervals
    """
    speech_start_seconds = segment.start
    speech_end_seconds = segment.end
    speakers = set()
    if segment.words:
        speech_start_seconds = segment.words[0].start
        speech_end_seconds = segment.words[-1].end
        speakers = {word.speaker for word in segment.words if word.speaker is not None}
    speaker = None
    if len(speakers) == 1:
        speaker = next(iter(speakers))
    start_ms = round(segment.start * 1000)
    end_ms = max(start_ms + 1, round(segment.end * 1000))
    speech_start_ms = round(speech_start_seconds * 1000)
    speech_end_ms = max(speech_start_ms, round(speech_end_seconds * 1000))
    return TranscriptionAlignmentSubtitle(
        index=index,
        text=segment.text,
        speech_start_ms=speech_start_ms,
        speech_end_ms=speech_end_ms,
        start_ms=min(start_ms, speech_start_ms),
        end_ms=max(end_ms, speech_end_ms),
        speaker=speaker,
    )


def _get_column_marker(column: TimedAlignmentColumn) -> str:
    """Get one validated alignment marker character."""
    if column.marker is None:
        raise ValueError("Alignment column does not contain a marker.")
    return column.marker


def _get_timed_alignment_tokens(
    timed_texts: Sequence[tuple[str, float, float]],
) -> tuple[TimedAlignmentToken, ...]:
    """Split timed text units uniformly into lexical character tokens."""
    tokens = []
    for text, start_seconds, end_seconds in timed_texts:
        characters = [char for char in text if _is_alignment_character(char)]
        if not characters:
            continue
        duration_seconds = max(0.0, end_seconds - start_seconds)
        step_seconds = duration_seconds / len(characters)
        for character_idx, character in enumerate(characters):
            character_start = start_seconds + character_idx * step_seconds
            character_end = start_seconds + (character_idx + 1) * step_seconds
            tokens.append(
                TimedAlignmentToken(character, character_start, character_end)
            )
    return tuple(tokens)


def _validate_render_arguments(
    alignment_offset_seconds: float,
    columns_per_chunk: int,
    diarization_offset_seconds: float,
    voice_activity_offset_seconds: float,
    voice_activity_threshold: float,
):
    """Validate shared structured and text rendering arguments."""
    if not 0.0 <= voice_activity_threshold <= 1.0:
        raise ValueError("Voice activity threshold must be between zero and one.")
    if alignment_offset_seconds < 0.0:
        raise ValueError("Alignment offset must be non-negative.")
    if diarization_offset_seconds < 0.0:
        raise ValueError("Diarization offset must be non-negative.")
    if voice_activity_offset_seconds < 0.0:
        raise ValueError("Voice activity offset must be non-negative.")
    if columns_per_chunk <= 0:
        raise ValueError("Alignment columns per chunk must be positive.")


def _is_alignment_character(character: str) -> bool:
    """Whether a source character should participate in lexical alignment."""
    category = unicodedata.category(character)
    return not category.startswith(("C", "P", "S", "Z"))
