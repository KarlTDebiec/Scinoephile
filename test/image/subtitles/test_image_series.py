#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.image.subtitles.series."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from scinoephile.common.file import get_temp_directory_path
from scinoephile.core import ScinoephileError
from scinoephile.image.bbox import Bbox
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle


@pytest.mark.parametrize(
    "input_path_fixture, expected_event_count, expected_first_size",
    [
        ("mlamd_eng_ocr_sup_path", 942, (953, 63)),
    ],
)
def test_load_sup(
    input_path_fixture: str,
    expected_event_count: int,
    expected_first_size: tuple[int, int],
    request: pytest.FixtureRequest,
):
    """Test loading SUP image subtitles.

    Arguments:
        input_path_fixture: sup input path fixture name
        expected_event_count: expected number of subtitles
        expected_first_size: expected size of first image
        request: pytest fixture request
    """
    input_path = request.getfixturevalue(input_path_fixture)
    series: ImageSeries = ImageSeries.load(input_path)

    assert len(series) == expected_event_count
    assert series.events[0].img.size == expected_first_size
    for event in series.events:
        assert event.start >= 0
        assert event.end >= event.start
        assert event.img.mode == "LA"
        assert event.img.size[0] > 0
        assert event.img.size[1] > 0


@pytest.mark.parametrize(
    "input_path_fixture, expected_event_count, expected_first_size",
    [
        ("mlamd_eng_image_path", 942, (953, 63)),
    ],
)
def test_load_html(
    input_path_fixture: str,
    expected_event_count: int,
    expected_first_size: tuple[int, int],
    request: pytest.FixtureRequest,
):
    """Test loading HTML image subtitles.

    Arguments:
        input_path_fixture: html input path fixture name
        expected_event_count: expected number of subtitles
        expected_first_size: expected size of the first image
        request: pytest fixture request
    """
    path = request.getfixturevalue(input_path_fixture)
    series: ImageSeries = ImageSeries.load(path, encoding="utf-8")

    assert len(series) == expected_event_count
    assert series.events[0].img.size == expected_first_size
    for event in series.events:
        assert event.start >= 0
        assert event.end >= event.start
        assert event.img.size[0] > 0
        assert event.img.size[1] > 0


def test_load_rejects_unsupported_input_file(tmp_path: Path):
    """Test unsupported image subtitle input files raise user-facing errors.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    input_path = tmp_path / "subtitles.txt"
    input_path.write_text("not image subtitles", encoding="utf-8")

    with pytest.raises(ScinoephileError, match="directory containing one index.html"):
        ImageSeries.load(input_path)


def test_save_html(tiny_image_series: ImageSeries):
    """Test saving HTML image subtitles.

    Arguments:
        tiny_image_series: small image subtitle series
    """
    with get_temp_directory_path() as output_dir:
        output_path = output_dir / "image_subtitles"
        tiny_image_series.save(output_path)

        html_path = output_path / "index.html"
        assert html_path.exists()

        html_text = html_path.read_text(encoding="utf-8")
        assert "<img src='0001.png' />" in html_text

        png_files = sorted(output_path.glob("*.png"))
        assert len(png_files) == len(tiny_image_series)


def test_series_fill_and_outline_colors():
    """Test fill and outline colors are detected at the image series level."""
    img = Image.new("LA", (3, 3), (0, 255))
    img.putpixel((1, 1), (255, 255))
    series = ImageSeries(events=[ImageSubtitle(start=0, end=1000, img=img)])

    assert series.fill_color == 255
    assert series.outline_color == 0


def test_text_font_size_defaults_when_no_useful_bboxes():
    """Test text font size falls back when no useful bboxes are present."""
    series = ImageSeries(
        events=[
            ImageSubtitle(
                start=0,
                end=1000,
                img=Image.new("LA", (4, 4), (255, 255)),
                bboxes=[
                    Bbox(0, 4, 0, 16),
                    Bbox(0, 6, 0, 60),
                ],
            )
        ]
    )

    assert series.text_font_size == 50


def test_text_font_size_invalidates_when_events_change():
    """Test cached text font size is invalidated when events change."""
    series = ImageSeries(
        events=[
            ImageSubtitle(
                start=0,
                end=1000,
                img=Image.new("LA", (2, 2), (255, 255)),
                bboxes=[Bbox(0, 10, 0, 52)],
            )
        ]
    )

    assert series.text_font_size == 52

    series.events = [
        ImageSubtitle(
            start=1000,
            end=2000,
            img=Image.new("LA", (3, 3), (255, 255)),
            bboxes=[Bbox(0, 10, 0, 60)],
        )
    ]

    assert series.text_font_size == 60


def test_text_font_size_uses_most_common_useful_bbox_height():
    """Test text font size is detected across the image series."""
    series = ImageSeries(
        events=[
            ImageSubtitle(
                start=0,
                end=1000,
                img=Image.new("LA", (2, 2), (255, 255)),
                bboxes=[
                    Bbox(0, 10, 0, 52),
                    Bbox(0, 4, 0, 10),
                ],
            ),
            ImageSubtitle(
                start=1000,
                end=2000,
                img=Image.new("LA", (3, 3), (255, 255)),
                bboxes=[
                    Bbox(0, 10, 0, 60),
                    Bbox(12, 22, 0, 60),
                ],
            ),
        ]
    )

    assert series.text_font_size == 60
