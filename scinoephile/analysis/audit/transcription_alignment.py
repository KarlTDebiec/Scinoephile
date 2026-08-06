#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit portable multi-source transcription alignments as Markdown."""

from __future__ import annotations

import unicodedata
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from statistics import median

from scinoephile.analysis.character_error_rate import LineCER
from scinoephile.analysis.multisequence_alignment import (
    TimedAlignmentColumn,
    TimedAlignmentSequence,
    TimedAlignmentToken,
    TimedMultiSequenceAligner,
    TimedMultiSequenceAlignment,
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
from scinoephile.llms.aligned_transcription_merge.splitting import (
    get_alignment_content_spans,
)

from .utils import validate_audit_range

__all__ = ["audit_transcription_alignment"]

_BOUNDARY_CHARACTER = "｜"
_GAP_CHARACTER = "　"
_PAUSE_CHARACTER = "・"
_SECTION_SEPARATOR_CHARACTER = "－"


def audit_transcription_alignment(
    artifact: TranscriptionAlignmentArtifact,
    references: Series | Mapping[str, Series] | None = None,
    *,
    reference_similarity: Callable[[TimedAlignmentToken, TimedAlignmentToken], float]
    | None = None,
    first_index: int | None = None,
    last_index: int | None = None,
    first_block: int | None = None,
    last_block: int | None = None,
    include_audio_events: bool = False,
    include_language: bool = False,
    include_speaker: bool = False,
    include_timing_tables: bool = False,
) -> str:
    """Audit aligned ASR, speaker, merged, and optional named references.

    Arguments:
        artifact: portable multi-source transcription alignment
        references: optional named independent references, or one legacy series
        reference_similarity: optional audit-only reference substitution scoring
        first_index: first one-based merged subtitle index to include
        last_index: last one-based merged subtitle index to include
        first_block: first one-based VAD block index to include
        last_block: last one-based VAD block index to include
        include_audio_events: whether to render singing and music rows
        include_language: whether to render the spoken-language row
        include_speaker: whether to render the speaker row
        include_timing_tables: whether to render detailed subtitle timing tables
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if index and block ranges are mixed or invalid
    """
    validate_audit_range(first_index, last_index, first_block, last_block)
    named_references = _get_named_references(artifact, references)
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
        f"- references: {', '.join(named_references) or 'none'}",
        f"- pause encoding: one {_PAUSE_CHARACTER} per {artifact.pause_unit_ms} ms",
        (
            "- merge request boundary: "
            f"{artifact.request_pause_columns} consecutive {_PAUSE_CHARACTER}"
        ),
    ]
    selected_artifact = artifact.model_copy(update={"blocks": tuple(blocks)})
    for reference_name, reference in named_references.items():
        lines.extend(("", f"### Reference {reference_name}", ""))
        lines.extend(_get_metric_summary(selected_artifact, reference))
    if named_references and include_timing_tables:
        lines.extend(("", "## Timing Comparisons", ""))
        for reference_name, reference in named_references.items():
            lines.extend((f"### {reference_name}", ""))
            lines.extend(_get_timing_comparison_lines(selected_artifact, reference))
            lines.append("")

    lines.extend(("", "## Alignments", ""))
    if reference_similarity is None:
        reference_similarity = _get_token_similarity
    aligner = TimedMultiSequenceAligner(reference_similarity)
    for block in blocks:
        lines.extend((f"### Block {block.index}",))
        if block.source_errors:
            errors = "; ".join(
                f"{name}: {error}" for name, error in block.source_errors.items()
            )
            lines.extend(("", f"Source errors: {errors}"))
        if include_timing_tables:
            lines.extend(("", *_get_merged_subtitle_lines(block)))
        block_artifact = artifact.model_copy(update={"blocks": (block,)})
        block_references = {
            reference_name: get_reference_for_alignment(block_artifact, reference)
            for reference_name, reference in named_references.items()
        }
        rendered = _render_block(
            block,
            block_references,
            aligner,
            pause_unit_ms=artifact.pause_unit_ms,
            request_pause_columns=artifact.request_pause_columns,
            include_audio_events=include_audio_events,
            include_language=include_language,
            include_speaker=include_speaker,
        )
        lines.extend(("", "```text", rendered, "```", ""))
    return "\n".join(lines).rstrip() + "\n"


def _get_named_references(
    artifact: TranscriptionAlignmentArtifact,
    references: Series | Mapping[str, Series] | None,
) -> dict[str, Series]:
    """Normalize and validate optional named audit references."""
    if references is None:
        return {}
    if isinstance(references, Series):
        named_references = {"reference": references}
    else:
        named_references = dict(references)
    reserved_names = {
        *(source.name for source in artifact.sources),
        "language",
        "merged",
        "music",
        "singing",
        "speaker",
    }
    for name in named_references:
        if not name.strip() or "\n" in name or "\r" in name:
            raise ValueError("Reference names must be nonblank single-line text.")
        if name in reserved_names:
            raise ValueError(f"Reference name conflicts with alignment row: {name}")
    return named_references


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
    references: Mapping[str, Series],
    aligner: TimedMultiSequenceAligner,
    *,
    pause_unit_ms: int,
    request_pause_columns: int,
    include_audio_events: bool,
    include_language: bool,
    include_speaker: bool,
) -> str:
    """Reconstruct and render one artifact block with named references."""
    artifact_rows = (*block.rows,)
    row_names = tuple(row.name for row in artifact_rows) + ("merged",)
    row_texts = tuple(row.text for row in artifact_rows) + (block.merged,)
    lexical_columns = []
    annotation_rows = _get_annotation_rows(
        block,
        include_audio_events=include_audio_events,
        include_language=include_language,
        include_speaker=include_speaker,
    )
    annotations_by_token_id = {}
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
                annotations_by_token_id[id(token)] = tuple(
                    row[column_idx] for _, row in annotation_rows
                )
            tokens.append(token)
        lexical_columns.append(TimedAlignmentColumn(tuple(tokens)))
    alignment = TimedMultiSequenceAlignment(
        source_names=row_names, columns=tuple(lexical_columns)
    )

    for reference_name, reference in references.items():
        reference_sequence = _get_reference_sequence(reference_name, reference)
        alignment = aligner.add_sequence(alignment, reference_sequence)
    alignment, marker_source_indexes_by_column_id = _get_alignment_with_track_markers(
        alignment, _get_track_markers(block, references)
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

    label_width = max(
        len(name)
        for name in (*alignment.source_names, *(name for name, _ in annotation_rows))
    )
    rendered_chunks = []
    content_spans = get_alignment_content_spans(
        tuple(column.is_pause for column in alignment.columns), request_pause_columns
    )
    for chunk_start, chunk_end in content_spans:
        columns = alignment.columns[chunk_start:chunk_end]
        if not any(
            token is not None
            for column in columns
            for token in column.tokens[: len(artifact_rows)]
        ):
            continue
        lines = []
        for source_idx, source_name in enumerate(alignment.source_names):
            if source_name == "merged":
                lines.append(
                    " " * (label_width + 2)
                    + _SECTION_SEPARATOR_CHARACTER * len(columns)
                )
            cells = [
                _get_alignment_cell(
                    column, source_idx, marker_source_indexes_by_column_id
                )
                for column in columns
            ]
            lines.append(
                f"{source_name:<{label_width}}  "
                + "".join(_get_display_cell(cell) for cell in cells)
            )
            if source_name == "merged":
                for annotation_idx, (annotation_name, _) in enumerate(annotation_rows):
                    annotation_cells = [
                        _get_annotation_cell(
                            column, annotations_by_token_id, annotation_idx
                        )
                        for column in columns
                    ]
                    lines.append(
                        f"{annotation_name:<{label_width}}  "
                        + "".join(_get_display_cell(cell) for cell in annotation_cells)
                    )

        rendered_chunks.append("\n".join(lines))
    return "\n\n".join(rendered_chunks)


def _get_annotation_rows(
    block: TranscriptionAlignmentBlock,
    *,
    include_audio_events: bool,
    include_language: bool,
    include_speaker: bool,
) -> list[tuple[str, str]]:
    """Get present portable annotation rows in stable display order."""
    rows = []
    if include_speaker:
        rows.append(("speaker", block.speaker))
    if include_language and block.language_trace is not None:
        rows.append(("language", block.language_trace))
    if include_audio_events:
        rows.extend(
            (name, row)
            for name, row in (
                ("singing", block.singing_trace),
                ("music", block.music_trace),
            )
            if row is not None
        )
    return rows


def _get_alignment_cell(
    column: TimedAlignmentColumn,
    source_idx: int,
    marker_source_indexes_by_column_id: dict[int, frozenset[int]],
) -> str:
    """Get one displayed cell from an augmented audit alignment."""
    if column.is_marker:
        if source_idx in marker_source_indexes_by_column_id[id(column)]:
            return _BOUNDARY_CHARACTER
        return _GAP_CHARACTER
    if column.is_pause:
        return _PAUSE_CHARACTER
    token = column.tokens[source_idx]
    if token is None:
        return _GAP_CHARACTER
    return token.text


def _get_alignment_with_track_markers(
    alignment: TimedMultiSequenceAlignment,
    markers_by_source: dict[str, tuple[tuple[int, float], ...]],
) -> tuple[TimedMultiSequenceAlignment, dict[int, frozenset[int]]]:
    """Insert and collapse row-owned markers at aligned lexical boundaries."""
    markers_by_boundary: dict[int, dict[int, list[float]]] = {}
    for source_name, markers in markers_by_source.items():
        source_idx = alignment.source_names.index(source_name)
        boundaries_by_token_count = {0: 0}
        token_count = 0
        for boundary, column in enumerate(alignment.columns, 1):
            if column.tokens[source_idx] is not None:
                token_count += 1
                boundaries_by_token_count[token_count] = boundary
        for marker_token_count, marker_time in markers:
            if marker_token_count not in boundaries_by_token_count:
                raise ValueError(
                    f"{source_name} subtitle boundaries exceed its aligned text."
                )
            boundary = boundaries_by_token_count[marker_token_count]
            markers_by_boundary.setdefault(boundary, {}).setdefault(
                source_idx, []
            ).append(marker_time)

    output_columns = []
    marker_source_indexes_by_column_id = {}
    for boundary in range(len(alignment.columns) + 1):
        markers_at_boundary = markers_by_boundary.get(boundary, {})
        marker_count = max(map(len, markers_at_boundary.values()), default=0)
        for marker_idx in range(marker_count):
            marker_source_indexes = frozenset(
                source_idx
                for source_idx, marker_times in markers_at_boundary.items()
                if marker_idx < len(marker_times)
            )
            marker_times = [
                markers_at_boundary[source_idx][marker_idx]
                for source_idx in marker_source_indexes
            ]
            marker_column = TimedAlignmentColumn(
                (None,) * len(alignment.source_names),
                marker=_BOUNDARY_CHARACTER,
                marker_time_seconds=median(marker_times),
            )
            output_columns.append(marker_column)
            marker_source_indexes_by_column_id[id(marker_column)] = (
                marker_source_indexes
            )
        if boundary < len(alignment.columns):
            output_columns.append(alignment.columns[boundary])
    return (
        TimedMultiSequenceAlignment(
            source_names=alignment.source_names, columns=tuple(output_columns)
        ),
        marker_source_indexes_by_column_id,
    )


def _get_alignment_characters(text: str) -> tuple[str, ...]:
    """Get lexical characters that participate in the displayed alignment."""
    return tuple(
        character
        for character in text
        if not unicodedata.category(character).startswith(("C", "P", "S", "Z"))
    )


def _get_display_cell(character: str) -> str:
    """Render one character as a fullwidth alignment cell."""
    codepoint = ord(character)
    if 0x21 <= codepoint <= 0x7E:
        return chr(codepoint + 0xFEE0)
    normalized = unicodedata.normalize("NFKC", character)
    if len(normalized) == 1 and unicodedata.east_asian_width(normalized) in {"F", "W"}:
        return normalized
    if unicodedata.east_asian_width(character) in {"F", "W"}:
        return character
    return f"{character} "


def _get_annotation_cell(
    column: TimedAlignmentColumn,
    annotations_by_token_id: dict[int, tuple[str, ...]],
    annotation_idx: int,
) -> str:
    """Project one stored annotation row through added reference columns."""
    if column.is_marker:
        return _GAP_CHARACTER
    if column.is_pause:
        return _PAUSE_CHARACTER
    for token in column.tokens:
        if token is not None and id(token) in annotations_by_token_id:
            return annotations_by_token_id[id(token)][annotation_idx]
    return _GAP_CHARACTER


def _get_reference_sequence(
    reference_name: str, reference: Series
) -> TimedAlignmentSequence:
    """Convert reference subtitles into approximately timed lexical characters."""
    tokens = []
    for subtitle in reference:
        characters = _get_alignment_characters(subtitle.text_with_newline)
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
    return TimedAlignmentSequence(reference_name, tuple(tokens))


def _get_track_markers(
    block: TranscriptionAlignmentBlock, references: Mapping[str, Series]
) -> dict[str, tuple[tuple[int, float], ...]]:
    """Get subtitle-end token counts and times for each boundary-owning row."""
    merged_token_count = 0
    merged_markers = []
    for subtitle in block.subtitles:
        merged_token_count += len(_get_alignment_characters(subtitle.text))
        merged_markers.append((merged_token_count, subtitle.speech_end_ms / 1000))
    markers_by_source = {"merged": tuple(merged_markers)}
    for reference_name, reference in references.items():
        reference_token_count = 0
        reference_markers = []
        for subtitle in reference:
            reference_token_count += len(
                _get_alignment_characters(subtitle.text_with_newline)
            )
            reference_markers.append((reference_token_count, subtitle.end / 1000))
        markers_by_source[reference_name] = tuple(reference_markers)
    return markers_by_source


def _get_token_similarity(one: TimedAlignmentToken, two: TimedAlignmentToken) -> float:
    """Score audit-only reference alignment using text and overall timing."""
    lexical_score = -2.0
    if one.text == two.text:
        lexical_score = 6.0
    one_midpoint = (one.start_seconds + one.end_seconds) / 2
    two_midpoint = (two.start_seconds + two.end_seconds) / 2
    temporal_score = 2.0 * max(-1.0, 1.0 - abs(one_midpoint - two_midpoint))
    return lexical_score + temporal_score
