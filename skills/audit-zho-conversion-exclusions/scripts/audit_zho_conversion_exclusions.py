#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audit Chinese conversion exclusions across subtitle test fixtures."""

from __future__ import annotations

from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from scinoephile.lang.zho.script.conversion import (
    OpenCCConfig,
    get_zho_text_converted,
)

type _KnownExceptionKey = tuple[str, str, str]


_KNOWN_INACTIVE_EXCEPTIONS: set[_KnownExceptionKey] = {
    ("test/data/acopopb/input/zho-Hans.srt", "捱", "388"),
    ("test/data/acopopb/input/zho-Hans.srt", "藉", "673"),
    ("test/data/acopopb/input/zho-Hans.srt", "潚", "517"),
    ("test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt", "藉", "60"),
    ("test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt", "藉", "621"),
    ("test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt", "決", "16"),
    ("test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt", "幫", "261"),
    ("test/data/acopopb/output/zho-Hans_ocr/fuse_clean_validate.srt", "捱", "392"),
    ("test/data/acopopb/output/zho-Hans_ocr/fuse_clean_validate.srt", "藉", "64"),
    ("test/data/acopopb/output/zho-Hans_ocr/fuse_clean_validate.srt", "藉", "679"),
    ("test/data/acopopb/output/zho-Hans_ocr/fuse_clean_validate.srt", "潚", "521"),
    ("test/data/acoptc/input/zho-Hans.srt", "剎", "1213"),
    ("test/data/acoptc/output/yue-Hans_ocr/fuse_clean_validate.srt", "藉", "368"),
    ("test/data/acoptc/output/yue-Hans_ocr/fuse_clean_validate.srt", "決", "326"),
    ("test/data/acoptc/output/zho-Hans_ocr/fuse_clean_validate.srt", "藉", "372"),
    ("test/data/kob/input/yue-Hans.srt", "捱", "1056"),
    ("test/data/kob/input/yue-Hans.srt", "覆", "315"),
    ("test/data/tmm/output/zho-Hant_ocr/fuse_clean_validate.srt", "借", "147"),
    ("test/data/tmm/output/zho-Hant_ocr/fuse_clean_validate.srt", "干", "989"),
    ("test/data/tmm/output/zho-Hant_ocr/fuse_clean_validate.srt", "干", "1036"),
}
"""Known fixture artifacts that should not be reported as unexpected."""


@dataclass(frozen=True)
class _Change:
    """A single character-level conversion change."""

    path: str
    """Repository-relative source subtitle path."""

    subtitle: str
    """Subtitle number where the change was found."""

    original: str
    """Original character or text span."""

    expected: str
    """Converted character or text span."""

    config: OpenCCConfig
    """OpenCC configuration used for the no-op direction check."""


@dataclass(frozen=True)
class _AuditResult:
    """Result of a conversion exclusion audit run."""

    target_count: int
    """Number of subtitle files audited."""

    raw_change_count: int
    """Number of changes found before applying active exclusions."""

    active_expected_count: int
    """Number of raw changes covered by active exclusions."""

    inactive_expected_count: int
    """Number of known inactive exceptions filtered from the report."""

    unexpected_changes: list[_Change]
    """Remaining unexpected changes."""


def main(argv: Sequence[str] | None = None):
    """Run the conversion exclusion audit."""
    args = _parse_args(argv)
    root_path = args.root.resolve()
    result = _audit(root_path)
    print(_get_markdown_report(result, root_path))


def _audit(root_path: Path) -> _AuditResult:
    """Audit conversion changes across all matching subtitle targets.

    Arguments:
        root_path: repository root path
    Returns:
        audit result
    """
    unexpected_changes: list[_Change] = []
    raw_change_count = 0
    post_exclusion_change_count = 0
    inactive_expected_count = 0
    target_paths = _discover_target_paths(root_path)

    for target_path in target_paths:
        relative_path = target_path.relative_to(root_path).as_posix()
        config = _get_config(relative_path)
        for subtitle, text in _parse_srt(target_path.read_text(encoding="utf-8-sig")):
            raw_converted_text = get_zho_text_converted(
                text, config, apply_exclusions=False
            )
            raw_change_count += len(_iter_text_changes(text, raw_converted_text))

            converted_text = get_zho_text_converted(text, config, apply_exclusions=True)
            changes = _iter_text_changes(text, converted_text)
            post_exclusion_change_count += len(changes)
            for original, expected in changes:
                if not original:
                    continue
                change = _Change(relative_path, subtitle, original, expected, config)
                if _is_known_inactive(change):
                    inactive_expected_count += 1
                    continue
                unexpected_changes.append(change)

    active_expected_count = raw_change_count - post_exclusion_change_count
    return _AuditResult(
        target_count=len(target_paths),
        raw_change_count=raw_change_count,
        active_expected_count=active_expected_count,
        inactive_expected_count=inactive_expected_count,
        unexpected_changes=unexpected_changes,
    )


def _describe_change(change: _Change) -> str:
    """Describe a change in report-ready prose.

    Arguments:
        change: change to describe
    Returns:
        description
    """
    if change.config is OpenCCConfig.s2t:
        return (
            f"Simplified `{change.original}` in Hant no-op check; "
            f"expected `{change.expected}`"
        )
    return (
        f"Traditional `{change.original}` in Hans no-op check; "
        f"expected `{change.expected}`"
    )


def _discover_target_paths(root_path: Path) -> list[Path]:
    """Discover all regular and OCR/PCR subtitle targets.

    Arguments:
        root_path: repository root path
    Returns:
        sorted subtitle paths
    """
    data_dir_path = root_path / "test" / "data"
    targets: list[Path] = []
    for file_path in data_dir_path.rglob("*.srt"):
        if _is_regular_target(file_path):
            targets.append(file_path)
            continue
        if _is_ocr_target(file_path):
            targets.append(file_path)
    return sorted(targets, key=lambda path: path.relative_to(root_path).as_posix())


def _get_config(relative_path: str) -> OpenCCConfig:
    """Get the no-op direction conversion config for a fixture path.

    Arguments:
        relative_path: repository-relative fixture path
    Returns:
        OpenCC configuration
    """
    if "-Hant" in relative_path:
        return OpenCCConfig.s2t
    return OpenCCConfig.t2s


def _get_image_dump_path(change_path: Path, root_path: Path) -> Path | None:
    """Get the image dump corresponding to a fixture path, if available.

    Arguments:
        change_path: repository-relative fixture path
        root_path: repository root path
    Returns:
        image dump path, if present
    """
    if change_path.name == "fuse_clean_validate.srt":
        image_path = root_path / change_path.parent / "image" / "index.html"
        if image_path.exists():
            return image_path
        return None

    if change_path.parent.name == "input":
        series = change_path.parts[2]
        language = change_path.stem
        image_path = (
            root_path
            / "test"
            / "data"
            / series
            / "output"
            / f"{language}_ocr"
            / "image"
            / "index.html"
        )
        if image_path.exists():
            return image_path
    return None


def _get_link(label: str, file_path: Path) -> str:
    """Get a Markdown link to a local file.

    Arguments:
        label: link label
        file_path: local file path
    Returns:
        Markdown link
    """
    return f"[{label}]({file_path.as_posix()})"


def _get_markdown_report(result: _AuditResult, root_path: Path) -> str:
    """Get the Markdown audit report.

    Arguments:
        result: audit result
        root_path: repository root path
    Returns:
        Markdown report
    """
    lines = [
        (
            f"Audited {result.target_count} targets. "
            f"Raw changes: {result.raw_change_count}. "
            f"Covered by active exclusions: {result.active_expected_count}. "
            f"Covered by known inactive exceptions: {result.inactive_expected_count}. "
            f"Unexpected: {len(result.unexpected_changes)}."
        ),
        "",
    ]
    if result.unexpected_changes:
        lines.extend(
            _get_unexpected_changes_table(result.unexpected_changes, root_path)
        )
    else:
        lines.append("No unexpected changes.")
    return "\n".join(lines)


def _get_source_label(change_path: Path) -> str:
    """Get a compact fixture label.

    Arguments:
        change_path: repository-relative fixture path
    Returns:
        compact fixture label
    """
    series = change_path.parts[2].upper()
    if change_path.name == "fuse_clean_validate.srt":
        language = change_path.parent.name.removesuffix("_ocr")
    else:
        language = change_path.stem
    return f"{series} {language}"


def _get_unexpected_changes_table(changes: list[_Change], root_path: Path) -> list[str]:
    """Get the unexpected changes Markdown table.

    Arguments:
        changes: unexpected changes
        root_path: repository root path
    Returns:
        Markdown table lines
    """
    lines = [
        "| Source | Image dump | Character | Expected | Subtitle | Note |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    lines.extend(
        _get_unexpected_changes_table_row(change, root_path) for change in changes
    )
    return lines


def _get_unexpected_changes_table_row(change: _Change, root_path: Path) -> str:
    """Get one unexpected changes Markdown table row.

    Arguments:
        change: unexpected change
        root_path: repository root path
    Returns:
        Markdown table row
    """
    change_path = Path(change.path)
    source_label = _get_source_label(change_path)
    source_link = _get_link(source_label, root_path / change_path)
    image_path = _get_image_dump_path(change_path, root_path)
    if image_path is None:
        image_link = ""
    else:
        image_link = _get_link("image", image_path)
    return (
        f"| {source_link} | {image_link} | `{change.original}` | "
        f"`{change.expected}` | {change.subtitle} | {_describe_change(change)} |"
    )


def _is_known_inactive(change: _Change) -> bool:
    """Check whether a change is a known inactive exception.

    Arguments:
        change: change to check
    Returns:
        whether the change is expected as an inactive fixture artifact
    """
    key = (change.path, change.original, change.subtitle)
    return key in _KNOWN_INACTIVE_EXCEPTIONS


def _is_ocr_target(file_path: Path) -> bool:
    """Check whether a path is an OCR/PCR fixture target.

    Arguments:
        file_path: file path to check
    Returns:
        whether the path should be audited
    """
    if file_path.name != "fuse_clean_validate.srt":
        return False
    if not file_path.parent.name.endswith("_ocr"):
        return False
    language = file_path.parent.name.split("_", 1)[0]
    return language in {"yue-Hans", "yue-Hant", "zho-Hans", "zho-Hant"}


def _is_regular_target(file_path: Path) -> bool:
    """Check whether a path is a regular source subtitle target.

    Arguments:
        file_path: file path to check
    Returns:
        whether the path should be audited
    """
    if file_path.parent.name != "input":
        return False
    return file_path.name in {
        "yue-Hans.srt",
        "yue-Hant.srt",
        "zho-Hans.srt",
        "zho-Hant.srt",
    }


def _iter_text_changes(original: str, converted: str) -> list[tuple[str, str]]:
    """Get changed text spans between original and converted text.

    Arguments:
        original: original text
        converted: converted text
    Returns:
        changed original and converted spans
    """
    changes: list[tuple[str, str]] = []
    matcher = SequenceMatcher(a=original, b=converted, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        old_text = original[i1:i2]
        new_text = converted[j1:j2]
        if len(old_text) == len(new_text):
            changes.extend(zip(old_text, new_text, strict=True))
            continue
        changes.append((old_text, new_text))
    return changes


def _parse_args(argv: Sequence[str] | None = None) -> Namespace:
    """Parse command-line arguments.

    Arguments:
        argv: command-line arguments
    Returns:
        parsed arguments
    """
    parser = ArgumentParser(
        description="Audit Chinese conversion exclusions across subtitle test fixtures."
    )
    parser.add_argument(
        "--root",
        default=Path.cwd(),
        type=Path,
        help="Repository root path. Defaults to the current working directory.",
    )
    return parser.parse_args(argv)


def _parse_srt(text: str) -> list[tuple[str, str]]:
    """Parse SRT text into subtitle number and subtitle text pairs.

    Arguments:
        text: SRT content
    Returns:
        subtitle number and text pairs
    """
    normalized_text = text.replace("\ufeff", "")
    normalized_text = normalized_text.replace("\r\n", "\n").replace("\r", "\n")
    blocks = [block for block in normalized_text.split("\n\n") if block.strip()]
    events: list[tuple[str, str]] = []
    for block in blocks:
        lines = block.split("\n")
        if not lines:
            continue
        subtitle = lines[0].strip()
        if len(lines) >= 2 and "-->" in lines[1]:
            text_lines = lines[2:]
        else:
            text_lines = lines[1:]
        events.append((subtitle, "\n".join(text_lines)))
    return events


if __name__ == "__main__":
    main()
