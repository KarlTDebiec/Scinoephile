#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit Yue direct reviews and final simplified-Hant comparison in one table."""

from __future__ import annotations

import argparse
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "AuditPaths",
    "ReviewChange",
    "SrtEvent",
    "audit_dataset",
    "format_markdown",
    "main",
    "parse_args",
    "parse_srt",
]


@dataclass(frozen=True)
class AuditPaths:
    """Paths and validation rules for one Yue dual-review audit.

    Attributes:
        layout: input/output layout name
        hans_dir_path: yue-Hans output directory
        hant_dir_path: yue-Hant output directory
        hans_original_path: yue-Hans direct-review input path
        hans_review_path: yue-Hans direct-review output path
        hans_final_path: final yue-Hans comparison path
        hant_original_path: yue-Hant direct-review input path
        hant_review_path: yue-Hant direct-review output path
        hant_final_path: final simplified yue-Hant comparison path
        timing_groups: labels to validate for matching timings
        context_lines: extra summary context lines
    """

    layout: str
    """Input/output layout name."""

    hans_dir_path: Path
    """Yue-Hans output directory."""

    hant_dir_path: Path
    """Yue-Hant output directory."""

    hans_original_path: Path
    """Yue-Hans direct-review input path."""

    hans_review_path: Path
    """Yue-Hans direct-review output path."""

    hans_final_path: Path
    """Final yue-Hans comparison path."""

    hant_original_path: Path
    """Yue-Hant direct-review input path."""

    hant_review_path: Path
    """Yue-Hant direct-review output path."""

    hant_final_path: Path
    """Final simplified yue-Hant comparison path."""

    timing_groups: tuple[tuple[str, ...], ...]
    """Labels to validate for matching timings."""

    context_lines: tuple[str, ...]
    """Extra summary context lines."""


@dataclass(frozen=True)
class ReviewChange:
    """One direct block-review change.

    Attributes:
        original: original validated subtitle text
        revised: reviewed subtitle text
    """

    original: str
    """Original validated subtitle text."""

    revised: str
    """Reviewed subtitle text."""


@dataclass(frozen=True)
class SrtEvent:
    """One SRT event parsed without normalizing text.

    Attributes:
        number: subtitle number
        timing: raw timing line
        text: raw subtitle text
    """

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
) -> str:
    """Audit one Yue dataset and return a Markdown report.

    Arguments:
        dataset_name: dataset name under `test/data`
        data_root_path: root path containing dataset directories
        layout: dataset layout, either auto, ocr, or non-ocr
    Returns:
        Markdown report
    """
    paths = _get_audit_paths(dataset_name, data_root_path, layout)

    hans_original = parse_srt(paths.hans_original_path)
    hans_review = parse_srt(paths.hans_review_path)
    hans_final = parse_srt(paths.hans_final_path)

    hant_original = parse_srt(paths.hant_original_path)
    hant_review = parse_srt(paths.hant_review_path)
    hant_final = parse_srt(paths.hant_final_path)

    _validate_counts_and_timing(
        {
            "yue-Hans source": hans_original,
            "yue-Hans direct review": hans_review,
            "yue-Hans final": hans_final,
            "yue-Hant source": hant_original,
            "yue-Hant direct review": hant_review,
            "yue-Hant final simplified review": hant_final,
        },
        paths.timing_groups,
    )

    hans_changes = _get_review_changes(hans_original, hans_review)
    hant_changes = _get_review_changes(hant_original, hant_review)
    final_differences = _get_text_differences(hans_final, hant_final)

    return format_markdown(
        dataset_name=dataset_name,
        layout=paths.layout,
        hans_dir_path=paths.hans_dir_path,
        hant_dir_path=paths.hant_dir_path,
        context_lines=paths.context_lines,
        hans_original=hans_original,
        hans_review=hans_review,
        hans_final=hans_final,
        hant_original=hant_original,
        hant_review=hant_review,
        hant_final=hant_final,
        hans_changes=hans_changes,
        hant_changes=hant_changes,
        final_differences=final_differences,
    )


def format_markdown(
    *,
    dataset_name: str,
    layout: str,
    hans_dir_path: Path,
    hant_dir_path: Path,
    context_lines: Sequence[str],
    hans_original: Mapping[int, SrtEvent],
    hans_review: Mapping[int, SrtEvent],
    hans_final: Mapping[int, SrtEvent],
    hant_original: Mapping[int, SrtEvent],
    hant_review: Mapping[int, SrtEvent],
    hant_final: Mapping[int, SrtEvent],
    hans_changes: Mapping[int, ReviewChange],
    hant_changes: Mapping[int, ReviewChange],
    final_differences: Mapping[int, tuple[str, str]],
) -> str:
    """Format an audit report as Markdown.

    Arguments:
        dataset_name: dataset name
        layout: input/output layout name
        hans_dir_path: yue-Hans output directory
        hant_dir_path: yue-Hant output directory
        context_lines: extra summary context lines
        hans_original: yue-Hans original validated subtitles
        hans_review: yue-Hans reviewed subtitles
        hans_final: final yue-Hans subtitles
        hant_original: yue-Hant original validated subtitles
        hant_review: yue-Hant reviewed subtitles
        hant_final: final simplified yue-Hant subtitles
        hans_changes: yue-Hans direct review changes by subtitle number
        hant_changes: yue-Hant direct review changes by subtitle number
        final_differences: final text differences by subtitle number
    Returns:
        Markdown report
    """
    changed_numbers = sorted(
        set(hans_changes) | set(hant_changes) | set(final_differences)
    )
    lines = [
        f"# {dataset_name} Yue Review Dual",
        "",
        "## Summary",
        "",
        f"- yue-Hans direct review count: {len(hans_original)} -> {len(hans_review)}",
        f"- yue-Hant direct review count: {len(hant_original)} -> {len(hant_review)}",
        f"- final yue-Hans / simplified yue-Hant count: "
        f"{len(hans_final)} / {len(hant_final)}",
        f"- yue-Hans direct review changes: {len(hans_changes)}",
        f"- yue-Hant direct review changes: {len(hant_changes)}",
        f"- final text differences: {len(final_differences)}",
        f"- layout: {layout}",
        "- subtitle counts: aligned across all audited SRT files",
        "- timings: aligned within comparable source/review and final groups",
        f"- table rows: {len(changed_numbers)}",
        *context_lines,
        "",
        "## Audit Table",
        "",
        "| Subtitle | yue-Hans | yue-Hant | yue-Hans vs Hant->Hans | Notes |",
        "|---:|---|---|---|---|",
    ]
    for number in changed_numbers:
        hans_change = hans_changes.get(number)
        hant_change = hant_changes.get(number)
        include_unchanged_review_text = bool(hans_change or hant_change)
        final_pair = final_differences.get(number)
        if final_pair is None:
            final_cell = ""
        else:
            final_cell = _format_pair(*final_pair)
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_cell(_format_subtitle_cell(number)),
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
                    _escape_cell(
                        _get_notes(
                            number=number,
                            hans_change=hans_change,
                            hant_change=hant_change,
                            final_pair=final_pair,
                        )
                    ),
                ]
            )
            + " |"
        )
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


def main(argv: Sequence[str] | None = None):
    """Run the Yue review dual audit.

    Arguments:
        argv: optional argument sequence
    """
    args = parse_args(argv)
    try:
        print(audit_dataset(args.dataset, args.data_root, args.layout), end="")
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
    """Format one direct review table cell.

    Arguments:
        number: subtitle number
        change: review change, if present
        reviewed: reviewed events for this script
        include_unchanged: whether to include unchanged counterpart text
    Returns:
        formatted direct review text
    """
    if change is not None:
        return _format_pair(change.original, change.revised)
    if include_unchanged:
        return reviewed[number].text
    return ""


def _format_pair(one: str, two: str) -> str:
    """Format two pieces of text as a stacked table cell.

    Arguments:
        one: first text
        two: second text
    Returns:
        stacked text
    """
    return f"{one}\n{two}"


def _get_notes(  # noqa: PLR0911
    *,
    number: int,
    hans_change: ReviewChange | None,
    hant_change: ReviewChange | None,
    final_pair: tuple[str, str] | None,
) -> str:
    """Get the default Notes value for one table row.

    The script is intentionally conservative; it does not infer review correctness
    and always returns a non-empty default note to keep the output tabular.

    Arguments:
        number: subtitle number
        hans_change: optional Hans direct-review change
        hant_change: optional Hant direct-review change
        final_pair: optional final Hans-vs-simplified-Hant difference
    Returns:
        non-empty default note
    """
    _ = number
    if final_pair is not None:
        hans_final, hant_final = final_pair
        final_change = _describe_diff(hans_final, hant_final)
        if hans_change is None and hant_change is None:
            return (
                f"final mismatch only ({final_change}); "
                "verify expected variant/simplification behavior before accepting"
            )
        if hans_change is None:
            hans_review_change = _describe_diff(
                hant_change.original, hant_change.revised
            )
            return (
                "Hant direct-review changed only "
                f"({hans_review_change}); decide whether Hans should mirror"
                f" this {hans_review_change} in direct review"
            )
        if hant_change is None:
            hant_review_change = _describe_diff(
                hans_change.original, hans_change.revised
            )
            return (
                "Hans direct-review changed only "
                f"({hant_review_change}); decide whether Hant should mirror"
                f" this {hant_review_change} in direct review"
            )
        if hans_change.revised == hant_change.revised:
            return (
                "both tracks corrected identically in review, but final diff remains "
                f"({final_change}); likely a conversion/simplification issue"
            )
        return (
            "both tracks changed in review differently "
            "and disagree; reconcile direct-review values before trusting final result"
        )
    if hans_change is not None and hant_change is not None:
        if hans_change.revised == hant_change.revised:
            review_change = _describe_diff(hans_change.original, hans_change.revised)
            return (
                "both tracks corrected consistently in review"
                f" ({review_change}); check once against image evidence"
            )
        hans_review_change = _describe_diff(hans_change.original, hans_change.revised)
        hant_review_change = _describe_diff(hant_change.original, hant_change.revised)
        return (
            "direct-review inconsistency"
            f" (Hans: {hans_review_change} / Hant: {hant_review_change});"
            " choose one consistent correction"
        )
    if hans_change is not None:
        review_change = _describe_diff(hans_change.original, hans_change.revised)
        return (
            "single-track direct review (Hans only)"
            f" ({review_change}); confirm if a Hant mirror is required"
        )
    if hant_change is not None:
        review_change = _describe_diff(hant_change.original, hant_change.revised)
        return (
            "single-track direct review (Hant only)"
            f" ({review_change}); confirm if a Hans mirror is required"
        )
    return "correct"


def _describe_diff(one: str, two: str) -> str:
    """Describe a pair of text values at a high level for notes.

    Arguments:
        one: first text
        two: second text
    Returns:
        short change description
    """
    if one == two:
        return "no change"
    if _collapse_whitespace(one) == _collapse_whitespace(two):
        return "spacing-only change"
    if _strip_punctuation(_collapse_whitespace(one)) == _strip_punctuation(
        _collapse_whitespace(two)
    ):
        if _contains_whitespace(one) and _contains_whitespace(two):
            return "spacing + punctuation"
        return "punctuation-only change"
    if _strip_whitespace(one) == _strip_whitespace(two):
        return "line-wrap/pacing difference"
    return "character/word change"


def _contains_whitespace(value: str) -> bool:
    """Return whether text contains whitespace characters."""
    return any(char.isspace() for char in value)


def _collapse_whitespace(value: str) -> str:
    """Collapse all whitespace to a canonical single space."""
    return re.sub(r"\s+", " ", value)


def _strip_punctuation(value: str) -> str:
    """Remove punctuation-like characters for a lightweight diff signature."""
    return re.sub(r"[.,!?;:，。？！；：、、“”『』《》「」()（）【】]", "", value)


def _strip_whitespace(value: str) -> str:
    """Remove whitespace for a lightweight diff signature."""
    return re.sub(r"\s+", "", value)


def _format_subtitle_cell(number: int) -> str:
    """Format subtitle number.

    Arguments:
        number: subtitle number
    Returns:
        formatted subtitle cell
    """
    return str(number)


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
            "yue-Hans direct review",
            "yue-Hans final",
            "yue-Hant source",
            "yue-Hant direct review",
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
            hans_review_path=hans_dir_path / "review.srt",
            hans_final_path=hans_dir_path / "timewarp_clean_flatten.srt",
            hant_original_path=input_dir_path / "yue-Hant.srt",
            hant_review_path=hant_dir_path / "review.srt",
            hant_final_path=hant_dir_path
            / "timewarp_clean_flatten_simplify_review.srt",
            timing_groups=(
                ("yue-Hans source", "yue-Hans direct review"),
                ("yue-Hant source", "yue-Hant direct review"),
                ("yue-Hans final", "yue-Hant final simplified review"),
            ),
            context_lines=(
                "- image indexes: not applicable; source subtitles are not OCR",
                f"- yue-Hans output directory: {hans_dir_path}",
                f"- yue-Hant output directory: {hant_dir_path}",
            ),
        )

    raise ValueError(f"Unsupported layout: {layout}")


def _get_review_changes(
    original: Mapping[int, SrtEvent],
    reviewed: Mapping[int, SrtEvent],
) -> dict[int, ReviewChange]:
    """Get direct review changes.

    Arguments:
        original: original events
        reviewed: reviewed events
    Returns:
        review changes keyed by subtitle number
    """
    changes: dict[int, ReviewChange] = {}
    for number in sorted(set(original) & set(reviewed)):
        original_text = original[number].text
        reviewed_text = reviewed[number].text
        if original_text == reviewed_text:
            continue
        changes[number] = ReviewChange(
            original=original_text,
            revised=reviewed_text,
        )
    return changes


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
    differences: dict[int, tuple[str, str]] = {}
    for number in sorted(set(one) & set(two)):
        one_text = one[number].text
        two_text = two[number].text
        if one_text != two_text:
            differences[number] = (one_text, two_text)
    return differences


def _validate_counts_and_timing(
    series_by_label: Mapping[str, Mapping[int, SrtEvent]],
    timing_groups: Sequence[Sequence[str]],
):
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
