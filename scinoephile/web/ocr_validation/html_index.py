#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""HTML index persistence for OCR image subtitle validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scinoephile.core import ScinoephileError
from scinoephile.image.subtitles import ImageSeries

__all__ = [
    "HtmlSubtitleEntry",
    "load_html_entries",
    "update_html_entry_text",
    "write_html_entries",
]


@dataclass(frozen=True)
class HtmlSubtitleEntry:
    """Subtitle entry parsed from an OCR image HTML index."""

    index: int
    """One-based subtitle index."""
    start: int
    """Start time in milliseconds."""
    end: int
    """End time in milliseconds."""
    image_name: str
    """Subtitle image file name."""
    text: str
    """Subtitle OCR text using ASS newline escapes."""


def load_html_entries(dir_path: Path) -> list[HtmlSubtitleEntry]:
    """Load subtitle entries from an OCR image HTML directory.

    Arguments:
        dir_path: directory containing index.html and subtitle images
    Returns:
        subtitle entries parsed from the HTML index
    """
    html_path = dir_path / "index.html"
    if not html_path.exists():
        raise ScinoephileError(f"Expected {html_path} to exist.")

    html_text = html_path.read_text(encoding="utf-8")
    html_events = ImageSeries.parse_html_events(html_text, dir_path)
    return [
        HtmlSubtitleEntry(
            index=html_event["index"],
            start=html_event["start"],
            end=html_event["end"],
            image_name=html_event["path"].name,
            text=html_event["text"],
        )
        for html_event in html_events
    ]


def update_html_entry_text(dir_path: Path, sub_idx: int, text: str):
    """Update one subtitle text entry in an OCR image HTML directory.

    Arguments:
        dir_path: directory containing index.html and subtitle images
        sub_idx: zero-based subtitle index to update
        text: replacement subtitle text using ASS newline escapes
    """
    entries = load_html_entries(dir_path)
    if sub_idx < 0 or sub_idx >= len(entries):
        raise IndexError(f"Subtitle index out of range: {sub_idx}")
    old_entry = entries[sub_idx]
    entries[sub_idx] = HtmlSubtitleEntry(
        index=old_entry.index,
        start=old_entry.start,
        end=old_entry.end,
        image_name=old_entry.image_name,
        text=text,
    )
    write_html_entries(dir_path, entries)


def write_html_entries(dir_path: Path, entries: list[HtmlSubtitleEntry]):
    """Rewrite an OCR image HTML index without touching image files.

    Arguments:
        dir_path: directory containing index.html and subtitle images
        entries: subtitle entries to write
    """
    html_lines = ImageSeries.html_header_lines()
    for entry in entries:
        html_lines.append(
            ImageSeries.format_html_entry(
                index=entry.index,
                start=entry.start,
                end=entry.end,
                image_name=entry.image_name,
                text=entry.text,
            )
        )
    html_lines.extend(ImageSeries.html_footer_lines())
    (dir_path / "index.html").write_text("\n".join(html_lines), encoding="utf-8")
