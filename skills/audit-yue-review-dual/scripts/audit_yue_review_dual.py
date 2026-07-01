#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit Yue reviews and final simplified-Hant comparison in one table."""

from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "AuditPaths",
    "ReviewChange",
    "SrtEvent",
    "audit_dataset",
    "format_markdown",
    "parse_srt",
]

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
) -> str:
    """Audit one Yue dataset and return a Markdown report.

    Arguments:
        dataset_name: dataset name under `test/data`
        data_root_path: root path containing dataset directories
        layout: dataset layout, either auto, ocr, or non-ocr
        first_index: first 1-indexed subtitle number to include, inclusive
        last_index: last 1-indexed subtitle number to include, inclusive
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
        context_lines=_get_index_range_context_lines(first_index, last_index),
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
    )


def format_markdown(
    *,
    dataset_name: str,
    context_lines: Sequence[str],
    series: Mapping[str, Mapping[int, SrtEvent]],
    hans_changes: Mapping[int, ReviewChange],
    hant_changes: Mapping[int, ReviewChange],
    final_differences: Mapping[int, tuple[str, str]],
) -> str:
    """Format an audit report as Markdown.

    Arguments:
        dataset_name: dataset name
        context_lines: extra summary context lines
        series: parsed SRT events keyed by internal series name
        hans_changes: yue-Hans review changes by subtitle number
        hant_changes: yue-Hant review changes by subtitle number
        final_differences: final text differences by subtitle number
    Returns:
        Markdown report
    """
    hans_review = series["hans_review"]
    hans_final = series["hans_final"]
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
                    "",
                ]
            )
            + " |"
        )

    summary_context_lines = list(context_lines)
    lines = [
        f"# {dataset_name} Yue Review Dual",
        "",
        "## Summary",
        "",
        f"- yue-Hans review edits: {len(hans_changes)}",
        f"- yue-Hant review edits: {len(hant_changes)}",
        f"- final text differences: {len(final_differences)}",
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
            hans_original_path=hans_dir_path / "fuse_clean_validate.srt",
            hans_review_path=hans_dir_path / "fuse_clean_validate_review.srt",
            hans_final_path=hans_dir_path / "fuse_clean_validate_review_flatten.srt",
            hant_original_path=hant_dir_path / "fuse_clean_validate.srt",
            hant_review_path=hant_dir_path / "fuse_clean_validate_review.srt",
            hant_final_path=(
                hant_dir_path / "fuse_clean_validate_review_flatten_simplify_review.srt"
            ),
            timing_groups=(labels,),
        )

    if layout == "non-ocr":
        hans_dir_path = output_dir_path / "yue-Hans"
        hant_dir_path = output_dir_path / "yue-Hant"
        return AuditPaths(
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
