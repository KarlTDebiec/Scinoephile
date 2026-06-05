#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""HTML index persistence for OCR image subtitle validation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape, unescape
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
    entries = []
    for match in _entry_pattern().finditer(html_text):
        raw_text = match.group("text") or ""
        text = unescape(raw_text.replace("<br />", "\n")).replace("\n", "\\N")
        entries.append(
            HtmlSubtitleEntry(
                index=int(match.group("index")),
                start=ImageSeries._parse_html_time(match.group("start")),
                end=ImageSeries._parse_html_time(match.group("end")),
                image_name=match.group("img"),
                text=text,
            )
        )

    if not entries:
        raise ScinoephileError(
            f"No subtitle entries found in HTML file for {dir_path}."
        )
    return entries


def update_html_entry_text(dir_path: Path, sub_idx: int, text: str):
    """Update one subtitle text entry in an OCR image HTML directory.

    Arguments:
        dir_path: directory containing index.html and subtitle images
        sub_idx: zero-based subtitle index to update
        text: replacement subtitle text using ASS newline escapes
    """
    entries = load_html_entries(dir_path)
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
    html_lines = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '   <meta charset="UTF-8" />',
        "   <title>Subtitle images</title>",
        "   <style>",
        "      img {",
        "         image-rendering: pixelated;",
        "         image-rendering: crisp-edges;",
        "      }",
        "   </style>",
        "</head>",
        "<body>",
    ]
    for entry in entries:
        start = ImageSeries._format_html_time(entry.start)
        end = ImageSeries._format_html_time(entry.end)
        line = (
            f"#{entry.index}:{start}->{end}"
            "<div style='text-align:center'>"
            f"<img src='{escape(entry.image_name, quote=True)}' />"
        )
        text = entry.text.replace("\\N", "\n")
        if text.strip():
            html_text = escape(text).replace("\n", "<br />")
            line += (
                "<br />"
                "<div style='font-size:22px; background-color:WhiteSmoke'>"
                f"{html_text}</div>"
            )
        line += "</div><br /><hr />"
        html_lines.append(line)
    html_lines.extend(["</body>", "</html>"])
    (dir_path / "index.html").write_text("\n".join(html_lines), encoding="utf-8")


def _entry_pattern() -> re.Pattern[str]:
    """Regex pattern for image subtitle HTML entries.

    Returns:
        compiled regex pattern
    """
    return re.compile(
        r"#(?P<index>\d+):(?P<start>[^-]+)->(?P<end>[^<]+)"
        r"<div style=['\"]text-align:center['\"]>"
        r"<img src=['\"](?P<img>[^'\"]+)['\"] />"
        r"(?:<br /><div style=['\"]font-size:22px; "
        r"background-color:WhiteSmoke['\"]>(?P<text>.*?)</div>)?"
        r"</div><br /><hr />",
        re.DOTALL,
    )
