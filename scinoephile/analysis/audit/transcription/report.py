#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Assemble portable multi-source transcription alignment audit reports."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence

from scinoephile.analysis.alignment.timed_msa.aligner import Aligner
from scinoephile.analysis.alignment.timed_msa.models import Token
from scinoephile.analysis.audit.utils import format_index_range, validate_audit_range
from scinoephile.analysis.transcription.artifact import (
    AlignmentArtifact,
    AlignmentBlock,
)
from scinoephile.analysis.transcription.evaluation import (
    evaluate_selected_character_errors,
    evaluate_transcription,
)
from scinoephile.analysis.transcription.timing import (
    evaluate_timing,
    get_block_references,
)
from scinoephile.core.subtitles import Series
from scinoephile.core.text import normalize_nfkc

from .rendering import render_transcription_alignment_block

__all__ = ["audit_transcription_alignment", "render_transcription_alignment_terminal"]


def audit_transcription_alignment(
    artifact: AlignmentArtifact,
    references: Mapping[str, Series] | None = None,
    *,
    token_similarity: Callable[[Token, Token], float] | None = None,
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
        token_similarity: optional token substitution scoring for reference alignment
            and merged-character support
        first_index: first merged subtitle index whose complete block to include
        last_index: last merged subtitle index whose complete block to include
        first_block: first one-based block index to include
        last_block: last one-based block index to include
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
    block_references = {
        reference_name: get_block_references(artifact, reference)
        for reference_name, reference in named_references.items()
    }
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
        f"- selected blocks: {len(blocks)}",
        f"- selected merged subtitles: {sum(len(block.subtitles) for block in blocks)}",
        f"- references: {', '.join(named_references) or 'none'}",
        f"- pause encoding: one ・ per {artifact.pause_unit_ms} ms",
        (f"- merge request boundary: {artifact.request_pause_columns} consecutive ・"),
    ]
    if include_merge_support:
        lines.append(
            "- merge support: ０=no similar successful ASR source; "
            "９=all successful ASR sources match"
        )
    index_range = format_index_range(first_index, last_index, track_name="merged")
    if index_range is not None:
        lines.append(f"- requested {index_range}; complete containing blocks shown")
    selected_artifact = artifact.model_copy(update={"blocks": tuple(blocks)})
    for reference_name, reference in named_references.items():
        lines.extend(("", f"### Reference {reference_name}", ""))
        lines.extend(_get_metric_summary(selected_artifact, reference))
        lines.extend(
            (
                "",
                "#### Block CER",
                "",
                (
                    "Sorted by merged CER, highest first. Blocks without reference "
                    "characters are unscored and listed last."
                ),
                "",
                *_get_block_cer_lines(
                    selected_artifact, block_references[reference_name]
                ),
            )
        )
    if named_references and include_timing_tables:
        lines.extend(("", "## Timing Comparisons", ""))
        for reference_name, reference in named_references.items():
            lines.extend((f"### {reference_name}", ""))
            lines.extend(_get_timing_comparison_lines(selected_artifact, reference))
            lines.append("")

    lines.extend(("", "## Alignments", ""))
    if token_similarity is None:
        token_similarity = _get_token_similarity
    aligner = Aligner(token_similarity)
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
        references_for_block = {
            reference_name: references_by_block[block.index]
            for reference_name, references_by_block in block_references.items()
        }
        rendered = render_transcription_alignment_block(
            block,
            references_for_block,
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
    token_similarity: Callable[[Token, Token], float] | None = None,
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
        token_similarity: optional token substitution scoring for reference alignment
            and merged-character support
        first_index: first merged subtitle index whose complete block to include
        last_index: last merged subtitle index whose complete block to include
        first_block: first one-based block index to include
        last_block: last one-based block index to include
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
    block_references = {
        reference_name: get_block_references(artifact, reference)
        for reference_name, reference in named_references.items()
    }
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
    if token_similarity is None:
        token_similarity = _get_token_similarity
    aligner = Aligner(token_similarity)
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
        references_for_block = {
            reference_name: references_by_block[block.index]
            for reference_name, references_by_block in block_references.items()
        }
        lines.append(
            render_transcription_alignment_block(
                block,
                references_for_block,
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


def _get_block_cer_lines(
    artifact: AlignmentArtifact, references_by_block: Mapping[int, Series]
) -> list[str]:
    """Get block-level CER rows sorted by merged error rate.

    Arguments:
        artifact: selected alignment artifact
        references_by_block: globally aligned reference subtitles by block index
    Returns:
        Markdown table lines
    """
    candidate_names = ("merged", *(source.name for source in artifact.sources))
    block_results = []
    for block in artifact.blocks:
        block_artifact = artifact.model_copy(update={"blocks": (block,)})
        block_results.append(
            (
                block.index,
                evaluate_selected_character_errors(
                    block_artifact, references_by_block[block.index]
                ),
            )
        )
    block_results.sort(
        key=lambda result: (
            result[1]["merged"].reference_length == 0,
            -result[1]["merged"].cer,
            result[0],
        )
    )

    headers = ("Block", "Reference characters", *candidate_names)
    rows = []
    for block_index, metrics_by_name in block_results:
        reference_length = metrics_by_name["merged"].reference_length
        rows.append(
            (
                str(block_index),
                str(reference_length),
                *(
                    "—" if reference_length == 0 else f"{metrics_by_name[name].cer:.0%}"
                    for name in candidate_names
                ),
            )
        )
    widths = tuple(
        max(4, len(header), *(len(row[index]) for row in rows))
        for index, header in enumerate(headers)
    )
    return [
        "| "
        + " | ".join(
            header.rjust(width) for header, width in zip(headers, widths, strict=True)
        )
        + " |",
        "| " + " | ".join("-" * (width - 1) + ":" for width in widths) + " |",
        *(
            "| "
            + " | ".join(
                cell.rjust(width) for cell, width in zip(row, widths, strict=True)
            )
            + " |"
            for row in rows
        ),
    ]


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
    evaluation = evaluate_transcription(artifact, reference)
    lines = [f"- reference subtitles: {evaluation.reference_subtitles}"]
    for name, result in evaluation.character_errors.items():
        lines.append(f"- {name} CER: {result.cer:.3%}")
    timing = evaluation.timing
    group_counts = timing.candidate_to_reference_group_counts
    lines.extend(
        (
            f"- text-aligned timing groups: {len(timing.pairs)}",
            (
                "- candidate:reference subtitle groups: "
                + ", ".join(
                    f"{shape} × {count}" for shape, count in group_counts.items()
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
        first_block: first block index to include
        last_block: last block index to include
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
    candidate_indexes = tuple(
        subtitle.index for block in artifact.blocks for subtitle in block.subtitles
    )
    lines = [
        "| Candidate | Reference | Candidate display | Reference display | IoU | "
        "Δ start | Δ end |",
        "| :--- | :--- | :--- | :--- | ---: | ---: | ---: |",
    ]
    for pair in timing.pairs:
        candidate_index_text = ",".join(
            str(candidate_indexes[index - 1]) for index in pair.candidate_indexes
        )
        lines.append(
            f"| {candidate_index_text} | "
            f"{','.join(map(str, pair.reference_indexes))} | "
            f"{pair.candidate_start_ms / 1000:.3f}–"
            f"{pair.candidate_end_ms / 1000:.3f} s | "
            f"{pair.reference_start_ms / 1000:.3f}–"
            f"{pair.reference_end_ms / 1000:.3f} s | "
            f"{pair.intersection_over_union:.1%} | "
            f"{pair.start_error_ms:+d} ms | {pair.end_error_ms:+d} ms |"
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
