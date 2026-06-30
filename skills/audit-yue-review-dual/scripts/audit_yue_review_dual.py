#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit Yue reviews and final simplified-Hant comparison in one table."""

from __future__ import annotations

import argparse
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

__all__ = [
    "AuditPaths",
    "ReviewChange",
    "SrtEvent",
    "audit_dataset",
    "format_markdown",
    "parse_srt",
]

_OK_CANTONESE_REPLACEMENTS = (
    ("忤怍", "仵作"),
    ("蒙吖", "懵吓"),
    ("矇吖", "懵吓"),
    ("们", "哋"),
    ("們", "哋"),
    ("架", "㗎"),
    ("罗", "啰"),
    ("祇", "只"),
    ("祗", "只"),
    ("搵", "揾"),
    ("哋", "地"),
    ("来", "嚟"),
    ("來", "嚟"),
    ("呀", "吖"),
    ("洗", "使"),
    ("左", "咗"),
    ("舖", "鋪"),
    ("吓", "下"),
    ("鼓", "旧"),
    ("鼓", "舊"),
    ("喱", "匿"),
    ("逗", "豆"),
    ("污", "侮"),
    ("币", "弊"),
    ("幣", "弊"),
    ("茅", "猾"),
    ("重", "仲"),
)
_OK_CANTONESE_REPLACEMENTS_BY_SOURCE_LENGTH = sorted(
    _OK_CANTONESE_REPLACEMENTS,
    key=lambda replacement: len(replacement[0]),
    reverse=True,
)
_SERIES_LABELS = {
    "hans_original": "yue-Hans source",
    "hans_review": "yue-Hans review",
    "hans_final": "yue-Hans final",
    "hant_original": "yue-Hant source",
    "hant_review": "yue-Hant review",
    "hant_final": "yue-Hant final simplified review",
}


@dataclass(frozen=True)
class AuditPaths:
    """Paths and validation rules for one Yue dual-review audit."""

    layout: str
    """Input/output layout name."""

    hans_dir_path: Path
    """Yue-Hans output directory."""

    hant_dir_path: Path
    """Yue-Hant output directory."""

    hans_original_path: Path
    """Yue-Hans review input path."""

    hans_review_path: Path
    """Yue-Hans review output path."""

    hans_final_path: Path
    """Final yue-Hans comparison path."""

    hant_original_path: Path
    """Yue-Hant review input path."""

    hant_review_path: Path
    """Yue-Hant review output path."""

    hant_final_path: Path
    """Final simplified yue-Hant comparison path."""

    timing_groups: tuple[tuple[str, ...], ...]
    """Labels to validate for matching timings."""

    context_lines: tuple[str, ...]
    """Extra summary context lines."""


@dataclass(frozen=True)
class ReviewChange:
    """One review edit."""

    original: str
    """Original validated subtitle text."""

    revised: str
    """Reviewed subtitle text."""


@dataclass(frozen=True)
class SrtEvent:
    """One SRT event parsed without normalizing text."""

    number: int
    """Subtitle number."""

    timing: str
    """Raw timing line."""

    text: str
    """Raw subtitle text."""


def audit_dataset(
    dataset_name: str,
    data_root_path: Path,
    layout: str = "auto",
    *,
    first_index: int | None = None,
    last_index: int | None = None,
    omit_ok: bool = False,
) -> str:
    """Audit one Yue dataset and return a Markdown report.

    Arguments:
        dataset_name: dataset name under `test/data`
        data_root_path: root path containing dataset directories
        layout: dataset layout, either auto, ocr, or non-ocr
        first_index: first 1-indexed subtitle number to include, inclusive
        last_index: last 1-indexed subtitle number to include, inclusive
        omit_ok: whether to omit rows whose generated note is OK
    Returns:
        Markdown report
    """
    _validate_index_range(first_index, last_index)
    paths = _get_audit_paths(dataset_name, data_root_path, layout)
    series_paths = {
        "hans_original": paths.hans_original_path,
        "hans_review": paths.hans_review_path,
        "hans_final": paths.hans_final_path,
        "hant_original": paths.hant_original_path,
        "hant_review": paths.hant_review_path,
        "hant_final": paths.hant_final_path,
    }
    series = {
        name: {
            number: event
            for number, event in sorted(parse_srt(series_path).items())
            if (first_index is None or number >= first_index)
            and (last_index is None or number <= last_index)
        }
        for name, series_path in series_paths.items()
    }
    _validate_counts_and_timing(
        {label: series[name] for name, label in _SERIES_LABELS.items()},
        paths.timing_groups,
    )

    return format_markdown(
        dataset_name=dataset_name,
        layout=paths.layout,
        context_lines=(
            *_get_index_range_context_lines(first_index, last_index),
            *paths.context_lines,
        ),
        series=series,
        hans_changes=_get_review_changes(
            series["hans_original"],
            series["hans_review"],
        ),
        hant_changes=_get_review_changes(
            series["hant_original"],
            series["hant_review"],
        ),
        final_differences=_get_text_differences(
            series["hans_final"],
            series["hant_final"],
        ),
        omit_ok=omit_ok,
    )


def format_markdown(
    *,
    dataset_name: str,
    layout: str,
    context_lines: Sequence[str],
    series: Mapping[str, Mapping[int, SrtEvent]],
    hans_changes: Mapping[int, ReviewChange],
    hant_changes: Mapping[int, ReviewChange],
    final_differences: Mapping[int, tuple[str, str]],
    omit_ok: bool = False,
) -> str:
    """Format an audit report as Markdown.

    Arguments:
        dataset_name: dataset name
        layout: input/output layout name
        context_lines: extra summary context lines
        series: parsed SRT events keyed by internal series name
        hans_changes: yue-Hans review changes by subtitle number
        hant_changes: yue-Hant review changes by subtitle number
        final_differences: final text differences by subtitle number
        omit_ok: whether to omit rows whose generated note is OK
    Returns:
        Markdown report
    """
    hans_original = series["hans_original"]
    hans_review = series["hans_review"]
    hans_final = series["hans_final"]
    hant_original = series["hant_original"]
    hant_review = series["hant_review"]
    hant_final = series["hant_final"]
    changed_numbers = sorted(
        set(hans_changes) | set(hant_changes) | set(final_differences)
    )
    row_lines: list[str] = []
    for number in changed_numbers:
        hans_change = hans_changes.get(number)
        hant_change = hant_changes.get(number)
        final_pair = final_differences.get(number)
        note = _get_notes(
            number=number,
            hans_change=hans_change,
            hant_change=hant_change,
            final_pair=final_pair,
            hans_review=hans_review,
            hant_review=hant_review,
            hans_final=hans_final,
            hant_final=hant_final,
        )
        if omit_ok and note == "OK":
            continue
        include_unchanged_review_text = bool(hans_change or hant_change)
        if final_pair is None:
            final_series = hans_final.get(number) or hant_final.get(number)
            final_cell = "" if final_series is None else final_series.text
        else:
            final_cell = f"{final_pair[0]}\n{final_pair[1]}"
        row_lines.append(
            "| "
            + " | ".join(
                [
                    _escape_cell(str(number)),
                    _escape_cell(
                        _format_review_cell(
                            number=number,
                            change=hans_change,
                            reviewed=hans_review,
                            include_unchanged=include_unchanged_review_text,
                        )
                    ),
                    _escape_cell(
                        _format_review_cell(
                            number=number,
                            change=hant_change,
                            reviewed=hant_review,
                            include_unchanged=include_unchanged_review_text,
                        )
                    ),
                    _escape_cell(final_cell),
                    _escape_cell(note),
                ]
            )
            + " |"
        )

    summary_context_lines = list(context_lines)
    if omit_ok:
        summary_context_lines.insert(0, "- omitted rows whose generated note is OK")
    lines = [
        f"# {dataset_name} Yue Review Dual",
        "",
        "## Summary",
        "",
        f"- yue-Hans source/review count: {len(hans_original)} -> {len(hans_review)}",
        f"- yue-Hant source/review count: {len(hant_original)} -> {len(hant_review)}",
        f"- final yue-Hans / simplified yue-Hant count: "
        f"{len(hans_final)} / {len(hant_final)}",
        f"- yue-Hans review edits: {len(hans_changes)}",
        f"- yue-Hant review edits: {len(hant_changes)}",
        f"- final text differences: {len(final_differences)}",
        f"- layout: {layout}",
        "- subtitle counts: aligned across all audited SRT files",
        "- timings: aligned within comparable source/review and final groups",
        f"- table rows: {len(row_lines)}",
        *summary_context_lines,
        "",
        "## Audit Table",
        "",
        "| Subtitle | yue-Hans | yue-Hant | yue-Hans vs Hant->Hans | Notes |",
        "|---:|---|---|---|---|",
        *row_lines,
    ]
    return "\n".join(lines) + "\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Arguments:
        argv: optional argument sequence
    Returns:
        parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Audit Yue review changes and final simplified-Hant differences."
    )
    parser.add_argument(
        "--dataset",
        required=True,
        help="Dataset name under test/data, such as acoptc or acopopb",
    )
    parser.add_argument(
        "--data-root",
        default=Path("test/data"),
        type=Path,
        help="Path to test data root. Default: test/data",
    )
    parser.add_argument(
        "--layout",
        choices=("auto", "ocr", "non-ocr"),
        default="auto",
        help="Dataset layout. Default: auto",
    )
    parser.add_argument(
        "--first-index",
        type=int,
        help="First 1-indexed subtitle number to include, inclusive",
    )
    parser.add_argument(
        "--last-index",
        type=int,
        help="Last 1-indexed subtitle number to include, inclusive",
    )
    parser.add_argument(
        "--omit-ok",
        action="store_true",
        help="Omit table rows whose generated note is OK",
    )
    return parser.parse_args(argv)


def parse_srt(srt_file_path: Path) -> dict[int, SrtEvent]:
    """Parse an SRT file without normalizing subtitle text.

    Arguments:
        srt_file_path: SRT file path
    Returns:
        SRT events keyed by subtitle number
    """
    text = srt_file_path.read_text(encoding="utf-8-sig")
    blocks = [block for block in text.replace("\r\n", "\n").split("\n\n") if block]
    events: dict[int, SrtEvent] = {}
    for block in blocks:
        lines = block.split("\n")
        if len(lines) < 2:
            continue
        number = int(lines[0])
        timing = lines[1]
        subtitle_text = "\n".join(lines[2:])
        events[number] = SrtEvent(number=number, timing=timing, text=subtitle_text)
    return events


def main(argv: Sequence[str] | None = None) -> None:
    """Run the Yue review dual audit.

    Arguments:
        argv: optional argument sequence
    """
    args = parse_args(argv)
    try:
        print(
            audit_dataset(
                args.dataset,
                args.data_root,
                args.layout,
                first_index=args.first_index,
                last_index=args.last_index,
                omit_ok=args.omit_ok,
            ),
            end="",
        )
    except ValueError as error:
        raise SystemExit(str(error)) from error


def _escape_cell(value: str) -> str:
    """Escape one Markdown table cell.

    Arguments:
        value: cell text
    Returns:
        escaped cell text
    """
    return value.replace("\n", "<br>").replace("|", "\\|")


def _format_review_cell(
    *,
    number: int,
    change: ReviewChange | None,
    reviewed: Mapping[int, SrtEvent],
    include_unchanged: bool,
) -> str:
    """Format one review table cell.

    Arguments:
        number: subtitle number
        change: review change, if present
        reviewed: reviewed events for this script
        include_unchanged: whether to include unchanged counterpart text
    Returns:
        formatted review text
    """
    if change is not None:
        return f"{change.original}\n{change.revised}"
    if include_unchanged:
        return reviewed[number].text
    return ""


def _get_notes(
    *,
    number: int,
    hans_change: ReviewChange | None,
    hant_change: ReviewChange | None,
    final_pair: tuple[str, str] | None,
    hans_review: Mapping[int, SrtEvent],
    hant_review: Mapping[int, SrtEvent],
    hans_final: Mapping[int, SrtEvent],
    hant_final: Mapping[int, SrtEvent],
) -> str:
    """Get the default Notes value for one table row.

    The script is intentionally conservative; it does not infer review correctness
    and always returns a non-empty default note to keep the output tabular.

    Arguments:
        number: subtitle number
        hans_change: optional Hans review change
        hant_change: optional Hant review change
        final_pair: optional final Hans-vs-simplified-Hant difference
        hans_review: reviewed Hans events
        hant_review: reviewed Hant events
        hans_final: final Hans events
        hant_final: final Hant events
    Returns:
        non-empty default note
    """
    hans_review_event = hans_review[number]
    hant_review_event = hant_review[number]
    hans_final_event = hans_final[number]
    hant_final_event = hant_final[number]
    hans_post_simplification_change = (
        hans_review_event.text != hans_final_event.text
        and (
            ReviewChange(
                original=hans_review_event.text,
                revised=hans_final_event.text,
            )
        )
        or None
    )
    hant_post_simplification_change = (
        hant_review_event.text != hant_final_event.text
        and (
            ReviewChange(
                original=hant_review_event.text,
                revised=hant_final_event.text,
            )
        )
        or None
    )

    if final_pair is not None:
        final_change = (
            f"{_format_note_text(final_pair[0])} vs {_format_note_text(final_pair[1])}"
        )
        if hans_change is None and hant_change is None:
            note = f"No review edits, but the finals still differ: {final_change}"
        elif hans_change is None:
            assert hant_change is not None
            note = (
                "Only Hant changed "
                f"({_format_change_summary(hant_change)}); "
                f"Hans stayed {_format_note_text(hans_review[number].text)}; "
                f"finals still differ: {final_change}"
            )
        elif hant_change is None:
            note = (
                "Only Hans changed "
                f"({_format_change_summary(hans_change)}); "
                f"Hant stayed {_format_note_text(hant_review[number].text)}; "
                f"finals still differ: {final_change}"
            )
        else:
            note = (
                "Both sides changed, but the finals still differ: "
                f"Hans {_format_change_summary(hans_change)}; "
                f"Hant {_format_change_summary(hant_change)}; "
                f"finals {final_change}"
        )
    else:
        changes = tuple(
            change for change in (hans_change, hant_change) if change is not None
        )
        post_simplification_changes = tuple(
            change
            for change in (
                hans_post_simplification_change,
                hant_post_simplification_change,
            )
            if change is not None
        )
        if not changes or all(_is_ok_cantonese_edit(change) for change in changes):
            if not changes and not post_simplification_changes:
                note = "OK"
            elif not changes and len(post_simplification_changes) == 1:
                post_change = post_simplification_changes[0]
                if post_change is hans_post_simplification_change:
                    note = (
                        "Only Hans changed during post-simplification review "
                        f"({hans_change_summary if False else _format_change_summary(hans_post_simplification_change)})"
                    )
                else:
                    note = (
                        "Only Hant changed during post-simplification review "
                        f"({hant_change_summary if False else _format_change_summary(hant_post_simplification_change)})"
                    )
            else:
                note = "OK"
        elif hans_change is not None and hant_change is not None:
            note = (
                "Both sides made the matching edit: "
                f"Hans {_format_change_summary(hans_change)}; "
                f"Hant {_format_change_summary(hant_change)}"
            )
        elif hans_change is not None:
            if hant_post_simplification_change is not None:
                note = (
                    f"Only Hans changed during initial review "
                    f"({_format_change_summary(hans_change)}); "
                    "Hant changed during post-simplification review: "
                    f"{_format_change_summary(hant_post_simplification_change)}"
                )
            else:
                note = (
                    f"Only Hans changed ({_format_change_summary(hans_change)}); "
                    f"Hant stayed {_format_note_text(hant_review[number].text)}"
                )
        else:
            assert hant_change is not None
            if hans_post_simplification_change is not None:
                note = (
                    f"Only Hant changed during initial review "
                    f"({_format_change_summary(hant_change)}); "
                    "Hans changed during post-simplification review: "
                    f"{_format_change_summary(hans_post_simplification_change)}"
                )
            else:
                note = (
                    f"Only Hant changed ({_format_change_summary(hant_change)}); "
                    f"Hans stayed {_format_note_text(hans_review[number].text)}"
                )
    return note


def _is_ok_cantonese_edit(change: ReviewChange) -> bool:
    """Return whether a review change is an accepted Cantonese edit.

    Arguments:
        change: review change to inspect
    Returns:
        whether the change can be explained by known-good Cantonese replacements
    """
    return _has_only_ok_replacement_edits(change) or _is_ok_spacing_cleanup(
        change.original,
        change.revised,
    )


def _has_only_ok_replacement_edits(change: ReviewChange) -> bool:
    """Return whether all changed spans are accepted replacement edits.

    Arguments:
        change: review change to inspect
    Returns:
        whether every changed span is an accepted replacement
    """
    edits = _get_text_edits(change.original, change.revised)
    return bool(edits) and all(
        tag == "replace" and _is_ok_replacement_span(original, revised)
        for tag, original, revised in edits
    )


def _is_ok_replacement_span(original: str, revised: str) -> bool:
    """Return whether one changed span contains only accepted replacements.

    Arguments:
        original: original changed span
        revised: revised changed span
    Returns:
        whether the changed span contains only accepted replacements
    """
    original_idx = 0
    revised_idx = 0
    while original_idx < len(original) or revised_idx < len(revised):
        matched_replacement = False
        if (
            original_idx < len(original)
            and revised_idx < len(revised)
            and original[original_idx] == revised[revised_idx]
        ):
            original_idx += 1
            revised_idx += 1
            continue
        for source, target in _OK_CANTONESE_REPLACEMENTS_BY_SOURCE_LENGTH:
            if original.startswith(source, original_idx) and revised.startswith(
                target,
                revised_idx,
            ):
                original_idx += len(source)
                revised_idx += len(target)
                matched_replacement = True
                break
        if not matched_replacement:
            return False
    return True


def _is_ok_spacing_cleanup(original: str, revised: str) -> bool:
    """Return whether a change is a clear OCR whitespace cleanup.

    Arguments:
        original: original text
        revised: revised text
    Returns:
        whether the change only repairs whitespace in otherwise matching text
    """
    if _strip_whitespace(original) != _strip_whitespace(revised):
        return False
    return any(char.isascii() and char.isalpha() for char in original + revised)


def _get_text_edits(original: str, revised: str) -> tuple[tuple[str, str, str], ...]:
    """Get non-equal edit spans between two strings.

    Arguments:
        original: original text
        revised: revised text
    Returns:
        non-equal edit spans
    """
    matcher = SequenceMatcher(None, original, revised, autojunk=False)
    opcodes = matcher.get_opcodes()
    return tuple(
        (tag, original[original_start:original_end], revised[revised_start:revised_end])
        for tag, original_start, original_end, revised_start, revised_end in opcodes
        if tag != "equal"
    )


def _format_change_summary(change: ReviewChange) -> str:
    """Format one text edit for a human-readable table note.

    Arguments:
        change: review change to summarize
    Returns:
        human-readable edit summary
    """
    edits = _get_text_edits(change.original, change.revised)
    if len(edits) != 1:
        original = _format_note_text(change.original)
        revised = _format_note_text(change.revised)
        return f"{original} -> {revised}"

    tag, original, revised = edits[0]
    if tag == "insert":
        return f"inserted {_format_note_text(revised)}"
    if tag == "delete":
        return f"removed {_format_note_text(original)}"
    return f"{_format_note_text(original)} -> {_format_note_text(revised)}"


def _format_note_text(value: str, max_length: int = 32) -> str:
    """Format one text value for a human-readable table note.

    Arguments:
        value: text value to format
        max_length: maximum text length before truncation
    Returns:
        formatted text value
    """
    normalized = _collapse_whitespace(value).strip().replace("`", "'")
    if len(normalized) > max_length:
        normalized = f"{normalized[: max_length - 3]}..."
    return f"`{normalized}`"


def _collapse_whitespace(value: str) -> str:
    """Collapse all whitespace to a canonical single space."""
    return re.sub(r"\s+", " ", value)


def _strip_whitespace(value: str) -> str:
    """Remove all whitespace from text."""
    return re.sub(r"\s+", "", value)


def _get_audit_paths(
    dataset_name: str,
    data_root_path: Path,
    layout: str,
) -> AuditPaths:
    """Get input/output paths for one audit layout.

    Arguments:
        dataset_name: dataset name under `test/data`
        data_root_path: root path containing dataset directories
        layout: dataset layout, either auto, ocr, or non-ocr
    Returns:
        audit paths and validation groups
    Raises:
        ValueError: if layout cannot be resolved
    """
    dataset_dir_path = data_root_path / dataset_name
    input_dir_path = dataset_dir_path / "input"
    output_dir_path = dataset_dir_path / "output"
    if layout == "auto":
        if (output_dir_path / "yue-Hans_ocr").is_dir():
            layout = "ocr"
        elif (output_dir_path / "yue-Hans").is_dir():
            layout = "non-ocr"
        else:
            raise ValueError(f"Unable to infer Yue layout for dataset {dataset_name}")

    if layout == "ocr":
        hans_dir_path = output_dir_path / "yue-Hans_ocr"
        hant_dir_path = output_dir_path / "yue-Hant_ocr"
        labels = (
            "yue-Hans source",
            "yue-Hans review",
            "yue-Hans final",
            "yue-Hant source",
            "yue-Hant review",
            "yue-Hant final simplified review",
        )
        return AuditPaths(
            layout="ocr",
            hans_dir_path=hans_dir_path,
            hant_dir_path=hant_dir_path,
            hans_original_path=hans_dir_path / "fuse_clean_validate.srt",
            hans_review_path=hans_dir_path / "fuse_clean_validate_review.srt",
            hans_final_path=hans_dir_path / "fuse_clean_validate_review_flatten.srt",
            hant_original_path=hant_dir_path / "fuse_clean_validate.srt",
            hant_review_path=hant_dir_path / "fuse_clean_validate_review.srt",
            hant_final_path=(
                hant_dir_path / "fuse_clean_validate_review_flatten_simplify_review.srt"
            ),
            timing_groups=(labels,),
            context_lines=(
                f"- yue-Hans image index: {hans_dir_path / 'image' / 'index.html'}",
                f"- yue-Hant image index: {hant_dir_path / 'image' / 'index.html'}",
            ),
        )

    if layout == "non-ocr":
        hans_dir_path = output_dir_path / "yue-Hans"
        hant_dir_path = output_dir_path / "yue-Hant"
        return AuditPaths(
            layout="non-ocr",
            hans_dir_path=hans_dir_path,
            hant_dir_path=hant_dir_path,
            hans_original_path=input_dir_path / "yue-Hans.srt",
            hans_review_path=hans_dir_path / "clean_review.srt",
            hans_final_path=hans_dir_path / "clean_review_flatten_timewarp.srt",
            hant_original_path=input_dir_path / "yue-Hant.srt",
            hant_review_path=hant_dir_path / "clean_review.srt",
            hant_final_path=hant_dir_path
            / "clean_review_flatten_timewarp_simplify_review.srt",
            timing_groups=(
                ("yue-Hans source", "yue-Hans review"),
                ("yue-Hant source", "yue-Hant review"),
                ("yue-Hans final", "yue-Hant final simplified review"),
            ),
            context_lines=(
                "- image indexes: not applicable; source subtitles are not OCR",
                f"- yue-Hans output directory: {hans_dir_path}",
                f"- yue-Hant output directory: {hant_dir_path}",
            ),
        )

    raise ValueError(f"Unsupported layout: {layout}")


def _get_index_range_context_lines(
    first_index: int | None,
    last_index: int | None,
) -> tuple[str, ...]:
    """Get summary context lines for an optional 1-indexed subtitle range.

    Arguments:
        first_index: first 1-indexed subtitle number to include, inclusive
        last_index: last 1-indexed subtitle number to include, inclusive
    Returns:
        summary context lines
    """
    if first_index is None and last_index is None:
        return ()
    if first_index is None:
        return (f"- subtitle range: 1-indexed numbers through {last_index}",)
    if last_index is None:
        return (f"- subtitle range: 1-indexed numbers from {first_index}",)
    return (f"- subtitle range: 1-indexed numbers {first_index} through {last_index}",)


def _get_review_changes(
    original: Mapping[int, SrtEvent],
    reviewed: Mapping[int, SrtEvent],
) -> dict[int, ReviewChange]:
    """Get review changes.

    Arguments:
        original: original events
        reviewed: reviewed events
    Returns:
        review changes keyed by subtitle number
    """
    return _get_text_changes(
        original,
        reviewed,
        lambda original_text, revised_text: ReviewChange(
            original=original_text,
            revised=revised_text,
        ),
    )


def _get_text_differences(
    one: Mapping[int, SrtEvent], two: Mapping[int, SrtEvent]
) -> dict[int, tuple[str, str]]:
    """Get text differences between two event mappings.

    Arguments:
        one: first event mapping
        two: second event mapping
    Returns:
        text differences keyed by subtitle number
    """
    return _get_text_changes(one, two, lambda one_text, two_text: (one_text, two_text))


def _get_text_changes[T](
    one: Mapping[int, SrtEvent],
    two: Mapping[int, SrtEvent],
    factory: Callable[[str, str], T],
) -> dict[int, T]:
    """Get changed text values between two event mappings.

    Arguments:
        one: first event mapping
        two: second event mapping
        factory: function that builds one change value
    Returns:
        changed text values keyed by subtitle number
    """
    changes: dict[int, T] = {}
    for number in sorted(set(one) & set(two)):
        one_text = one[number].text
        two_text = two[number].text
        if one_text != two_text:
            changes[number] = factory(one_text, two_text)
    return changes


def _validate_counts_and_timing(
    series_by_label: Mapping[str, Mapping[int, SrtEvent]],
    timing_groups: Sequence[Sequence[str]],
) -> None:
    """Validate that all audited SRT files share subtitle numbers and timings.

    Arguments:
        series_by_label: event mappings keyed by display label
        timing_groups: label groups within which timings must match
    Raises:
        ValueError: if subtitle numbers or timings differ
    """
    labels = list(series_by_label)
    reference_label = labels[0]
    reference = series_by_label[reference_label]
    reference_numbers = set(reference)
    errors: list[str] = []
    for label in labels[1:]:
        events = series_by_label[label]
        numbers = set(events)
        missing_numbers = sorted(reference_numbers - numbers)
        extra_numbers = sorted(numbers - reference_numbers)
        if missing_numbers:
            errors.append(
                f"{label} is missing subtitles present in {reference_label}: "
                f"{_format_mismatch_numbers(missing_numbers)}"
            )
        if extra_numbers:
            errors.append(
                f"{label} has extra subtitles not present in {reference_label}: "
                f"{_format_mismatch_numbers(extra_numbers)}"
            )
    for group in timing_groups:
        group_labels = list(group)
        group_reference_label = group_labels[0]
        group_reference = series_by_label[group_reference_label]
        group_reference_numbers = set(group_reference)
        for label in group_labels[1:]:
            events = series_by_label[label]
            timing_mismatches = [
                number
                for number in sorted(group_reference_numbers & set(events))
                if group_reference[number].timing != events[number].timing
            ]
            if timing_mismatches:
                errors.append(
                    f"{label} timing differs from {group_reference_label}: "
                    f"{_format_mismatch_numbers(timing_mismatches)}"
                )
    if errors:
        raise ValueError(
            "Subtitle count/timing validation failed:\n"
            + "\n".join(f"- {error}" for error in errors)
        )


def _validate_index_range(first_index: int | None, last_index: int | None) -> None:
    """Validate inclusive 1-indexed subtitle range bounds.

    Arguments:
        first_index: first 1-indexed subtitle number to include, inclusive
        last_index: last 1-indexed subtitle number to include, inclusive
    Raises:
        ValueError: if either bound is invalid
    """
    if first_index is not None and first_index < 1:
        raise ValueError("--first-index must be a positive 1-indexed subtitle number")
    if last_index is not None and last_index < 1:
        raise ValueError("--last-index must be a positive 1-indexed subtitle number")
    if first_index is not None and last_index is not None and first_index > last_index:
        raise ValueError("--first-index must be less than or equal to --last-index")


def _format_mismatch_numbers(numbers: Sequence[int]) -> str:
    """Format mismatch subtitle numbers compactly.

    Arguments:
        numbers: subtitle numbers
    Returns:
        formatted subtitle numbers
    """
    if len(numbers) <= 20:
        return ", ".join(str(number) for number in numbers)
    displayed_numbers = ", ".join(str(number) for number in numbers[:20])
    return f"{displayed_numbers}, ... ({len(numbers)} total)"


if __name__ == "__main__":
    main()
