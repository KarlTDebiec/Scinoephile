#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR validation web HTML index persistence."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from pytest import raises

from scinoephile.image.subtitles import ImageSeries
from scinoephile.web.ocr_validation.html_index import (
    load_html_entries,
    update_html_entry_text,
)


def test_load_html_entries_reads_existing_export(tmp_path: Path):
    """Test loading subtitle entries from existing image subtitle HTML."""
    html_dir_path = _make_html_dir(tmp_path, text="old<br />text")

    entries = load_html_entries(html_dir_path)

    assert len(entries) == 1
    assert entries[0].index == 1
    assert entries[0].start == 1000
    assert entries[0].end == 2000
    assert entries[0].image_name == "0001.png"
    assert entries[0].text == "old\\Ntext"


def test_update_html_entry_text_rewrites_index_compatibly(tmp_path: Path):
    """Test updating one subtitle text in an OCR image HTML index."""
    html_dir_path = _make_html_dir(tmp_path, text="old")

    update_html_entry_text(html_dir_path, 0, "new\\Nline")

    html_text = (html_dir_path / "index.html").read_text(encoding="utf-8")
    assert "new<br />line" in html_text
    output = ImageSeries.load(html_dir_path)
    assert output.events[0].text == "new\\Nline"


def test_update_html_entry_text_does_not_touch_png(tmp_path: Path):
    """Test updating OCR text does not rewrite subtitle image files."""
    html_dir_path = _make_html_dir(tmp_path, text="old")
    image_path = html_dir_path / "0001.png"
    original_image_bytes = image_path.read_bytes()

    update_html_entry_text(html_dir_path, 0, "new")

    assert image_path.read_bytes() == original_image_bytes


def test_update_html_entry_text_rejects_negative_index(tmp_path: Path):
    """Test updating OCR text rejects negative subtitle indexes."""
    html_dir_path = _make_html_dir(tmp_path, text="old")

    with raises(IndexError, match="Subtitle index out of range: -1"):
        update_html_entry_text(html_dir_path, -1, "new")


def test_update_html_entry_text_rejects_out_of_range_index(tmp_path: Path):
    """Test updating OCR text rejects out-of-range subtitle indexes."""
    html_dir_path = _make_html_dir(tmp_path, text="old")

    with raises(IndexError, match="Subtitle index out of range: 1"):
        update_html_entry_text(html_dir_path, 1, "new")


def _make_html_dir(tmp_path: Path, *, text: str) -> Path:
    """Create an OCR image HTML directory.

    Arguments:
        tmp_path: pytest temporary directory path
        text: HTML subtitle text content
    Returns:
        OCR image HTML directory path
    """
    html_dir_path = tmp_path / "image"
    html_dir_path.mkdir()
    Image.new("LA", (2, 2), (255, 255)).save(html_dir_path / "0001.png")
    (html_dir_path / "index.html").write_text(
        "\n".join(
            [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                '   <meta charset="UTF-8" />',
                "   <title>Subtitle images</title>",
                "</head>",
                "<body>",
                "#1:1,000->2,000"
                "<div style='text-align:center'>"
                "<img src='0001.png' />"
                "<br /><div style='font-size:22px; background-color:WhiteSmoke'>"
                f"{text}</div></div><br /><hr />",
                "</body>",
                "</html>",
            ]
        ),
        encoding="utf-8",
    )
    return html_dir_path
