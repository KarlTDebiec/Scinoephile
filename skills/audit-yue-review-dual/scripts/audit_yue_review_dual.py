#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit Yue direct reviews and final simplified-Hant comparison in one table."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "ReviewChange",
    "SrtEvent",
    "audit_dataset",
    "format_markdown",
    "main",
    "parse_args",
    "parse_srt",
]


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


def audit_dataset(dataset_name: str, data_root_path: Path) -> str:
    """Audit one OCR dataset and return a Markdown report.

    Arguments:
        dataset_name: dataset name under `test/data`
        data_root_path: root path containing dataset directories
    Returns:
        Markdown report
    """
    output_dir_path = data_root_path / dataset_name / "output"
    hans_dir_path = output_dir_path / "yue-Hans_ocr"
    hant_dir_path = output_dir_path / "yue-Hant_ocr"

    hans_original = parse_srt(hans_dir_path / "fuse_clean_validate.srt")
    hans_review = parse_srt(hans_dir_path / "fuse_clean_validate_review.srt")
    hans_final = parse_srt(hans_dir_path / "fuse_clean_validate_review_flatten.srt")

    hant_original = parse_srt(hant_dir_path / "fuse_clean_validate.srt")
    hant_review = parse_srt(hant_dir_path / "fuse_clean_validate_review.srt")
    hant_final = parse_srt(
        hant_dir_path / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )

    _validate_counts_and_timing(
        {
            "yue-Hans fuse_clean_validate": hans_original,
            "yue-Hans fuse_clean_validate_review": hans_review,
            "yue-Hans final": hans_final,
            "yue-Hant fuse_clean_validate": hant_original,
            "yue-Hant fuse_clean_validate_review": hant_review,
            "yue-Hant final simplified review": hant_final,
        }
    )

    hans_changes = _get_review_changes(hans_original, hans_review)
    hant_changes = _get_review_changes(hant_original, hant_review)
    final_differences = _get_text_differences(hans_final, hant_final)

    return format_markdown(
        dataset_name=dataset_name,
        hans_dir_path=hans_dir_path,
        hant_dir_path=hant_dir_path,
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
    hans_dir_path: Path,
    hant_dir_path: Path,
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
        hans_dir_path: yue-Hans OCR output directory
        hant_dir_path: yue-Hant OCR output directory
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
        "- subtitle counts and timings: aligned across all audited SRT files",
        f"- table rows: {len(changed_numbers)}",
        f"- yue-Hans image index: {hans_dir_path / 'image' / 'index.html'}",
        f"- yue-Hant image index: {hant_dir_path / 'image' / 'index.html'}",
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
                    "",
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
        print(audit_dataset(args.dataset, args.data_root), end="")
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


def _format_subtitle_cell(number: int) -> str:
    """Format subtitle number and anchor IDs.

    Arguments:
        number: subtitle number
    Returns:
        formatted subtitle cell
    """
    return f"{number} (Hans #subtitle-number-{number} / Hant #subtitle-number-{number})"


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


def _validate_counts_and_timing(series_by_label: Mapping[str, Mapping[int, SrtEvent]]):
    """Validate that all audited SRT files share subtitle numbers and timings.

    Arguments:
        series_by_label: event mappings keyed by display label
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
        timing_mismatches = [
            number
            for number in sorted(reference_numbers & numbers)
            if reference[number].timing != events[number].timing
        ]
        if timing_mismatches:
            errors.append(
                f"{label} timing differs from {reference_label}: "
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
