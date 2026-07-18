#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit aligned subtitle differences and format them as Markdown."""

from __future__ import annotations

from enum import StrEnum
from html import escape

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.core.text import is_full_width_char

from .diff import LineDiff, LineDiffKind, SeriesDiff

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
        similarity_cutoff: similarity cutoff for pairing replacement blocks
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if the range or guide alignment is invalid
    """
    _validate_range(first_index, last_index)
    aligned_guide = _align_guide(transcription, guide)

    diff = SeriesDiff(
        transcription,
        reference,
        one_lbl="transcription",
        two_lbl="reference",
        similarity_cutoff=similarity_cutoff,
    )
    selected_transcription_idxs = _get_selected_transcription_indices(
        transcription,
        first_index,
        last_index,
    )
    time_window = _get_time_window(transcription, selected_transcription_idxs)

    selected_messages: list[tuple[LineDiff, tuple[int, ...], tuple[int, ...]]] = []
    for message in diff.get_messages(include_equal=True):
        transcription_idxs, reference_idxs = diff.get_event_indices(message)
        if not _message_is_in_range(
            transcription_idxs,
            reference_idxs,
            reference,
            selected_transcription_idxs,
            time_window,
            range_applied=first_index is not None or last_index is not None,
        ):
            continue
        selected_messages.append((message, transcription_idxs, reference_idxs))

    differing_rows = sum(
        message.kind is not LineDiffKind.EQUAL for message, _, _ in selected_messages
    )
    equal_rows = len(selected_messages) - differing_rows
    if row_filter is AlignedDiffAuditFilter.changes:
        selected_messages = [
            row for row in selected_messages if row[0].kind is not LineDiffKind.EQUAL
        ]

    lines = [
        "# Aligned Subtitle Diff Audit",
        "",
        "## Summary",
        "",
        f"- transcription subtitles: {len(transcription)}",
        f"- reference subtitles: {len(reference)}",
        f"- original: {'included' if original is not None else 'omitted'}",
        f"- guide: {'included' if aligned_guide is not None else 'omitted'}",
        f"- aligned rows in selected range: {differing_rows + equal_rows}",
        f"- differing rows: {differing_rows}",
        f"- equal rows: {equal_rows}",
        f"- row filter: {row_filter.value}",
    ]
    range_summary = _format_transcription_range(first_index, last_index)
    if range_summary is not None:
        lines.append(range_summary)
    lines.extend(
        (
            f"- table rows: {len(selected_messages)}",
            "",
            "## Audit Table",
            "",
            "| Indexes | Alignment | Notes |",
            "|---|---|---|",
        )
    )
    for message, transcription_idxs, reference_idxs in selected_messages:
        lines.append(
            _format_row(
                message,
                transcription_idxs,
                reference_idxs,
                transcription,
                original,
                aligned_guide,
            )
        )
    return "\n".join(lines) + "\n"


def _align_guide(transcription: Series, guide: Series | None) -> Series | None:
    """Align a raw guide series to transcription events by exact timing.

    Arguments:
        transcription: transcription series
        guide: optional raw guide series
    Returns:
        guide aligned one-to-one with the transcription, or None
    Raises:
        ScinoephileError: if guide timings are duplicated or missing
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
    for transcription_index, subtitle in enumerate(transcription.events, 1):
        timing = (subtitle.start, subtitle.end)
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
    transcription: Series,
    event_idxs: tuple[int, ...],
) -> str:
    """Join original text that overlaps the transcription events' time range.

    Arguments:
        original: original subtitle series
        transcription: transcription series
        event_idxs: zero-based transcription event indices
    Returns:
        joined original text
    """
    if not event_idxs:
        return ""

    start = min(transcription[event_idx].start for event_idx in event_idxs)
    end = max(transcription[event_idx].end for event_idx in event_idxs)
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
    original: Series | None,
    guide: Series | None,
) -> str:
    """Format one Markdown audit table row.

    Arguments:
        message: aligned line diff message
        transcription_idxs: transcription event indices represented by the message
        reference_idxs: reference event indices represented by the message
        transcription: transcription series
        original: optional original series
        guide: optional guide series
    Returns:
        Markdown table row
    """
    index_cell = "<br>".join(
        (
            _format_event_indices("T", transcription_idxs),
            _format_event_indices("R", reference_idxs),
        )
    )
    transcription_text, reference_text = message.get_aligned_texts()
    aligned_lines = []
    if original is not None:
        original_text = _format_original_text(
            original,
            transcription,
            transcription_idxs,
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
    alignment_cell = f"<pre>{'<br>'.join(aligned_lines)}</pre>"
    return f"| {index_cell} | {alignment_cell} |  |"


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


def _format_transcription_range(
    first_index: int | None,
    last_index: int | None,
) -> str | None:
    """Format an optional transcription range for the report summary.

    Arguments:
        first_index: first included 1-indexed transcription subtitle number
        last_index: last included 1-indexed transcription subtitle number
    Returns:
        formatted range summary, or None if the range is unbounded
    """
    if first_index is None and last_index is None:
        return None
    if first_index is None:
        return f"- transcription subtitle range: through {last_index}"
    if last_index is None:
        return f"- transcription subtitle range: {first_index} onward"
    return f"- transcription subtitle range: {first_index} through {last_index}"


def _get_selected_transcription_indices(
    transcription: Series,
    first_index: int | None,
    last_index: int | None,
) -> frozenset[int]:
    """Get selected zero-based transcription event indices.

    Arguments:
        transcription: transcription series
        first_index: first included 1-indexed subtitle number
        last_index: last included 1-indexed subtitle number
    Returns:
        selected zero-based event indices
    """
    start = 0
    if first_index is not None:
        start = first_index - 1
    stop = len(transcription)
    if last_index is not None:
        stop = min(last_index, stop)
    return frozenset(range(start, stop))


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
        previous_char = chunks[-1][-1] if chunks[-1] else None
        next_char = text[0] if text else None
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


def _validate_range(first_index: int | None, last_index: int | None):
    """Validate optional 1-indexed range boundaries.

    Arguments:
        first_index: first included subtitle number
        last_index: last included subtitle number
    Raises:
        ScinoephileError: if either boundary is invalid
    """
    if first_index is not None and first_index < 1:
        raise ScinoephileError("First index must be at least 1")
    if last_index is not None and last_index < 1:
        raise ScinoephileError("Last index must be at least 1")
    if first_index is not None and last_index is not None and first_index > last_index:
        raise ScinoephileError("First index must be less than or equal to last index")
