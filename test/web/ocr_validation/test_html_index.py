#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR validation web HTML index persistence."""

from __future__ import annotations

from pathlib import Path

from pytest import raises

from scinoephile.image.subtitles import ImageSeries
from scinoephile.web.ocr_validation.html_index import (
    load_html_entries,
    update_html_entry_text,
)
from test.helpers.ocr_validation import make_ocr_html_dir


def test_load_html_entries_reads_existing_export(tmp_path: Path):
    """Test loading subtitle entries from existing image subtitle HTML."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="old<br />text")

    entries = load_html_entries(html_dir_path)

    assert len(entries) == 1
    assert entries[0].index == 1
    assert entries[0].start == 1000
    assert entries[0].end == 2000
    assert entries[0].image_name == "0001.png"
    assert entries[0].text == "old\\Ntext"


def test_update_html_entry_text_rewrites_index_compatibly(tmp_path: Path):
    """Test updating one subtitle text in an OCR image HTML index."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="old")

    update_html_entry_text(html_dir_path, 0, "new\\Nline")

    html_text = (html_dir_path / "index.html").read_text(encoding="utf-8")
    assert "<a id='sub-1' href='#sub-1'>#1</a>:" in html_text
    assert "subtitle-number-1" not in html_text
    assert "style=" not in html_text
    assert "new<br />line" in html_text
    output = ImageSeries.load(html_dir_path)
    assert output.events[0].text == "new\\Nline"


def test_update_html_entry_text_does_not_touch_png(tmp_path: Path):
    """Test updating OCR text does not rewrite subtitle image files."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="old")
    image_path = html_dir_path / "0001.png"
    original_image_bytes = image_path.read_bytes()

    update_html_entry_text(html_dir_path, 0, "new")

    assert image_path.read_bytes() == original_image_bytes


def test_update_html_entry_text_rejects_negative_index(tmp_path: Path):
    """Test updating OCR text rejects negative subtitle indexes."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="old")

    with raises(IndexError, match="Subtitle index out of range: -1"):
        update_html_entry_text(html_dir_path, -1, "new")


def test_update_html_entry_text_rejects_out_of_range_index(tmp_path: Path):
    """Test updating OCR text rejects out-of-range subtitle indexes."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="old")

    with raises(IndexError, match="Subtitle index out of range: 1"):
        update_html_entry_text(html_dir_path, 1, "new")
