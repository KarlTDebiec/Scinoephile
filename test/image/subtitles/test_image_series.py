#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.image.subtitles.series."""

from __future__ import annotations

import pytest

from scinoephile.common.file import get_temp_directory_path
from scinoephile.image.subtitles import ImageBlock, ImageSeries


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
    assert series[0].img.size == expected_first_size
    for event in series:
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
    assert series[0].img.size == expected_first_size
    for event in series:
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


@pytest.mark.parametrize(
    "input_path_fixture",
    [
        "mlamd_eng_sup_path",
        "mlamd_zho_hans_sup_path",
    ],
)
def test_image_blocks(input_path_fixture: str, request: pytest.FixtureRequest):
    """Test ImageBlock functionality.

    Arguments:
        input_path_fixture: sup input path fixture name
        request: pytest fixture request
    """
    input_path = request.getfixturevalue(input_path_fixture)
    series = ImageSeries.load(input_path)

    # Test blocks property returns ImageBlock instances
    blocks = series.blocks
    assert len(blocks) > 0
    assert all(isinstance(block, ImageBlock) for block in blocks)

    # Test that blocks contain the correct subtitles
    for block in blocks:
        assert len(block) > 0
        assert block.start_idx < block.end_idx
        assert block.end_idx <= len(series)

        # Test block iteration
        block_events = list(block)
        assert len(block_events) == len(block)
        assert all(hasattr(event, "img") for event in block_events)

        # Test block indexing
        first_event = block[0]
        assert first_event == series[block.start_idx]
        if len(block) > 1:
            last_event = block[-1]
            assert last_event == series[block.end_idx - 1]

        # Test block time properties
        assert block.start == series[block.start_idx].start
        assert block.end == series[block.end_idx - 1].end
        assert block.start < block.end
