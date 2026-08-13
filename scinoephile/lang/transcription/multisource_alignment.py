#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Prepare, render, and serialize timed multi-source ASR alignments."""

from __future__ import annotations

from collections.abc import Mapping
from collections.abc import Sequence as AbcSequence
from dataclasses import dataclass
from unicodedata import category

from scinoephile.analysis.alignment.timed_msa.aligner import Aligner
from scinoephile.analysis.alignment.timed_msa.alignment import Alignment
from scinoephile.analysis.alignment.timed_msa.models import Column, Sequence, Token
from scinoephile.analysis.transcription.artifact import (
    AlignmentBlock,
    AlignmentColumn,
    AlignmentRow,
    AlignmentSubtitle,
    TimingSource,
)
from scinoephile.audio.classification import (
    AudioEvent,
    AudioEventDetectionResult,
    LanguageIdentificationResult,
)
from scinoephile.audio.diarization.models import SpeakerDiarizationResult
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.vad.trace import VoiceActivityTrace
from scinoephile.core.subtitles.series import Series
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_text_converted

__all__ = [
    "TimedMultisourceAlignmentRows",
    "TimedMultisourceAlignmentSource",
    "get_timed_alignment_sequence",
    "get_timed_multisource_alignment_rows",
    "get_timed_reference_alignment_sequence",
    "get_transcription_alignment_block",
]

_ALIGNMENT_GAP_CHARACTER = "　"
"""Fullwidth ideographic space used for ordinary alignment gaps."""

_PAUSE_CHARACTER = "・"
"""Wide middle dot used for shared timed pauses."""

_VAD_SPEECH_CHARACTER = "＊"
"""Fullwidth marker for speech without an attributed speaker."""

_VAD_SPEECH_THRESHOLD = 0.9
"""Minimum VAD score rendered as unattributed speech."""


@dataclass(frozen=True, slots=True)
class TimedMultisourceAlignmentRows:
    """Rendered aligned ASR and annotation rows."""

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
    """One named rendered source row in an alignment."""

    name: str
    """Stable ASR source name."""
    text: str
    """Aligned display characters, fullwidth gaps, and timed pauses."""


def get_timed_alignment_sequence(
    name: str, segments: AbcSequence[TranscribedSegment], *, offset_seconds: float = 0.0
) -> Sequence:
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
    return Sequence(name=name, tokens=_get_timed_alignment_tokens(timed_texts))


def get_timed_multisource_alignment_rows(
    alignment: Alignment,
    *,
    audio_events: AudioEventDetectionResult | None = None,
    diarization: SpeakerDiarizationResult | None = None,
    language_identification: LanguageIdentificationResult | None = None,
    source_offset_seconds: float = 0.0,
    traditionalize: bool = False,
    voice_activity_trace: VoiceActivityTrace | None = None,
) -> TimedMultisourceAlignmentRows:
    """Render complete aligned source and annotation rows.

    Arguments:
        alignment: timed character alignment to render
        audio_events: optional FireRed speech, singing, and music timeline
        diarization: optional exclusive pyannote speaker timeline
        language_identification: optional FireRed spoken-language timeline
        source_offset_seconds: source time corresponding to alignment-local zero
        traditionalize: whether to render source characters in Traditional Chinese
        voice_activity_trace: optional pyannote voice-activity score trace
    Returns:
        structured complete aligned source and annotation rows
    """
    if source_offset_seconds < 0.0:
        raise ValueError("Alignment source offset must be non-negative.")
    if not alignment.columns:
        raise ValueError("Cannot render an empty timed alignment.")
    speaker_symbols = _get_speaker_symbols(diarization)
    language_symbols = _get_language_symbols(language_identification)
    language_legend = {
        symbol: language for language, symbol in language_symbols.items()
    }
    source_cells = tuple(
        _get_source_cells(alignment.columns, source_idx, traditionalize)
        for source_idx in range(len(alignment.source_names))
    )
    sources = tuple(
        TimedMultisourceAlignmentSource(
            name=source_name, text="".join(source_cells[source_idx])
        )
        for source_idx, source_name in enumerate(alignment.source_names)
    )
    speaker = "".join(
        _get_annotation_cell(
            column,
            diarization,
            speaker_symbols,
            source_offset_seconds,
            voice_activity_trace,
        )
        for column in alignment.columns
    )
    language_trace = None
    if language_identification is not None:
        language_trace = "".join(
            _get_language_cell(
                column, language_identification, source_offset_seconds, language_symbols
            )
            for column in alignment.columns
        )
    return TimedMultisourceAlignmentRows(
        sources=sources,
        speaker=speaker,
        language_trace=language_trace,
        language_legend=language_legend,
        singing_trace=_get_event_row(
            alignment.columns,
            audio_events,
            AudioEvent.SINGING,
            "唱",
            source_offset_seconds,
        ),
        music_trace=_get_event_row(
            alignment.columns,
            audio_events,
            AudioEvent.MUSIC,
            "樂",
            source_offset_seconds,
        ),
    )


def get_timed_reference_alignment_sequence(
    name: str, series: Series, *, offset_seconds: float = 0.0
) -> Sequence:
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
    return Sequence(name=name, tokens=_get_timed_alignment_tokens(timed_texts))


def get_transcription_alignment_block(
    alignment: Alignment,
    merged_segments: AbcSequence[TranscribedSegment],
    aligner: Aligner,
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
    pause_intervals_seconds: AbcSequence[tuple[float, float]] = (),
    source_errors: Mapping[str, str] | None = None,
    timing_sources: Mapping[int, TimingSource] | None = None,
    traditionalize: bool = False,
    voice_activity_trace: VoiceActivityTrace | None = None,
) -> AlignmentBlock:
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
        timing_sources: final segment IDs mapped to their speech-timing origins
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
    augmented = augmented.with_pauses(
        minimum_pause_seconds=0.25,
        pause_intervals_seconds=pause_intervals_seconds,
        pause_unit_seconds=0.25,
        source_names=alignment.source_names,
    )
    rendered = get_timed_multisource_alignment_rows(
        augmented,
        audio_events=audio_events,
        diarization=diarization,
        language_identification=language_identification,
        source_offset_seconds=offset_seconds,
        traditionalize=traditionalize,
        voice_activity_trace=voice_activity_trace,
    )
    rendered_rows = {source.name: source.text for source in rendered.sources}
    columns = []
    for column_idx, column in enumerate(augmented.columns, start=1):
        column_kind = "text"
        if column.is_pause:
            column_kind = "pause"
        columns.append(
            AlignmentColumn(
                index=column_idx,
                start_ms=round((column.start_seconds + offset_seconds) * 1000),
                end_ms=round((column.end_seconds + offset_seconds) * 1000),
                kind=column_kind,
            )
        )
    subtitles = tuple(
        _get_transcription_alignment_subtitle(
            segment,
            first_subtitle_index + segment_idx,
            (timing_sources or {}).get(segment.id, "source"),
        )
        for segment_idx, segment in enumerate(merged_segments)
    )
    return AlignmentBlock(
        index=block_index,
        core_start_ms=core_start_ms,
        core_end_ms=core_end_ms,
        buffered_start_ms=buffered_start_ms,
        buffered_end_ms=buffered_end_ms,
        columns=tuple(columns),
        rows=tuple(
            AlignmentRow(name=name, text=rendered_rows[name])
            for name in alignment.source_names
        ),
        speaker=rendered.speaker,
        language_trace=rendered.language_trace,
        language_legend=dict(rendered.language_legend),
        singing_trace=rendered.singing_trace,
        music_trace=rendered.music_trace,
        merged=rendered_rows[merged_sequence.name],
        subtitles=subtitles,
        source_errors=dict(source_errors or {}),
    )


def _get_annotation_cell(
    column: Column,
    diarization: SpeakerDiarizationResult | None,
    speaker_symbols: dict[str, str],
    source_offset_seconds: float,
    voice_activity_trace: VoiceActivityTrace | None,
) -> str:
    """Get one speaker/VAD display character for an alignment column.

    Arguments:
        column: alignment column to annotate
        diarization: optional complete-source speaker diarization
        speaker_symbols: diarization labels mapped to display characters
        source_offset_seconds: source time corresponding to alignment-local zero
        voice_activity_trace: optional complete-source VAD score trace
    Returns:
        speaker, speech, pause, marker, or gap display character
    """
    if column.is_marker:
        return _get_column_marker(column)
    if column.is_pause:
        return _PAUSE_CHARACTER
    start_seconds = column.start_seconds
    end_seconds = column.end_seconds
    if diarization is not None:
        speaker = diarization.get_exclusive_speaker(
            start_seconds + source_offset_seconds, end_seconds + source_offset_seconds
        )
        if speaker is not None:
            return speaker_symbols[speaker]
    if voice_activity_trace is not None:
        score = voice_activity_trace.get_mean_score(
            start_seconds + source_offset_seconds, end_seconds + source_offset_seconds
        )
        if score is not None and score >= _VAD_SPEECH_THRESHOLD:
            return _VAD_SPEECH_CHARACTER
    return _ALIGNMENT_GAP_CHARACTER


def _get_column_marker(column: Column) -> str:
    """Get one validated alignment marker character.

    Arguments:
        column: alignment column expected to contain a marker
    Returns:
        alignment marker character
    Raises:
        ValueError: if the column does not contain a marker
    """
    if column.marker is None:
        raise ValueError("Alignment column does not contain a marker.")
    return column.marker


def _get_event_row(
    columns: AbcSequence[Column],
    audio_events: AudioEventDetectionResult | None,
    event: AudioEvent,
    marker: str,
    offset_seconds: float,
) -> str | None:
    """Get one independent binary audio-event annotation row.

    Arguments:
        columns: alignment columns to annotate
        audio_events: optional complete-source audio-event timeline
        event: audio event to mark
        marker: display character used when the event is present
        offset_seconds: source time corresponding to alignment-local zero
    Returns:
        aligned event row, or None when event detection is unavailable
    """
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


def _get_language_cell(
    column: Column,
    language_identification: LanguageIdentificationResult,
    offset_seconds: float,
    language_symbols: Mapping[str, str],
) -> str:
    """Get one spoken-language display character for an alignment column.

    Arguments:
        column: alignment column to annotate
        language_identification: complete-source spoken-language timeline
        offset_seconds: source time corresponding to alignment-local zero
        language_symbols: language labels mapped to display characters
    Returns:
        language, pause, marker, or gap display character
    """
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


def _get_language_symbols(
    language_identification: LanguageIdentificationResult | None,
) -> dict[str, str]:
    """Assign stable one-column symbols to FireRed language labels.

    Arguments:
        language_identification: optional spoken-language timeline
    Returns:
        language labels mapped to display characters
    """
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


def _get_source_cells(
    columns: AbcSequence[Column], source_idx: int, traditionalize: bool
) -> tuple[str, ...]:
    """Get one source's display cells while preserving its alignment gaps.

    Arguments:
        columns: alignment columns to render
        source_idx: index of the source row to render
        traditionalize: whether to render text in Hong Kong Traditional Chinese
    Returns:
        one display cell per alignment column
    """
    tokens = tuple(column.tokens[source_idx] for column in columns)
    converted_characters = None
    if traditionalize:
        source_text = "".join(token.text for token in tokens if token is not None)
        converted_text = get_zho_text_converted(source_text, OpenCCConfig.s2hk)
        if len(converted_text) == len(source_text):
            converted_characters = iter(converted_text)

    cells = []
    for column, token in zip(columns, tokens, strict=True):
        if column.is_marker:
            cells.append(_get_column_marker(column))
        elif column.is_pause:
            cells.append(_PAUSE_CHARACTER)
        elif token is None:
            cells.append(_ALIGNMENT_GAP_CHARACTER)
        elif converted_characters is not None:
            cells.append(next(converted_characters))
        elif traditionalize:
            converted_character = get_zho_text_converted(token.text, OpenCCConfig.s2hk)
            if len(converted_character) == 1:
                cells.append(converted_character)
            else:
                cells.append(token.text)
        else:
            cells.append(token.text)
    return tuple(cells)


def _get_speaker_symbols(
    diarization: SpeakerDiarizationResult | None,
) -> dict[str, str]:
    """Assign concise symbols to diarization labels by first appearance.

    Arguments:
        diarization: optional complete-source speaker diarization
    Returns:
        diarization labels mapped to display characters
    """
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


def _get_timed_alignment_tokens(
    timed_texts: AbcSequence[tuple[str, float, float]],
) -> tuple[Token, ...]:
    """Split timed text units uniformly into lexical character tokens.

    Arguments:
        timed_texts: text units paired with start and end times
    Returns:
        timestamped lexical character tokens
    """
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
            tokens.append(Token(character, character_start, character_end))
    return tuple(tokens)


def _get_transcription_alignment_subtitle(
    segment: TranscribedSegment, index: int, timing_source: TimingSource
) -> AlignmentSubtitle:
    """Convert one final segment into a portable subtitle record.

    Arguments:
        segment: final segment with display timing and optional CTC words
        index: one-based global subtitle index
        timing_source: origin of the segment's speech interval
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
    speech_end_ms = max(speech_start_ms + 1, round(speech_end_seconds * 1000))
    return AlignmentSubtitle(
        index=index,
        text=segment.text,
        speech_start_ms=speech_start_ms,
        speech_end_ms=speech_end_ms,
        timing_source=timing_source,
        start_ms=min(start_ms, speech_start_ms),
        end_ms=max(end_ms, speech_end_ms),
        speaker=speaker,
    )


def _is_alignment_character(character: str) -> bool:
    """Check whether a source character should participate in lexical alignment.

    Arguments:
        character: source character to inspect
    Returns:
        whether the character is lexical rather than control or punctuation
    """
    return not category(character).startswith(("C", "P", "S", "Z"))
