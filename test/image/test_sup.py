#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of SUP subtitle loading."""

from __future__ import annotations

import pytest

from scinoephile.image.subtitles import ImageSeries
from scinoephile.testing import skip_if_ci, test_data_root


@pytest.mark.parametrize(
    "relative_path",
    [
        skip_if_ci()("mlamd/input/eng.sup"),
        skip_if_ci()("mlamd/input/zho-Hans.sup"),
        skip_if_ci()("mlamd/input/zho-Hant.sup"),
    ],
)
def test_sup_load(relative_path: str):
    """Test loading SUP image subtitles.

    Arguments:
        relative_path: relative path to the sup file
    """
    path = test_data_root / relative_path
    series = ImageSeries.load(path)

    assert len(series) > 0
    for event in series:
        assert event.start >= 0
        assert event.end >= event.start
        assert event.img.mode == "RGBA"
        assert event.img.size[0] > 0
        assert event.img.size[1] > 0
