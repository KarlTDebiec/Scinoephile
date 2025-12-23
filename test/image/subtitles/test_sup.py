#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of SUP subtitle loading."""

from __future__ import annotations

import pytest

from scinoephile.core.testing import skip_if_ci
from scinoephile.image.subtitles import ImageSeries


@pytest.mark.parametrize(
    "input_path_fixture, expected_event_count, expected_first_size",
    [
        skip_if_ci()("mlamd_eng_sup_path", 942, (953, 63)),
        skip_if_ci()("mlamd_zho_hans_sup_path", 932, (773, 73)),
        skip_if_ci()("mlamd_zho_hant_sup_path", 932, (775, 73)),
    ],
)
def test_sup_load(
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
        assert event.img.mode == "RGBA"
        assert event.img.size[0] > 0
        assert event.img.size[1] > 0
