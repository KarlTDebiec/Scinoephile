#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Build portable multi-source transcription alignment artifacts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from math import isfinite

from scinoephile.analysis.alignment.timed_msa import MsaAligner, MsaAlignment, MsaColumn
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
from scinoephile.audio.transcription.alignment_sequence import (
    get_transcription_sequence,
)
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.vad.speech_block import SpeechBlock
from scinoephile.audio.vad.trace import VoiceActivityTrace
from scinoephile.core.script import OpenCCConfig
from scinoephile.lang.zho.script.conversion import get_zho_text_converted

__all__ = [
    "RenderedTranscriptionAlignment",
    "build_transcription_alignment_block",
    "render_transcription_alignment",
]

_VAD_SPEECH_THRESHOLD = 0.9
"""Minimum VAD score rendered as unattributed speech."""


@dataclass(frozen=True, slots=True)
class RenderedTranscriptionAlignment:
    """Column-aligned ASR and audio-analysis rows."""

    rows: tuple[AlignmentRow, ...]
    """Named ASR rows in alignment source order."""
    speaker: str
    """Speaker and unattributed-speech annotation row."""
    language: str | None
    """Spoken-language annotation row, when available."""
    language_legend: Mapping[str, str]
    """Language-row display characters mapped to language labels."""
    singing: str | None
    """Singing annotation row, when available."""
    music: str | None
    """Music annotation row, when available."""


def build_transcription_alignment_block(
    alignment: MsaAlignment,
    merged_segments: Sequence[TranscribedSegment],
    aligner: MsaAligner,
    *,
    speech_block: SpeechBlock,
    audio_events: AudioEventDetectionResult | None = None,
    diarization: SpeakerDiarizationResult | None = None,
    first_subtitle_index: int = 1,
    language_identification: LanguageIdentificationResult | None = None,
    pause_intervals_seconds: Sequence[tuple[float, float]] = (),
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
        speech_block: VAD-derived core and buffered source intervals
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
    Raises:
        ValueError: if a value is invalid
    """
    if not merged_segments:
        raise ValueError("Alignment blocks require merged subtitle segments.")
    if not alignment.columns:
        raise ValueError("Alignment blocks require lexical source columns.")
    if any(column.is_pause or column.is_marker for column in alignment.columns):
        raise ValueError("Portable block construction requires lexical alignment.")

    offset_seconds = speech_block.buffered_start_ms / 1000
    merged_name = "merged"
    while merged_name in alignment.source_names:
        merged_name = f"_{merged_name}"
    merged_sequence = get_transcription_sequence(
        merged_name, merged_segments, offset_seconds=offset_seconds
    )
    augmented = aligner.add_sequence(alignment, merged_sequence)
    augmented = augmented.with_pauses(
        pause_intervals_seconds=pause_intervals_seconds,
        source_names=alignment.source_names,
    )
    rendered = render_transcription_alignment(
        augmented,
        audio_events=audio_events,
        diarization=diarization,
        language_identification=language_identification,
        source_offset_seconds=offset_seconds,
        traditionalize=traditionalize,
        voice_activity_trace=voice_activity_trace,
    )
    speaker_symbols = _get_speaker_symbols(diarization)

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
    resolved_timing_sources = timing_sources or {}
    subtitles = tuple(
        _get_transcription_subtitle(
            segment,
            first_subtitle_index + segment_idx,
            resolved_timing_sources.get(segment.id, "source"),
            speaker_symbols,
        )
        for segment_idx, segment in enumerate(merged_segments)
    )
    return AlignmentBlock(
        index=speech_block.index + 1,
        core_start_ms=speech_block.start_ms,
        core_end_ms=speech_block.end_ms,
        buffered_start_ms=speech_block.buffered_start_ms,
        buffered_end_ms=speech_block.buffered_end_ms,
        columns=tuple(columns),
        rows=rendered.rows[:-1],
        speaker=rendered.speaker,
        language_trace=rendered.language,
        language_legend=rendered.language_legend,
        singing_trace=rendered.singing,
        music_trace=rendered.music,
        merged=rendered.rows[-1].text,
        subtitles=subtitles,
        source_errors=dict(source_errors or {}),
    )


def render_transcription_alignment(
    alignment: MsaAlignment,
    *,
    audio_events: AudioEventDetectionResult | None = None,
    diarization: SpeakerDiarizationResult | None = None,
    language_identification: LanguageIdentificationResult | None = None,
    source_offset_seconds: float = 0.0,
    traditionalize: bool = False,
    voice_activity_trace: VoiceActivityTrace | None = None,
) -> RenderedTranscriptionAlignment:
    """Render aligned ASR and audio-analysis rows.

    Arguments:
        alignment: timed lexical and pause alignment to render
        audio_events: optional complete-source FireRed audio-event timeline
        diarization: optional complete-source speaker diarization
        language_identification: optional complete-source FireRed language timeline
        source_offset_seconds: source time corresponding to alignment-local zero
        traditionalize: whether to render lexical rows in Hong Kong Traditional
        voice_activity_trace: optional complete-source VAD score trace
    Returns:
        equal-width ASR and annotation rows
    """
    rows = tuple(
        AlignmentRow(
            name=source_name,
            text=_get_row_text(alignment.columns, source_idx, traditionalize),
        )
        for source_idx, source_name in enumerate(alignment.source_names)
    )
    speaker_symbols = _get_speaker_symbols(diarization)
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
    language_symbols = _get_language_symbols(language_identification)
    language = None
    if language_identification is not None:
        language = "".join(
            _get_language_cell(
                column, language_identification, source_offset_seconds, language_symbols
            )
            for column in alignment.columns
        )
    return RenderedTranscriptionAlignment(
        rows=rows,
        speaker=speaker,
        language=language,
        language_legend={
            symbol: language for language, symbol in language_symbols.items()
        },
        singing=_get_event_row(
            alignment.columns,
            audio_events,
            AudioEvent.SINGING,
            "唱",
            source_offset_seconds,
        ),
        music=_get_event_row(
            alignment.columns,
            audio_events,
            AudioEvent.MUSIC,
            "樂",
            source_offset_seconds,
        ),
    )


def _get_annotation_cell(
    column: MsaColumn,
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
        speaker, speech, pause, or gap display character
    """
    if column.is_pause:
        return "・"
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
            return "＊"
    return "　"


def _get_event_row(
    columns: Sequence[MsaColumn],
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
        if column.is_pause:
            cells.append("・")
        elif audio_events.has_event(
            event,
            column.start_seconds + offset_seconds,
            column.end_seconds + offset_seconds,
        ):
            cells.append(marker)
        else:
            cells.append("　")
    return "".join(cells)


def _get_language_cell(
    column: MsaColumn,
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
        language, pause, or gap display character
    """
    if column.is_pause:
        return "・"
    language = language_identification.get_language(
        column.start_seconds + offset_seconds, column.end_seconds + offset_seconds
    )
    if language is None:
        return "　"
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


def _get_row_text(
    columns: Sequence[MsaColumn], source_idx: int, traditionalize: bool
) -> str:
    """Get one source's display text while preserving its alignment gaps.

    Arguments:
        columns: alignment columns to render
        source_idx: index of the source row to render
        traditionalize: whether to render text in Hong Kong Traditional Chinese
    Returns:
        one display character per alignment column
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
        if column.is_pause:
            cells.append("・")
        elif token is None:
            cells.append("　")
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
    return "".join(cells)


def _get_speaker_symbols(
    diarization: SpeakerDiarizationResult | None,
) -> dict[str, str]:
    """Assign concise symbols to diarization labels by first appearance.

    Arguments:
        diarization: optional complete-source speaker diarization
    Returns:
        diarization labels mapped to display characters
    Raises:
        ValueError: if a value is invalid
    """
    if diarization is None:
        return {}
    symbols = {}
    for turn in diarization.exclusive_turns:
        if turn.speaker in symbols:
            continue
        speaker_idx = len(symbols)
        if speaker_idx >= 26:
            raise ValueError("Alignment artifacts support at most 26 speakers.")
        symbols[turn.speaker] = chr(ord("Ａ") + speaker_idx)
    return symbols


def _get_transcription_subtitle(
    segment: TranscribedSegment,
    index: int,
    timing_source: TimingSource,
    speaker_symbols: Mapping[str, str],
) -> AlignmentSubtitle:
    """Convert one final segment into a portable subtitle record.

    Arguments:
        segment: final segment with display timing and optional CTC words
        index: one-based global subtitle index
        timing_source: origin of the segment's speech interval
        speaker_symbols: diarization labels mapped to artifact speaker symbols
    Returns:
        portable subtitle retaining separate speech and display intervals
    Raises:
        ValueError: if a value is invalid
    """
    if not isfinite(segment.start) or not isfinite(segment.end):
        raise ValueError("Merged subtitle display timing must be finite.")
    if segment.start < 0.0 or segment.end <= segment.start:
        raise ValueError("Merged subtitle display timing must be positive.")

    speech_start_seconds = segment.start
    speech_end_seconds = segment.end
    speakers = set()
    if segment.words:
        previous_start_seconds = -1.0
        for word in segment.words:
            if not isfinite(word.start) or not isfinite(word.end):
                raise ValueError("Merged subtitle word timing must be finite.")
            if word.start < 0.0 or word.end <= word.start:
                raise ValueError("Merged subtitle word timing must be positive.")
            if word.start < previous_start_seconds:
                raise ValueError(
                    "Merged subtitle words must be chronologically ordered."
                )
            previous_start_seconds = word.start
        speech_start_seconds = segment.words[0].start
        speech_end_seconds = segment.words[-1].end
        speakers = {word.speaker for word in segment.words if word.speaker is not None}
    speaker = None
    if len(speakers) == 1:
        speaker = speaker_symbols.get(next(iter(speakers)))

    # Preserve positive durations that collapse during millisecond rounding
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
