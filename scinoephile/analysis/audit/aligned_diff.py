#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit aligned subtitle differences and format them as Markdown."""

from __future__ import annotations

from enum import StrEnum
from html import escape

from scinoephile.analysis.diff import LineDiff, LineDiffKind, SeriesDiff
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.core.text import is_full_width_char

from .utils import (
    format_audit_report,
    get_selected_event_indexes,
)

__all__ = [
    "AlignedDiffAuditFilter",
    "audit_aligned_diff",
]


class AlignedDiffAuditFilter(StrEnum):
    """Row filters supported by an aligned subtitle diff audit."""

    all = "all"
    """Include both equal and differing aligned rows."""

    changes = "changes"
    """Include only differing aligned rows."""


def audit_aligned_diff(
    transcription: Series,
    reference: Series,
    guide: Series | None = None,
    *,
    original: Series | None = None,
    row_filter: AlignedDiffAuditFilter = AlignedDiffAuditFilter.changes,
    first_index: int | None = None,
    last_index: int | None = None,
    first_block: int | None = None,
    last_block: int | None = None,
    similarity_cutoff: float = 0.6,
) -> str:
    """Audit a transcription against a reference and optional guide.

    Arguments:
        transcription: transcribed subtitle series under audit
        reference: subtitle series used as a comparison point
        guide: optional guide series one-to-one aligned with the transcription
        original: optional original series displayed by timing overlap
        row_filter: aligned row filter
        first_index: first 1-indexed transcription subtitle number to include
        last_index: last 1-indexed transcription subtitle number to include
        first_block: first 1-indexed transcription block number to include
        last_block: last 1-indexed transcription block number to include
        similarity_cutoff: similarity cutoff for pairing replacement blocks
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if the range or guide alignment is invalid
    """
    # Validate and resolve the selected transcription range
    selected_transcription_idxs = get_selected_event_indexes(
        transcription,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
    )
    time_window = _get_time_window(transcription, selected_transcription_idxs)

    # Align the optional guide and build the character-level diff
    aligned_guide = _align_guide(transcription, guide)
    diff = SeriesDiff(
        transcription,
        reference,
        one_lbl="transcription",
        two_lbl="reference",
        similarity_cutoff=similarity_cutoff,
    )

    # Select aligned rows in the requested transcription range
    selected_messages: list[tuple[LineDiff, tuple[int, ...], tuple[int, ...]]] = []
    for message in diff.get_messages(include_equal=True):
        transcription_idxs, reference_idxs = diff.get_event_indices(message)
        if not _message_is_in_range(
            transcription_idxs,
            reference_idxs,
            reference,
            selected_transcription_idxs,
            time_window,
            range_applied=any(
                boundary is not None
                for boundary in (first_index, last_index, first_block, last_block)
            ),
        ):
            continue
        selected_messages.append((message, transcription_idxs, reference_idxs))

    # Count all selected rows before applying the display filter
    differing_rows = sum(
        message.kind is not LineDiffKind.EQUAL for message, _, _ in selected_messages
    )
    equal_rows = len(selected_messages) - differing_rows
    if row_filter is AlignedDiffAuditFilter.changes:
        selected_messages = [
            row for row in selected_messages if row[0].kind is not LineDiffKind.EQUAL
        ]

    # Format the report through the shared audit renderer
    original_status = "omitted"
    if original is not None:
        original_status = "included"
    guide_status = "omitted"
    if aligned_guide is not None:
        guide_status = "included"
    return format_audit_report(
        title="Aligned Subtitle Diff Audit",
        summary_items=(
            f"transcription subtitles: {len(transcription)}",
            f"reference subtitles: {len(reference)}",
            f"original: {original_status}",
            f"guide: {guide_status}",
            f"aligned rows in selected range: {differing_rows + equal_rows}",
            f"differing rows: {differing_rows}",
            f"equal rows: {equal_rows}",
            f"row filter: {row_filter.value}",
        ),
        columns=(
            ("Indexes", "right"),
            ("Alignment", "left"),
            ("Notes", "left"),
        ),
        rows=[
            _format_row(
                message,
                transcription_idxs,
                reference_idxs,
                transcription,
                reference,
                original,
                aligned_guide,
            )
            for message, transcription_idxs, reference_idxs in selected_messages
        ],
        first_index=first_index,
        last_index=last_index,
        index_track_name="transcription",
        first_block=first_block,
        last_block=last_block,
    )


def _align_guide(transcription: Series, guide: Series | None) -> Series | None:
    """Align a raw guide series to transcription events by exact timing.

    Arguments:
        transcription: transcription series
        guide: optional raw guide series
    Returns:
        guide aligned one-to-one with the transcription, or None
    Raises:
        ScinoephileError: if transcription or guide timings are duplicated or missing
    """
    if guide is None:
        return None

    guide_by_timing = {}
    for guide_index, subtitle in enumerate(guide.events, 1):
        timing = (subtitle.start, subtitle.end)
        if timing in guide_by_timing:
            raise ScinoephileError(
                f"Guide subtitles have duplicate timing at index {guide_index}: "
                f"{subtitle.start}-{subtitle.end} ms"
            )
        guide_by_timing[timing] = subtitle

    aligned_events = []
    matched_timings = set()
    for transcription_index, subtitle in enumerate(transcription.events, 1):
        timing = (subtitle.start, subtitle.end)
        if timing in matched_timings:
            raise ScinoephileError(
                "Transcription subtitles have duplicate timing at index "
                f"{transcription_index}: {subtitle.start}-{subtitle.end} ms"
            )
        matched_timings.add(timing)
        guide_subtitle = guide_by_timing.get(timing)
        if guide_subtitle is None:
            raise ScinoephileError(
                "Guide subtitle series has no exact timing match for transcription "
                f"index {transcription_index}: {subtitle.start}-{subtitle.end} ms"
            )
        aligned_events.append(guide_subtitle)
    return Series(events=aligned_events)


def _escape_preformatted(value: str) -> str:
    """Escape text for use in a preformatted Markdown table cell.

    Arguments:
        value: raw text
    Returns:
        HTML-escaped text
    """
    return escape(value, quote=False).replace("|", "&#124;")


def _format_event_indices(prefix: str, event_idxs: tuple[int, ...]) -> str:
    """Format event indices as compact 1-indexed ranges.

    Arguments:
        prefix: series label prefix
        event_idxs: zero-based event indices
    Returns:
        prefixed index ranges
    """
    if not event_idxs:
        return f"{prefix} —"

    ranges = []
    start = event_idxs[0]
    end = start
    for event_idx in event_idxs[1:]:
        if event_idx == end + 1:
            end = event_idx
            continue
        ranges.append((start, end))
        start = event_idx
        end = event_idx
    ranges.append((start, end))

    formatted_ranges = []
    for start, end in ranges:
        if start == end:
            formatted_ranges.append(str(start + 1))
        else:
            formatted_ranges.append(f"{start + 1}-{end + 1}")
    return f"{prefix} {', '.join(formatted_ranges)}"


def _format_original_text(
    original: Series,
    timing_track: Series,
    event_idxs: tuple[int, ...],
) -> str:
    """Join original text that overlaps the indexed events' time range.

    Arguments:
        original: original subtitle series
        timing_track: subtitle series providing the indexed event timings
        event_idxs: zero-based event indices
    Returns:
        joined original text
    """
    if not event_idxs:
        return ""

    start = min(timing_track[event_idx].start for event_idx in event_idxs)
    end = max(timing_track[event_idx].end for event_idx in event_idxs)
    texts = [
        line.strip()
        for subtitle in original
        if subtitle.start < end and subtitle.end > start
        for line in subtitle.text_with_newline.splitlines()
        if line.strip()
    ]
    return _join_track_texts(texts)


def _format_row(
    message: LineDiff,
    transcription_idxs: tuple[int, ...],
    reference_idxs: tuple[int, ...],
    transcription: Series,
    reference: Series,
    original: Series | None,
    guide: Series | None,
) -> tuple[str, str, str]:
    """Format one aligned diff as semantic table data.

    Arguments:
        message: aligned line diff message
        transcription_idxs: transcription event indices represented by the message
        reference_idxs: reference event indices represented by the message
        transcription: transcription series
        reference: reference series
        original: optional original series
        guide: optional guide series
    Returns:
        index, alignment, and notes cells
    """
    index_cell = "\n".join(
        (
            _format_event_indices("T", transcription_idxs),
            _format_event_indices("R", reference_idxs),
        )
    )
    transcription_text, reference_text = message.get_aligned_texts()
    aligned_lines = []
    if original is not None:
        original_timing_track = transcription
        original_event_idxs = transcription_idxs
        if not original_event_idxs:
            original_timing_track = reference
            original_event_idxs = reference_idxs
        original_text = _format_original_text(
            original,
            original_timing_track,
            original_event_idxs,
        )
        aligned_lines.append(f"O │ {_escape_preformatted(original_text)}")
    aligned_lines.extend(
        (
            f"T │ {_escape_preformatted(transcription_text)}",
            f"R │ {_escape_preformatted(reference_text)}",
        )
    )
    if guide is not None:
        guide_text = _format_track_text(guide, transcription_idxs)
        aligned_lines.append(f"G │ {_escape_preformatted(guide_text)}")
    aligned_text = "\n".join(aligned_lines)
    alignment_cell = f"<pre>{aligned_text}</pre>"
    return index_cell, alignment_cell, ""


def _format_track_text(track: Series, event_idxs: tuple[int, ...]) -> str:
    """Join ancillary track text corresponding to transcription event indices.

    Arguments:
        track: ancillary series aligned with the transcription
        event_idxs: zero-based transcription event indices
    Returns:
        joined track text
    """
    texts = []
    for event_idx in event_idxs:
        texts.extend(
            line.strip()
            for line in track.events[event_idx].text_with_newline.splitlines()
            if line.strip()
        )
    return _join_track_texts(texts)


def _get_time_window(
    transcription: Series,
    event_idxs: frozenset[int],
) -> tuple[int, int] | None:
    """Get the selected transcription events' combined time window.

    Arguments:
        transcription: transcription series
        event_idxs: selected zero-based event indices
    Returns:
        start and end milliseconds, or None when no events are selected
    """
    if not event_idxs:
        return None
    return (
        min(transcription[event_idx].start for event_idx in event_idxs),
        max(transcription[event_idx].end for event_idx in event_idxs),
    )


def _join_track_texts(texts: list[str]) -> str:
    """Join one track's text lines with display-width-aware spaces.

    Arguments:
        texts: nonempty text lines in time order
    Returns:
        joined track text
    """
    if not texts:
        return ""

    chunks = [texts[0]]
    for text in texts[1:]:
        previous_char = None
        if chunks[-1]:
            previous_char = chunks[-1][-1]
        next_char = None
        if text:
            next_char = text[0]
        if (
            previous_char is not None
            and is_full_width_char(previous_char)
            or next_char is not None
            and is_full_width_char(next_char)
        ):
            chunks.append("\u3000")
        else:
            chunks.append(" ")
        chunks.append(text)
    return "".join(chunks)


def _message_is_in_range(
    transcription_idxs: tuple[int, ...],
    reference_idxs: tuple[int, ...],
    reference: Series,
    selected_transcription_idxs: frozenset[int],
    time_window: tuple[int, int] | None,
    *,
    range_applied: bool,
) -> bool:
    """Check whether an aligned message belongs in the requested range.

    Arguments:
        transcription_idxs: transcription event indices in the message
        reference_idxs: reference event indices in the message
        reference: reference series
        selected_transcription_idxs: selected transcription event indices
        time_window: selected transcription time window
        range_applied: whether either range boundary was supplied
    Returns:
        whether the message belongs in the range
    """
    if not range_applied:
        return True
    if transcription_idxs:
        return any(idx in selected_transcription_idxs for idx in transcription_idxs)
    if time_window is None:
        return False

    window_start, window_end = time_window
    return any(
        reference[idx].start < window_end and reference[idx].end > window_start
        for idx in reference_idxs
    )
