#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of HTML image subtitle loading and saving."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core.testing import test_data_root
from scinoephile.image.subtitles import ImageSeries


def test_html_image_series_load():
    """Test loading HTML image subtitles."""
    path = test_data_root / "mlamd/output/eng_image"
    series = ImageSeries.load(path)

    assert len(series) > 0

    first_event = series[0]
    assert first_event.start == 48792
    assert first_event.end == 51125
    assert first_event.text == "yat"

    sixth_event = series[5]
    assert sixth_event.start == 67083
    assert sixth_event.end == 70042
    assert sixth_event.text == ""

    for event in series[:3]:
        assert event.img.size[0] > 0
        assert event.img.size[1] > 0


def test_html_image_series_save(tmp_path: Path):
    """Test saving HTML image subtitles.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    source_path = test_data_root / "mlamd/output/eng_image"
    series = ImageSeries.load(source_path)
    output_dir = tmp_path / "eng_image"

    series.save(output_dir)

    html_path = output_dir / "index.html"
    assert html_path.exists()

    html_text = html_path.read_text(encoding="utf-8")
    assert "#1:48,792->51,125" in html_text
    assert "<img src='0001.png' />" in html_text
    assert "background-color:WhiteSmoke'>yat</div>" in html_text

    sixth_line = next(line for line in html_text.splitlines() if line.startswith("#6:"))
    assert "WhiteSmoke" not in sixth_line

    png_files = sorted(output_dir.glob("*.png"))
    assert len(png_files) == len(series)
