#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for scinoephile.core.series."""
from __future__ import annotations

import pytest

from scinoephile.common.file import get_temp_file_path
from scinoephile.core import Series
from scinoephile.testing.file import get_test_file_path


@pytest.mark.parametrize(
    "relative_path",
    [
        "kob/input/en-HK.srt",
        "mnt/input/en-US.srt",
        "t/input/en-HK.srt",
    ],
)
def test_series(relative_path):
    path = get_test_file_path(relative_path)

    series = Series.load(path)
    assert len(series) > 0

    # Assert that all lines have text
    for event in series:
        assert event.text
        assert event.text.strip()

    with get_temp_file_path(".srt") as output_path:
        series.save(output_path)
        assert output_path.exists()
        assert output_path.stat().st_size > 0
