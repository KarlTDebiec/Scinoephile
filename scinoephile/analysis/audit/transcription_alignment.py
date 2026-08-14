#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Render portable multi-source transcription alignment audits."""

from __future__ import annotations

import unicodedata
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from statistics import median

from scinoephile.analysis.alignment.timed_msa.aligner import Aligner
from scinoephile.analysis.alignment.timed_msa.alignment import Alignment
from scinoephile.analysis.alignment.timed_msa.models import Column, Token
from scinoephile.analysis.character_error_rate import LineCER
from scinoephile.analysis.transcription.alignment_sequence import get_reference_sequence
from scinoephile.analysis.transcription.artifact import (
    AlignmentArtifact,
    AlignmentBlock,
)
from scinoephile.analysis.transcription.timing import (
    evaluate_timing,
    get_reference_for_alignment,
)
from scinoephile.core.subtitles import Series
from scinoephile.core.text import (
    AnsiColor,
    colorize,
    is_lexical_character,
    normalize_nfkc,
)

from .utils import format_index_range, validate_audit_range

__all__ = ["audit_transcription_alignment", "render_transcription_alignment_terminal"]

_MERGE_SUPPORT_CHARACTERS = "０１２３４５６７８９"
"""Fullwidth support levels used in Markdown and as terminal color indexes."""
_MERGE_SUPPORT_RGB_COLORS = (
    (255, 59, 48),
    (255, 90, 54),
    (255, 122, 50),
    (255, 159, 10),
    (255, 214, 10),
    (212, 225, 87),
    (168, 210, 74),
    (114, 201, 65),
    (52, 199, 89),
    (0, 168, 63),
)
"""Red-to-green terminal colors for ascending merge-support levels."""


def audit_transcription_alignment(
    artifact: AlignmentArtifact,
    references: Mapping[str, Series] | None = None,
    *,
    reference_similarity: Callable[[Token, Token], float] | None = None,
    first_index: int | None = None,
    last_index: int | None = None,
    first_block: int | None = None,
    last_block: int | None = None,
    include_audio_events: bool = False,
    include_language: bool = False,
    include_merge_support: bool = False,
    include_speaker: bool = False,
    include_timing_tables: bool = False,
) -> str:
    """Audit aligned ASR, speaker, merged, and optional named references.

    Arguments:
        artifact: portable multi-source transcription alignment
        references: optional named independent references
        reference_similarity: optional audit-only reference substitution scoring
        first_index: first merged subtitle index whose complete block to include
        last_index: last merged subtitle index whose complete block to include
        first_block: first one-based VAD block index to include
        last_block: last one-based VAD block index to include
        include_audio_events: whether to render singing and music rows
        include_language: whether to render the spoken-language row
        include_merge_support: whether to render normalized merged-character support
        include_speaker: whether to render the speaker row
        include_timing_tables: whether to render detailed subtitle timing tables
    Returns:
        Markdown audit report
    Raises:
        ScinoephileError: if index and block ranges are mixed or invalid
        ValueError: if a reference name or reconstructed alignment is invalid
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
        f"- pause encoding: one ・ per {artifact.pause_unit_ms} ms",
        (f"- merge request boundary: {artifact.request_pause_columns} consecutive ・"),
    ]
    if include_merge_support:
        lines.append(
            "- exact merge support: ０=no matching successful ASR source; "
            "９=all successful ASR sources match"
        )
    index_range = format_index_range(first_index, last_index, track_name="merged")
    if index_range is not None:
        lines.append(f"- requested {index_range}; complete containing blocks shown")
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
    aligner = Aligner(reference_similarity)
    for block in blocks:
        lines.append(f"### Block {block.index}")
        if block.source_errors:
            errors = "; ".join(
                f"{name}: {error}" for name, error in block.source_errors.items()
            )
            lines.extend(("", f"Source errors: {errors}"))
        if include_language and (language_legend := _get_language_legend(block)):
            lines.extend(("", language_legend))
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
            request_pause_columns=artifact.request_pause_columns,
            include_audio_events=include_audio_events,
            include_language=include_language,
            include_merge_support=include_merge_support,
            include_speaker=include_speaker,
        )
        lines.extend(("", "```text", rendered, "```", ""))
    return "\n".join(lines).rstrip() + "\n"


def render_transcription_alignment_terminal(
    artifact: AlignmentArtifact,
    references: Mapping[str, Series] | None = None,
    *,
    authoritative_row_name: str = "merged",
    reference_similarity: Callable[[Token, Token], float] | None = None,
    first_index: int | None = None,
    last_index: int | None = None,
    first_block: int | None = None,
    last_block: int | None = None,
    include_audio_events: bool = False,
    include_language: bool = False,
    include_merge_support: bool = False,
    include_speaker: bool = False,
) -> str:
    """Render an ANSI-colored multi-source alignment for a terminal.

    Exact matches are green, substitutions are purple, characters present only
    in the authoritative row are red, and characters absent from it are blue.

    Arguments:
        artifact: portable multi-source transcription alignment
        references: optional named independent references
        authoritative_row_name: named reference or merged row used for coloring
        reference_similarity: optional audit-only reference substitution scoring
        first_index: first merged subtitle index whose complete block to include
        last_index: last merged subtitle index whose complete block to include
        first_block: first one-based VAD block index to include
        last_block: last one-based VAD block index to include
        include_audio_events: whether to render singing and music rows
        include_language: whether to render the spoken-language row
        include_merge_support: whether to render normalized merged-character support
        include_speaker: whether to render the speaker row
    Returns:
        ANSI-colored terminal alignment
    Raises:
        ScinoephileError: if index and block ranges are mixed or invalid
        ValueError: if a reference, authority, or reconstructed alignment is invalid
    """
    validate_audit_range(first_index, last_index, first_block, last_block)
    named_references = _get_named_references(artifact, references)
    valid_authoritative_names = {"merged", *named_references}
    if authoritative_row_name not in valid_authoritative_names:
        options = ", ".join(sorted(valid_authoritative_names))
        raise ValueError(
            f"Authoritative alignment row must be one of: {options}; "
            f"got {authoritative_row_name!r}."
        )
    blocks = _get_selected_blocks(
        artifact.blocks,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
    )
    if reference_similarity is None:
        reference_similarity = _get_token_similarity
    aligner = Aligner(reference_similarity)
    lines = [f"Authority: {authoritative_row_name}"]
    for block in blocks:
        lines.extend(("", f"Block {block.index}"))
        if block.source_errors:
            errors = "; ".join(
                f"{name}: {error}" for name, error in block.source_errors.items()
            )
            lines.append(f"Source errors: {errors}")
        if include_language and (language_legend := _get_language_legend(block)):
            lines.append(language_legend)
        block_artifact = artifact.model_copy(update={"blocks": (block,)})
        block_references = {
            reference_name: get_reference_for_alignment(block_artifact, reference)
            for reference_name, reference in named_references.items()
        }
        lines.append(
            _render_block(
                block,
                block_references,
                aligner,
                request_pause_columns=artifact.request_pause_columns,
                include_audio_events=include_audio_events,
                include_language=include_language,
                include_merge_support=include_merge_support,
                include_speaker=include_speaker,
                authoritative_row_name=authoritative_row_name,
            )
        )
    return "\n".join(lines).rstrip() + "\n"


def _get_alignment_cell(
    column: Column,
    source_idx: int,
    marker_source_indexes_by_column_id: dict[int, frozenset[int]],
) -> str:
    """Get one displayed cell from an augmented audit alignment.

    Arguments:
        column: augmented alignment column
        source_idx: row index whose cell is requested
        marker_source_indexes_by_column_id: marker owners keyed by column identity
    Returns:
        visible lexical, gap, pause, or boundary character
    """
    if column.is_marker:
        if source_idx in marker_source_indexes_by_column_id[id(column)]:
            return "｜"
        return "　"
    if column.is_pause:
        return "・"
    token = column.tokens[source_idx]
    if token is None:
        return "　"
    return token.text


def _get_alignment_cell_color(
    column: Column,
    source_idx: int,
    authoritative_source_idx: int,
    marker_source_indexes_by_column_id: dict[int, frozenset[int]],
    authoritative_peer_source_indexes: tuple[int, ...] | None,
) -> AnsiColor | None:
    """Get a cell color relative to one authoritative alignment row.

    Arguments:
        column: augmented alignment column
        source_idx: row index whose color is requested
        authoritative_source_idx: row index used as the comparison authority
        marker_source_indexes_by_column_id: marker owners keyed by column identity
        authoritative_peer_source_indexes: optional authority comparison peers
    Returns:
        terminal color for the cell, or None for an empty cell
    """
    cell = _get_alignment_cell(column, source_idx, marker_source_indexes_by_column_id)
    color = None
    if cell != "　":
        authoritative_cell = _get_alignment_cell(
            column, authoritative_source_idx, marker_source_indexes_by_column_id
        )
        if source_idx != authoritative_source_idx:
            color = AnsiColor.PURPLE
            if normalize_nfkc(cell) == normalize_nfkc(authoritative_cell):
                color = AnsiColor.GREEN
            elif authoritative_cell == "　":
                color = AnsiColor.BLUE
        else:
            if authoritative_peer_source_indexes is None:
                authoritative_peer_source_indexes = tuple(
                    other_idx
                    for other_idx in range(len(column.tokens))
                    if other_idx != authoritative_source_idx
                )
            other_cells = tuple(
                _get_alignment_cell(
                    column, other_idx, marker_source_indexes_by_column_id
                )
                for other_idx in authoritative_peer_source_indexes
            )
            color = AnsiColor.RED
            comparison_cell = normalize_nfkc(cell)
            if any(
                comparison_cell == normalize_nfkc(other_cell)
                for other_cell in other_cells
            ):
                color = AnsiColor.GREEN
            elif any(other_cell != "　" for other_cell in other_cells):
                color = AnsiColor.PURPLE
    return color


def _get_alignment_characters(text: str) -> tuple[str, ...]:
    """Get lexical characters that participate in the displayed alignment.

    Arguments:
        text: source text containing lexical and formatting characters
    Returns:
        lexical characters in source order
    """
    return tuple(character for character in text if is_lexical_character(character))


def _get_alignment_with_profile_pauses(
    alignment: Alignment,
    profile_column_anchor_ids: tuple[int, ...],
    pause_intervals_by_profile_boundary: Mapping[int, Sequence[tuple[float, float]]],
) -> Alignment:
    """Restore artifact pauses at their fixed production profile boundaries.

    Arguments:
        alignment: reference-augmented lexical alignment
        profile_column_anchor_ids: production token identities in column order
        pause_intervals_by_profile_boundary: pauses grouped by production boundary
    Returns:
        alignment with production pauses restored
    Raises:
        RuntimeError: if reference augmentation loses a production column
    """
    if not pause_intervals_by_profile_boundary:
        return alignment

    profile_boundaries = {0: 0}
    profile_column_idx = 0
    for boundary, column in enumerate(alignment.columns, 1):
        if profile_column_idx >= len(profile_column_anchor_ids):
            break
        anchor_id = profile_column_anchor_ids[profile_column_idx]
        if any(token is not None and id(token) == anchor_id for token in column.tokens):
            profile_column_idx += 1
            profile_boundaries[profile_column_idx] = boundary
    if profile_column_idx != len(profile_column_anchor_ids):
        raise RuntimeError("Audit reference alignment lost an artifact profile column.")

    pauses_by_boundary = {
        profile_boundaries[profile_boundary]: intervals
        for profile_boundary, intervals in pause_intervals_by_profile_boundary.items()
    }
    output_columns = []
    for boundary in range(len(alignment.columns) + 1):
        output_columns.extend(
            Column(
                (None,) * len(alignment.source_names),
                pause_interval_seconds=pause_interval,
            )
            for pause_interval in pauses_by_boundary.get(boundary, ())
        )
        if boundary < len(alignment.columns):
            output_columns.append(alignment.columns[boundary])
    return Alignment(source_names=alignment.source_names, columns=tuple(output_columns))


def _get_alignment_with_track_markers(
    alignment: Alignment, markers_by_source: dict[str, tuple[tuple[int, float], ...]]
) -> tuple[Alignment, dict[int, frozenset[int]]]:
    """Insert and collapse row-owned markers at aligned lexical boundaries.

    Arguments:
        alignment: augmented lexical alignment
        markers_by_source: token counts and times for each boundary-owning row
    Returns:
        marked alignment and marker owners keyed by column identity
    Raises:
        ValueError: if a boundary exceeds its aligned row text
    """
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
            marker_column = Column(
                (None,) * len(alignment.source_names),
                marker="｜",
                marker_time_seconds=median(marker_times),
            )
            output_columns.append(marker_column)
            marker_source_indexes_by_column_id[id(marker_column)] = (
                marker_source_indexes
            )
        if boundary < len(alignment.columns):
            output_columns.append(alignment.columns[boundary])
    return (
        Alignment(source_names=alignment.source_names, columns=tuple(output_columns)),
        marker_source_indexes_by_column_id,
    )


def _get_annotation_cell(
    column: Column,
    annotations_by_token_id: dict[int, tuple[str, ...]],
    annotation_idx: int,
) -> str:
    """Project one stored annotation row through added reference columns.

    Arguments:
        column: reference-augmented alignment column
        annotations_by_token_id: annotation cells keyed by artifact token identity
        annotation_idx: annotation row index to project
    Returns:
        annotation, gap, or pause cell
    """
    if column.is_marker:
        return "　"
    if column.is_pause:
        return "・"
    for token in column.tokens:
        if token is not None and id(token) in annotations_by_token_id:
            return annotations_by_token_id[id(token)][annotation_idx]
    return "　"


def _get_annotation_rows(
    block: AlignmentBlock,
    *,
    include_audio_events: bool,
    include_language: bool,
    include_merge_support: bool,
    include_speaker: bool,
) -> list[tuple[str, str]]:
    """Get present portable annotation rows in stable display order.

    Arguments:
        block: alignment block containing portable annotations
        include_audio_events: whether to include singing and music rows
        include_language: whether to include the spoken-language row
        include_merge_support: whether to include merged-character support
        include_speaker: whether to include the speaker row
    Returns:
        requested annotation names and aligned row text
    """
    rows = []
    if include_speaker:
        rows.append(("speaker", block.speaker))
    if include_merge_support:
        rows.append(("support", _get_merge_support_row(block)))
    if include_language and block.language_trace is not None:
        rows.append(("language", block.language_trace))
    if include_audio_events:
        rows.extend(
            (name, row)
            for name, row in (
                ("music", block.music_trace),
                ("singing", block.singing_trace),
            )
            if row is not None
        )
    return rows


def _get_content_spans(
    shared_pause_columns: Sequence[bool], separator_columns: int
) -> tuple[tuple[int, int], ...]:
    """Get content spans between long shared-pause separators.

    Arguments:
        shared_pause_columns: whether each alignment column is a shared pause
        separator_columns: minimum consecutive pauses separating content spans
    Returns:
        inclusive-start, exclusive-end content spans
    Raises:
        ValueError: if the separator threshold is not positive
    """
    if separator_columns <= 0:
        raise ValueError("Alignment separator column count must be positive.")

    separator_spans = []
    run_start: int | None = None
    for column_idx, is_shared_pause in enumerate((*shared_pause_columns, False)):
        if is_shared_pause:
            if run_start is None:
                run_start = column_idx
            continue
        if run_start is None:
            continue
        if column_idx - run_start >= separator_columns:
            separator_spans.append((run_start, column_idx))
        run_start = None

    content_spans = []
    content_start = 0
    for separator_start, separator_end in separator_spans:
        if content_start < separator_start:
            content_spans.append((content_start, separator_start))
        content_start = separator_end
    if content_start < len(shared_pause_columns):
        content_spans.append((content_start, len(shared_pause_columns)))
    return tuple(content_spans)


def _get_display_cell(character: str) -> str:
    """Render one character as a fullwidth alignment cell.

    Arguments:
        character: character to render
    Returns:
        character occupying one fullwidth terminal cell
    """
    codepoint = ord(character)
    if 0x21 <= codepoint <= 0x7E:
        return chr(codepoint + 0xFEE0)
    normalized = normalize_nfkc(character)
    if len(normalized) == 1 and unicodedata.east_asian_width(normalized) in {"F", "W"}:
        return normalized
    if unicodedata.east_asian_width(character) in {"F", "W"}:
        return character
    return f"{character} "


def _get_language_legend(block: AlignmentBlock) -> str | None:
    """Get the optional language-symbol legend for one alignment block.

    Arguments:
        block: alignment block containing an optional language trace and legend
    Returns:
        formatted language legend, or None when no legend is available
    """
    if block.language_trace is None or not block.language_legend:
        return None
    entries = "; ".join(
        f"{symbol}={label}" for symbol, label in block.language_legend.items()
    )
    return f"Language legend: {entries}"


def _get_merge_support_display_cell(character: str) -> str:
    """Render one support level as a fullwidth ANSI background cell.

    Arguments:
        character: fullwidth support digit, gap, or pause
    Returns:
        terminal-colored support cell
    """
    if character not in _MERGE_SUPPORT_CHARACTERS:
        return _get_display_cell(character)
    support_level = _MERGE_SUPPORT_CHARACTERS.index(character)
    red, green, blue = _MERGE_SUPPORT_RGB_COLORS[support_level]
    return f"\x1b[48;2;{red};{green};{blue}m　{AnsiColor.RESET.value}"


def _get_merge_support_row(block: AlignmentBlock) -> str:
    """Get normalized exact source agreement for each merged column.

    Arguments:
        block: alignment block containing successful source and merged rows
    Returns:
        fullwidth support digits, gaps, and shared pause characters
    """
    source_count = len(block.rows)
    output = []
    for column_idx, merged_character in enumerate(block.merged):
        if merged_character in {"　", "・"}:
            output.append(merged_character)
            continue
        matching_source_count = sum(
            normalize_nfkc(row.text[column_idx]) == normalize_nfkc(merged_character)
            for row in block.rows
        )
        support_level = 0
        if source_count:
            support_level = int(
                matching_source_count
                / source_count
                * (len(_MERGE_SUPPORT_CHARACTERS) - 1)
                + 0.5
            )
        output.append(_MERGE_SUPPORT_CHARACTERS[support_level])
    return "".join(output)


def _get_merged_subtitle_lines(block: AlignmentBlock) -> list[str]:
    """Get a table of merged subtitle speech and display timing.

    Arguments:
        block: alignment block containing merged subtitles
    Returns:
        Markdown timing-table lines
    """
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


def _get_metric_summary(artifact: AlignmentArtifact, reference: Series) -> list[str]:
    """Get CER and timing summary lines for selected blocks.

    Arguments:
        artifact: selected alignment artifact
        reference: independent reference subtitles
    Returns:
        Markdown summary list items
    """
    selected_reference = get_reference_for_alignment(artifact, reference)
    reference_text = "".join(
        subtitle.text_with_newline for subtitle in selected_reference
    )
    source_texts = {source.name: [] for source in artifact.sources}
    for block in artifact.blocks:
        rows = {row.name: row.text for row in block.rows}
        for source in artifact.sources:
            row = rows.get(source.name, "")
            source_texts[source.name].append(row.replace("　", "").replace("・", ""))
    candidates = {name: "".join(parts) for name, parts in source_texts.items()}
    candidates["merged"] = "".join(
        subtitle.text for block in artifact.blocks for subtitle in block.subtitles
    )
    lines = [f"- reference subtitles: {len(selected_reference)}"]
    for name, candidate_text in candidates.items():
        result = LineCER(reference_text, candidate_text)
        lines.append(f"- {name} CER: {result.cer:.3%}")
    timing = evaluate_timing(artifact, reference)
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


def _get_named_references(
    artifact: AlignmentArtifact, references: Mapping[str, Series] | None
) -> dict[str, Series]:
    """Validate and copy optional named audit references.

    Arguments:
        artifact: alignment artifact whose row names are reserved
        references: optional named independent references
    Returns:
        validated references preserving input order
    Raises:
        ValueError: if a reference name is invalid or conflicts with a row
    """
    named_references = dict(references or {})
    reserved_names = {
        *(source.name for source in artifact.sources),
        "language",
        "merged",
        "music",
        "singing",
        "speaker",
        "support",
    }
    for name in named_references:
        if not name.strip() or "\n" in name or "\r" in name:
            raise ValueError("Reference names must be nonblank single-line text.")
        if name in reserved_names:
            raise ValueError(f"Reference name conflicts with alignment row: {name}")
    return named_references


def _get_rendered_annotation_lines(
    columns: Sequence[Column],
    annotation_rows: Sequence[tuple[str, str]],
    annotations_by_token_id: dict[int, tuple[str, ...]],
    *,
    authoritative_source_idx: int | None,
    label_width: int,
) -> tuple[list[str], list[str]]:
    """Render inline and post-reference annotation lines.

    Arguments:
        columns: alignment columns in the rendered chunk
        annotation_rows: named artifact annotation rows
        annotations_by_token_id: annotation cells keyed by artifact token identity
        authoritative_source_idx: optional row index indicating terminal output
        label_width: display width reserved for row labels
    Returns:
        annotation lines rendered before and after reference rows
    """
    inline_lines = []
    trailing_lines = []
    for annotation_idx, (annotation_name, _) in enumerate(annotation_rows):
        annotation_cells = [
            _get_annotation_cell(column, annotations_by_token_id, annotation_idx)
            for column in columns
        ]
        display_cells = []
        for cell in annotation_cells:
            if annotation_name == "support" and authoritative_source_idx is not None:
                display_cells.append(_get_merge_support_display_cell(cell))
            else:
                display_cells.append(_get_display_cell(cell))
        annotation_line = f"{annotation_name:<{label_width}}  " + "".join(display_cells)
        if annotation_name in {"language", "music", "singing", "support"}:
            trailing_lines.append(annotation_line)
        else:
            inline_lines.append(annotation_line)
    return inline_lines, trailing_lines


def _get_selected_blocks(
    blocks: Sequence[AlignmentBlock],
    *,
    first_index: int | None,
    last_index: int | None,
    first_block: int | None,
    last_block: int | None,
) -> list[AlignmentBlock]:
    """Select complete artifact blocks by block or contained subtitle indexes.

    Arguments:
        blocks: alignment blocks in source order
        first_index: first merged subtitle index whose block to include
        last_index: last merged subtitle index whose block to include
        first_block: first VAD block index to include
        last_block: last VAD block index to include
    Returns:
        complete blocks intersecting the requested range
    """
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


def _get_timing_comparison_lines(
    artifact: AlignmentArtifact, reference: Series
) -> list[str]:
    """Get text-aligned candidate/reference timing comparisons.

    Arguments:
        artifact: selected alignment artifact
        reference: independent reference subtitles
    Returns:
        Markdown timing-comparison table lines
    """
    timing = evaluate_timing(artifact, reference)
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


def _get_token_similarity(one: Token, two: Token) -> float:
    """Score audit-only reference alignment using text and overall timing.

    Arguments:
        one: first timed alignment token
        two: second timed alignment token
    Returns:
        combined lexical and temporal substitution score
    """
    lexical_score = -2.0
    if normalize_nfkc(one.text) == normalize_nfkc(two.text):
        lexical_score = 6.0
    one_midpoint = (one.start_seconds + one.end_seconds) / 2
    two_midpoint = (two.start_seconds + two.end_seconds) / 2
    temporal_score = 2.0 * max(-1.0, 1.0 - abs(one_midpoint - two_midpoint))
    return lexical_score + temporal_score


def _get_track_markers(
    block: AlignmentBlock, references: Mapping[str, Series]
) -> dict[str, tuple[tuple[int, float], ...]]:
    """Get subtitle-end token counts and times for boundary-owning rows.

    Arguments:
        block: alignment block containing merged subtitles
        references: named references selected for this block
    Returns:
        boundary token counts and times grouped by row name
    """
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


def _render_block(
    block: AlignmentBlock,
    references: Mapping[str, Series],
    aligner: Aligner,
    *,
    request_pause_columns: int,
    include_audio_events: bool,
    include_language: bool,
    include_merge_support: bool,
    include_speaker: bool,
    authoritative_row_name: str | None = None,
) -> str:
    """Reconstruct and render one artifact block with named references.

    Arguments:
        block: portable alignment block to render
        references: named references selected for this block
        aligner: timed aligner used to add reference rows
        request_pause_columns: consecutive pauses separating rendered chunks
        include_audio_events: whether to render singing and music rows
        include_language: whether to render the spoken-language row
        include_merge_support: whether to render merged-character support
        include_speaker: whether to render the speaker row
        authoritative_row_name: optional row used for terminal coloring
    Returns:
        rendered block alignment
    Raises:
        RuntimeError: if reference augmentation loses an artifact column
        ValueError: if rows, markers, or separator settings are invalid
    """
    row_names = tuple(row.name for row in block.rows) + ("merged",)
    row_texts = tuple(row.text for row in block.rows) + (block.merged,)
    lexical_columns = []
    pause_intervals_by_profile_boundary: dict[int, list[tuple[float, float]]] = {}
    profile_column_anchor_ids = []
    annotation_rows = _get_annotation_rows(
        block,
        include_audio_events=include_audio_events,
        include_language=include_language,
        include_merge_support=include_merge_support,
        include_speaker=include_speaker,
    )
    annotations_by_token_id = {}
    for column_idx, column in enumerate(block.columns):
        if column.kind == "pause":
            pause_intervals_by_profile_boundary.setdefault(
                len(lexical_columns), []
            ).append((column.start_ms / 1000, column.end_ms / 1000))
            continue
        tokens = []
        for row_text in row_texts:
            character = row_text[column_idx]
            token = None
            if character != "　":
                token = Token(character, column.start_ms / 1000, column.end_ms / 1000)
                annotations_by_token_id[id(token)] = tuple(
                    row[column_idx] for _, row in annotation_rows
                )
            tokens.append(token)
        lexical_column = Column(tuple(tokens))
        lexical_columns.append(lexical_column)
        profile_column_anchor_ids.append(
            id(next(token for token in lexical_column.tokens if token is not None))
        )
    alignment = Alignment(source_names=row_names, columns=tuple(lexical_columns))

    for reference_name, reference in references.items():
        reference_sequence = get_reference_sequence(reference_name, reference)
        alignment = aligner.add_sequence(alignment, reference_sequence)
    alignment = _get_alignment_with_profile_pauses(
        alignment, tuple(profile_column_anchor_ids), pause_intervals_by_profile_boundary
    )
    alignment, marker_source_indexes_by_column_id = _get_alignment_with_track_markers(
        alignment, _get_track_markers(block, references)
    )
    authoritative_source_idx = None
    authoritative_peer_source_indexes = None
    if authoritative_row_name is not None:
        authoritative_source_idx = alignment.source_names.index(authoritative_row_name)
        if authoritative_row_name != "merged":
            authoritative_peer_source_indexes = (
                alignment.source_names.index("merged"),
            )

    label_width = max(
        len(name)
        for name in (*alignment.source_names, *(name for name, _ in annotation_rows))
    )
    rendered_chunks = []
    content_spans = _get_content_spans(
        tuple(column.is_pause for column in alignment.columns), request_pause_columns
    )
    for chunk_start, chunk_end in content_spans:
        columns = alignment.columns[chunk_start:chunk_end]
        rendered_chunk = _render_chunk(
            columns,
            alignment,
            annotation_rows=annotation_rows,
            annotations_by_token_id=annotations_by_token_id,
            marker_source_indexes_by_column_id=marker_source_indexes_by_column_id,
            authoritative_source_idx=authoritative_source_idx,
            authoritative_peer_source_indexes=authoritative_peer_source_indexes,
            label_width=label_width,
        )
        if rendered_chunk is not None:
            rendered_chunks.append(rendered_chunk)
    return "\n\n".join(rendered_chunks)


def _render_chunk(
    columns: Sequence[Column],
    alignment: Alignment,
    *,
    annotation_rows: Sequence[tuple[str, str]],
    annotations_by_token_id: dict[int, tuple[str, ...]],
    marker_source_indexes_by_column_id: dict[int, frozenset[int]],
    authoritative_source_idx: int | None,
    authoritative_peer_source_indexes: tuple[int, ...] | None,
    label_width: int,
) -> str | None:
    """Render one long-pause-delimited alignment chunk.

    Arguments:
        columns: alignment columns in the chunk
        alignment: complete alignment providing row names
        annotation_rows: named artifact annotation rows
        annotations_by_token_id: annotation cells keyed by artifact token identity
        marker_source_indexes_by_column_id: marker owners keyed by column identity
        authoritative_source_idx: optional row index used for terminal coloring
        authoritative_peer_source_indexes: optional peers for the authoritative row
        label_width: display width reserved for row labels
    Returns:
        rendered chunk, or None when it contains no production text
    """
    profile_source_count = alignment.source_names.index("merged") + 1
    if not any(
        token is not None
        for column in columns
        for token in column.tokens[:profile_source_count]
    ):
        return None

    inline_annotation_lines, trailing_annotation_lines = _get_rendered_annotation_lines(
        columns,
        annotation_rows,
        annotations_by_token_id,
        authoritative_source_idx=authoritative_source_idx,
        label_width=label_width,
    )
    lines = []
    for source_idx, source_name in enumerate(alignment.source_names):
        if source_name == "merged":
            lines.append(" " * (label_width + 2) + "－" * len(columns))
        cells = []
        for column in columns:
            cell = _get_alignment_cell(
                column, source_idx, marker_source_indexes_by_column_id
            )
            display_cell = _get_display_cell(cell)
            if authoritative_source_idx is not None:
                color = _get_alignment_cell_color(
                    column,
                    source_idx,
                    authoritative_source_idx,
                    marker_source_indexes_by_column_id,
                    authoritative_peer_source_indexes,
                )
                if color is not None:
                    display_cell = colorize(display_cell, color)
            cells.append(display_cell)
        lines.append(f"{source_name:<{label_width}}  " + "".join(cells))
        if source_name == "merged":
            lines.extend(inline_annotation_lines)
    lines.extend(trailing_annotation_lines)
    return "\n".join(lines)
