#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit portable multi-source transcription alignments as Markdown."""

from __future__ import annotations

import unicodedata
from collections import Counter
from collections.abc import Sequence

from scinoephile.analysis.character_error_rate import LineCER
from scinoephile.analysis.multisequence_alignment import (
    TimedAlignmentColumn,
    TimedAlignmentSequence,
    TimedAlignmentToken,
    TimedMultiSequenceAligner,
    TimedMultiSequenceAlignment,
    get_timed_alignment_with_markers,
    get_timed_alignment_with_pauses,
)
from scinoephile.analysis.transcription_alignment import (
    TranscriptionAlignmentArtifact,
    TranscriptionAlignmentBlock,
)
from scinoephile.analysis.transcription_timing import (
    evaluate_transcription_timing,
    get_reference_for_alignment,
)
from scinoephile.core.subtitles import Series

from .utils import validate_audit_range

__all__ = ["audit_transcription_alignment"]

_BOUNDARY_CHARACTER = "｜"
_GAP_CHARACTER = "　"
_PAUSE_CHARACTER = "・"


def audit_transcription_alignment(
    artifact: TranscriptionAlignmentArtifact,
    reference: Series | None = None,
    *,
    first_index: int | None = None,
    last_index: int | None = None,
    first_block: int | None = None,
    last_block: int | None = None,
    columns_per_chunk: int = 60,
) -> str:
    """Audit aligned ASR, speaker, merged, and optional reference evidence.

    Arguments:
        artifact: portable multi-source transcription alignment
        reference: optional independent reference used only for evaluation
        first_index: first one-based merged subtitle index to include
        last_index: last one-based merged subtitle index to include
        first_block: first one-based VAD block index to include
        last_block: last one-based VAD block index to include
        columns_per_chunk: alignment columns rendered in each stacked chunk
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if index and block ranges are mixed or invalid
        ValueError: if the display width is not positive
    """
    validate_audit_range(first_index, last_index, first_block, last_block)
    if columns_per_chunk <= 0:
        raise ValueError("Alignment audit columns per chunk must be positive.")
    blocks = _get_selected_blocks(
        artifact.blocks,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
    )

    lines = [
        "# Transcription Alignment Audit",
        "",
        "## Summary",
        "",
        f"- format: {artifact.format} v{artifact.version}",
        f"- language: {artifact.language.code}",
        f"- ASR sources: {len(artifact.sources)}",
        f"- selected VAD blocks: {len(blocks)}",
        f"- selected merged subtitles: {sum(len(block.subtitles) for block in blocks)}",
        f"- pause encoding: one {_PAUSE_CHARACTER} per {artifact.pause_unit_ms} ms",
        (
            "- merge request boundary: "
            f"{artifact.request_pause_columns} consecutive {_PAUSE_CHARACTER}"
        ),
    ]
    selected_artifact = artifact.model_copy(update={"blocks": tuple(blocks)})
    if reference is not None:
        lines.extend(_get_metric_summary(selected_artifact, reference))
        lines.extend(
            ("", "## Timing Comparisons", "")
            + tuple(_get_timing_comparison_lines(selected_artifact, reference))
        )

    lines.extend(("", "## Alignments", ""))
    aligner = TimedMultiSequenceAligner(_get_token_similarity)
    for block in blocks:
        lines.extend(
            (
                f"### Block {block.index}",
                "",
                (
                    f"Core {block.core_start_ms / 1000:.3f}–"
                    f"{block.core_end_ms / 1000:.3f} s; input "
                    f"{block.buffered_start_ms / 1000:.3f}–"
                    f"{block.buffered_end_ms / 1000:.3f} s."
                ),
            )
        )
        if block.source_errors:
            errors = "; ".join(
                f"{name}: {error}" for name, error in block.source_errors.items()
            )
            lines.extend(("", f"Source errors: {errors}"))
        lines.extend(("", *_get_merged_subtitle_lines(block)))
        block_reference = None
        if reference is not None:
            block_reference = get_reference_for_alignment(
                artifact.model_copy(update={"blocks": (block,)}), reference
            )
        rendered = _render_block(
            block,
            block_reference,
            aligner,
            pause_unit_ms=artifact.pause_unit_ms,
            columns_per_chunk=columns_per_chunk,
        )
        lines.extend(("", "```text", rendered, "```", ""))
    return "\n".join(lines).rstrip() + "\n"


def _get_merged_subtitle_lines(block: TranscriptionAlignmentBlock) -> list[str]:
    """Get a table of merged subtitle speech and display timing."""
    lines = [
        "| Index | CTC speech | SRT display | Speaker | Text |",
        "| ---: | :--- | :--- | :--- | :--- |",
    ]
    for subtitle in block.subtitles:
        text = subtitle.text.replace("|", "\\|").replace("\n", "<br>")
        lines.append(
            f"| {subtitle.index} | "
            f"{subtitle.speech_start_ms / 1000:.3f}–"
            f"{subtitle.speech_end_ms / 1000:.3f} s | "
            f"{subtitle.start_ms / 1000:.3f}–{subtitle.end_ms / 1000:.3f} s | "
            f"{subtitle.speaker or '—'} | {text} |"
        )
    return lines


def _get_timing_comparison_lines(
    artifact: TranscriptionAlignmentArtifact, reference: Series
) -> list[str]:
    """Get text-aligned candidate/reference timing comparisons."""
    timing = evaluate_transcription_timing(artifact, reference)
    lines = [
        "| Candidate | Reference | Candidate display | Reference display | IoU | "
        "Δ start | Δ end |",
        "| :--- | :--- | :--- | :--- | ---: | ---: | ---: |",
    ]
    lines.extend(
        (
            f"| {','.join(map(str, pair.candidate_indexes))} | "
            f"{','.join(map(str, pair.reference_indexes))} | "
            f"{pair.candidate_start_ms / 1000:.3f}–"
            f"{pair.candidate_end_ms / 1000:.3f} s | "
            f"{pair.reference_start_ms / 1000:.3f}–"
            f"{pair.reference_end_ms / 1000:.3f} s | "
            f"{pair.intersection_over_union:.1%} | "
            f"{pair.start_error_ms:+d} ms | {pair.end_error_ms:+d} ms |"
        )
        for pair in timing.pairs
    )
    return lines


def _get_metric_summary(
    artifact: TranscriptionAlignmentArtifact, reference: Series
) -> list[str]:
    """Get CER and timing summary lines for selected blocks."""
    selected_reference = get_reference_for_alignment(artifact, reference)
    reference_text = "".join(
        subtitle.text_with_newline for subtitle in selected_reference
    )
    source_texts = {source.name: [] for source in artifact.sources}
    for block in artifact.blocks:
        rows = {row.name: row.text for row in block.rows}
        for source in artifact.sources:
            row = rows.get(source.name, "")
            source_texts[source.name].append(
                row.replace(_GAP_CHARACTER, "").replace(_PAUSE_CHARACTER, "")
            )
    candidates = {name: "".join(parts) for name, parts in source_texts.items()}
    candidates["merged"] = "".join(
        subtitle.text for block in artifact.blocks for subtitle in block.subtitles
    )
    lines = [f"- reference subtitles: {len(selected_reference)}"]
    for name, candidate_text in candidates.items():
        result = LineCER(reference_text, candidate_text)
        lines.append(f"- {name} CER: {result.cer:.3%}")
    timing = evaluate_transcription_timing(artifact, reference)
    group_counts = Counter(
        f"{len(pair.candidate_indexes)}:{len(pair.reference_indexes)}"
        for pair in timing.pairs
    )
    lines.extend(
        (
            f"- text-aligned timing groups: {len(timing.pairs)}",
            (
                "- candidate:reference subtitle groups: "
                + ", ".join(
                    f"{shape} × {count}"
                    for shape, count in sorted(group_counts.items())
                )
            ),
            f"- temporal micro IoU: {timing.micro_intersection_over_union:.3%}",
            (
                "- one-to-one temporal micro IoU: "
                f"{timing.one_to_one_micro_intersection_over_union:.3%} "
                f"({len(timing.one_to_one_pairs)} groups)"
            ),
            f"- mean reference-time coverage: {timing.mean_reference_coverage:.3%}",
            (
                "- mean signed start/end error: "
                f"{timing.mean_start_error_ms:.0f}/"
                f"{timing.mean_end_error_ms:.0f} ms"
            ),
            (
                "- mean absolute start/end error: "
                f"{timing.mean_absolute_start_error_ms:.0f}/"
                f"{timing.mean_absolute_end_error_ms:.0f} ms"
            ),
            (
                "- unmatched candidate/reference subtitles: "
                f"{timing.unmatched_candidate_subtitles}/"
                f"{timing.unmatched_reference_subtitles}"
            ),
        )
    )
    return lines


def _get_pause_intervals(
    block: TranscriptionAlignmentBlock,
) -> tuple[tuple[float, float], ...]:
    """Combine consecutive artifact pause columns into intervals."""
    intervals = []
    start_ms = None
    end_ms = None
    for column in block.columns:
        if column.kind == "pause":
            if start_ms is None:
                start_ms = column.start_ms
            end_ms = column.end_ms
            continue
        if start_ms is not None and end_ms is not None:
            intervals.append((start_ms / 1000, end_ms / 1000))
        start_ms = None
        end_ms = None
    if start_ms is not None and end_ms is not None:
        intervals.append((start_ms / 1000, end_ms / 1000))
    return tuple(intervals)


def _get_selected_blocks(
    blocks: Sequence[TranscriptionAlignmentBlock],
    *,
    first_index: int | None,
    last_index: int | None,
    first_block: int | None,
    last_block: int | None,
) -> list[TranscriptionAlignmentBlock]:
    """Select artifact blocks by their original block or subtitle indexes."""
    selected = []
    for block in blocks:
        if first_block is not None and block.index < first_block:
            continue
        if last_block is not None and block.index > last_block:
            continue
        if first_index is not None or last_index is not None:
            subtitle_indexes = tuple(subtitle.index for subtitle in block.subtitles)
            if not subtitle_indexes:
                continue
            if first_index is not None and max(subtitle_indexes) < first_index:
                continue
            if last_index is not None and min(subtitle_indexes) > last_index:
                continue
        selected.append(block)
    return selected


def _render_block(
    block: TranscriptionAlignmentBlock,
    reference: Series | None,
    aligner: TimedMultiSequenceAligner,
    *,
    pause_unit_ms: int,
    columns_per_chunk: int,
) -> str:
    """Reconstruct and render one artifact block with optional reference."""
    artifact_rows = (*block.rows,)
    row_names = tuple(row.name for row in artifact_rows) + ("merged",)
    row_texts = tuple(row.text for row in artifact_rows) + (block.merged,)
    lexical_columns = []
    speaker_by_token_id = {}
    for column_idx, column in enumerate(block.columns):
        if column.kind == "pause":
            continue
        tokens = []
        for row_text in row_texts:
            character = row_text[column_idx]
            token = None
            if character != _GAP_CHARACTER:
                token = TimedAlignmentToken(
                    character, column.start_ms / 1000, column.end_ms / 1000
                )
                speaker_by_token_id[id(token)] = block.speaker[column_idx]
            tokens.append(token)
        lexical_columns.append(TimedAlignmentColumn(tuple(tokens)))
    alignment = TimedMultiSequenceAlignment(
        source_names=row_names, columns=tuple(lexical_columns)
    )

    if reference is not None and len(reference) > 0:
        reference_sequence = _get_reference_sequence(reference)
        alignment = aligner.add_sequence(alignment, reference_sequence)
        alignment = get_timed_alignment_with_markers(
            alignment,
            tuple((subtitle.end / 1000, _BOUNDARY_CHARACTER) for subtitle in reference),
            source_names=("reference",),
        )
    pause_intervals = _get_pause_intervals(block)
    if pause_intervals:
        alignment = get_timed_alignment_with_pauses(
            alignment,
            pause_intervals_seconds=pause_intervals,
            minimum_pause_seconds=pause_unit_ms / 1000,
            pause_unit_seconds=pause_unit_ms / 1000,
            source_names=("merged",),
        )

    label_width = max(len(name) for name in (*alignment.source_names, "speaker"))
    rendered_chunks = []
    for chunk_start in range(0, len(alignment.columns), columns_per_chunk):
        columns = alignment.columns[chunk_start : chunk_start + columns_per_chunk]
        if not columns:
            continue
        lines = [
            f"[{chunk_start + 1:04d}-{chunk_start + len(columns):04d}] "
            f"{min(column.start_seconds for column in columns):07.3f}-"
            f"{max(column.end_seconds for column in columns):07.3f}s"
        ]
        for source_idx, source_name in enumerate(alignment.source_names):
            cells = [_get_alignment_cell(column, source_idx) for column in columns]
            lines.append(
                f"{source_name:<{label_width}}  "
                + "".join(_get_display_cell(cell) for cell in cells)
            )
            if source_name == "merged":
                speaker_cells = [
                    _get_speaker_cell(column, speaker_by_token_id) for column in columns
                ]
                lines.append(
                    f"{'speaker':<{label_width}}  "
                    + "".join(_get_display_cell(cell) for cell in speaker_cells)
                )

        rendered_chunks.append("\n".join(lines))
    return "\n\n".join(rendered_chunks)


def _get_alignment_cell(column: TimedAlignmentColumn, source_idx: int) -> str:
    """Get one displayed cell from an augmented audit alignment."""
    if column.is_marker:
        assert column.marker is not None
        return column.marker
    if column.is_pause:
        return _PAUSE_CHARACTER
    token = column.tokens[source_idx]
    if token is None:
        return _GAP_CHARACTER
    return token.text


def _get_display_cell(character: str) -> str:
    """Pad a narrow character to the width of one CJK alignment cell."""
    if unicodedata.east_asian_width(character) in {"F", "W"}:
        return character
    return f"{character} "


def _get_speaker_cell(
    column: TimedAlignmentColumn, speaker_by_token_id: dict[int, str]
) -> str:
    """Project the stored speaker row through added reference columns."""
    if column.is_marker:
        assert column.marker is not None
        return column.marker
    if column.is_pause:
        return _PAUSE_CHARACTER
    for token in column.tokens:
        if token is not None and id(token) in speaker_by_token_id:
            return speaker_by_token_id[id(token)]
    return _GAP_CHARACTER


def _get_reference_sequence(reference: Series) -> TimedAlignmentSequence:
    """Convert reference subtitles into approximately timed lexical characters."""
    tokens = []
    for subtitle in reference:
        characters = [
            character
            for character in subtitle.text_with_newline
            if not unicodedata.category(character).startswith(("C", "P", "S", "Z"))
        ]
        if not characters:
            continue
        step_seconds = (subtitle.end - subtitle.start) / 1000 / len(characters)
        for character_idx, character in enumerate(characters):
            start_seconds = subtitle.start / 1000 + character_idx * step_seconds
            tokens.append(
                TimedAlignmentToken(
                    character, start_seconds, start_seconds + step_seconds
                )
            )
    return TimedAlignmentSequence("reference", tuple(tokens))


def _get_token_similarity(one: TimedAlignmentToken, two: TimedAlignmentToken) -> float:
    """Score audit-only reference alignment using text and overall timing."""
    lexical_score = -2.0
    if one.text == two.text:
        lexical_score = 6.0
    one_midpoint = (one.start_seconds + one.end_seconds) / 2
    two_midpoint = (two.start_seconds + two.end_seconds) / 2
    temporal_score = 2.0 * max(-1.0, 1.0 - abs(one_midpoint - two_midpoint))
    return lexical_score + temporal_score
