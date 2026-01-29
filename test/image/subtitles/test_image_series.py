#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.image.subtitles.series."""

from __future__ import annotations

import pytest

from scinoephile.common.file import get_temp_directory_path
from scinoephile.image.subtitles import ImageSeries
from scinoephile.image.subtitles.subtitle import ImageSubtitle


@pytest.mark.parametrize(
    "input_path_fixture, expected_event_count, expected_first_size",
    [
        ("mlamd_eng_sup_path", 942, (953, 63)),
        ("mlamd_zho_hans_sup_path", 932, (773, 73)),
        ("mlamd_zho_hant_sup_path", 932, (775, 73)),
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
    series = ImageSeries.load(input_path)

    assert len(series) == expected_event_count
    first_event: ImageSubtitle = series[0]  # type: ignore[assignment]
    assert first_event.img.size == expected_first_size
    event: ImageSubtitle
    for event in series:  # type: ignore[assignment]
        assert event.start >= 0
        assert event.end >= event.start
        assert event.img.mode == "LA"
        assert event.img.size[0] > 0
        assert event.img.size[1] > 0


@pytest.mark.parametrize(
    "input_path_fixture, expected_event_count, expected_first_size",
    [
        ("mlamd_eng_image_path", 942, (953, 63)),
        ("mlamd_zho_hans_image_path", 932, (773, 73)),
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
    series = ImageSeries.load(path, encoding="utf-8")

    assert len(series) == expected_event_count
    first_event: ImageSubtitle = series[0]  # type: ignore[assignment]
    assert first_event.img.size == expected_first_size
    event: ImageSubtitle
    for event in series:  # type: ignore[assignment]
        assert event.start >= 0
        assert event.end >= event.start
        assert event.img.size[0] > 0
        assert event.img.size[1] > 0


@pytest.mark.parametrize(
    "input_path_fixture, expected_event_count",
    [
        ("mlamd_eng_image_path", 942),
        ("mlamd_zho_hans_image_path", 932),
    ],
)
def test_save_html(
    input_path_fixture: str,
    expected_event_count: int,
    request: pytest.FixtureRequest,
):
    """Test saving HTML image subtitles.

    Arguments:
        input_path_fixture: html input path fixture name
        expected_event_count: expected number of subtitles
        request: pytest fixture request
    """
    source_path = request.getfixturevalue(input_path_fixture)
    series = ImageSeries.load(source_path, encoding="utf-8")
    with get_temp_directory_path() as output_dir:
        output_path = output_dir / "image_subtitles"
        series.save(output_path)

        html_path = output_path / "index.html"
        assert html_path.exists()

        html_text = html_path.read_text(encoding="utf-8")
        assert "<img src='0001.png' />" in html_text

        png_files = sorted(output_path.glob("*.png"))
        assert len(png_files) == expected_event_count
