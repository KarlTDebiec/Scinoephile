#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.image.subtitles.series."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from pytest import FixtureRequest, param, raises

from scinoephile.common.file import get_temp_directory_path
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.bbox import Bbox
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle
from test.helpers import parametrize


@parametrize(
    "input_path_fixture, expected_event_count, expected_first_size",
    [
        param(
            "mlamd_eng_ocr_sup_path",
            942,
            (953, 63),
            id="mlamd-eng-sup",
        ),
    ],
)
def test_load_sup(
    input_path_fixture: str,
    expected_event_count: int,
    expected_first_size: tuple[int, int],
    request: FixtureRequest,
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


@parametrize(
    "input_path_fixture, expected_event_count, expected_first_size",
    [
        param(
            "mlamd_eng_image_path",
            942,
            (953, 63),
            id="mlamd-eng-html",
        ),
    ],
)
def test_load_html(
    input_path_fixture: str,
    expected_event_count: int,
    expected_first_size: tuple[int, int],
    request: FixtureRequest,
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


def test_load_html_rejects_image_path_outside_directory(tmp_path: Path):
    """Test HTML image paths cannot escape the subtitle directory.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    input_dir_path = tmp_path / "subtitles"
    input_dir_path.mkdir()
    outside_path = tmp_path / "outside.png"
    Image.new("RGBA", (2, 2), (255, 255, 255, 255)).save(outside_path)
    html_text = ImageSeries.format_html_entry(
        index=1,
        start=0,
        end=1000,
        image_name="../outside.png",
        text="",
    )
    (input_dir_path / "index.html").write_text(html_text, encoding="utf-8")

    with raises(
        ScinoephileError,
        match="Unable to load ImageSeries.*single contained filename",
    ):
        ImageSeries.load(input_dir_path)


def test_load_rejects_unsupported_input_file(tmp_path: Path):
    """Test unsupported image subtitle input files raise user-facing errors.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    input_path = tmp_path / "subtitles.txt"
    input_path.write_text("not image subtitles", encoding="utf-8")

    with raises(ScinoephileError, match="directory containing one index.html"):
        ImageSeries.load(input_path)


def test_image_series_load_wraps_input_path_errors(tmp_path: Path):
    """Test image subtitle loading path errors are user-facing.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    input_path = tmp_path / "missing"

    with raises(
        ScinoephileError,
        match="Unable to load ImageSeries from .*missing",
    ) as excinfo:
        ImageSeries.load(input_path)

    assert isinstance(excinfo.value.__cause__, OSError)


def test_copy_text_from_mutates_image_subtitle_texts():
    """Test copying text from a text series mutates image subtitles in place."""
    image_subtitle = ImageSubtitle(
        start=1000,
        end=2000,
        img=Image.new("LA", (2, 2), (0, 255)),
        bboxes=[Bbox(0, 1, 2, 3)],
        text="old",
    )
    image_series = ImageSeries(events=[image_subtitle])
    text_series = Series(events=[Subtitle(start=1100, end=2100, text="new")])

    image_series.copy_text_from(text_series)

    assert image_series.events[0] is image_subtitle
    assert image_series.events[0].start == 1000
    assert image_series.events[0].end == 2000
    assert image_series.events[0].text == "new"
    assert image_series.events[0].bboxes == [Bbox(0, 1, 2, 3)]


def test_copy_text_from_rejects_length_mismatch():
    """Test copying text rejects length mismatches."""
    image_series = ImageSeries(
        events=[
            ImageSubtitle(
                start=1000,
                end=2000,
                img=Image.new("LA", (2, 2), (0, 255)),
            )
        ]
    )
    text_series = Series(
        events=[
            Subtitle(start=1000, end=2000, text="one"),
            Subtitle(start=3000, end=4000, text="two"),
        ]
    )

    with raises(ScinoephileError, match="Length mismatch: 2 vs 1"):
        image_series.copy_text_from(text_series)


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
        assert '<html lang="">' in html_text
        assert "<a id='sub-1' href='#sub-1'>#1</a>:" in html_text
        assert "subtitle-number-1" not in html_text
        assert "style=" not in html_text
        assert "class=" not in html_text
        assert "image-rendering: pixelated;" in html_text
        assert "image-rendering: crisp-edges;" not in html_text
        assert "body > div {" in html_text
        assert "<div><img src='0001.png' />" in html_text
        assert "<br /><div>recognized</div>" in html_text
        assert "<img src='0001.png' />" in html_text

        png_files = sorted(output_path.glob("*.png"))
        assert len(png_files) == len(tiny_image_series)


def test_load_html_accepts_subtitle_number_anchor(tiny_image_series: ImageSeries):
    """Test loading HTML image subtitles with subtitle number anchors.

    Arguments:
        tiny_image_series: small image subtitle series
    """
    with get_temp_directory_path() as output_dir:
        output_path = output_dir / "image_subtitles"
        tiny_image_series.save(output_path)

        output = ImageSeries.load(output_path)

        assert len(output) == len(tiny_image_series)
        assert output.events[0].text == tiny_image_series.events[0].text


def test_image_series_save_wraps_output_path_errors(
    tiny_image_series: ImageSeries, tmp_path: Path
):
    """Test image subtitle saving path errors are user-facing.

    Arguments:
        tiny_image_series: small image subtitle series
        tmp_path: pytest temporary directory path
    """
    output_path = tmp_path / "image_output"
    output_path.touch()

    with raises(
        ScinoephileError,
        match="Unable to save ImageSeries to .*image_output",
    ) as excinfo:
        tiny_image_series.save(output_path)

    assert isinstance(excinfo.value.__cause__, OSError)


def test_series_fill_and_outline_colors():
    """Test fill and outline colors are detected at the image series level."""
    img = Image.new("LA", (3, 3), (0, 255))
    img.putpixel((1, 1), (255, 255))
    series = ImageSeries(events=[ImageSubtitle(start=0, end=1000, img=img)])

    assert series.fill_color == 255
    assert series.outline_color == 0


def test_text_font_size_defaults_when_no_bboxes():
    """Test text font size falls back when no bboxes are present."""
    series = ImageSeries(
        events=[
            ImageSubtitle(
                start=0,
                end=1000,
                img=Image.new("LA", (4, 4), (255, 255)),
                bboxes=[],
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


def test_text_font_size_uses_upper_weighted_useful_bbox_height():
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


def test_text_font_size_uses_ascender_height_for_latin_bboxes():
    """Test Latin text size favors ascenders over lowercase x-height."""
    series = ImageSeries(
        events=[
            ImageSubtitle(
                start=0,
                end=1000,
                img=Image.new("LA", (2, 2), (255, 255)),
                bboxes=[
                    Bbox(0, 10, 0, 29),
                    Bbox(12, 22, 0, 29),
                    Bbox(24, 34, 0, 29),
                    Bbox(36, 46, 0, 39),
                    Bbox(48, 58, 0, 39),
                ],
            ),
        ]
    )

    assert series.text_font_size == 39
