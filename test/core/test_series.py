#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for scinoephile.core.series."""
from __future__ import annotations

import pytest

from scinoephile.common.file import get_temp_file_path
from scinoephile.core import Series
from scinoephile.testing import get_test_file_path


@pytest.mark.parametrize(
    "relative_input_path",
    [
        "kob/input/en-HK.srt",
        "mnt/input/en-US.srt",
        "t/input/en-HK.srt",
    ],
)
def test_series(relative_input_path: str):
    input_path = get_test_file_path(relative_input_path)

    input_series = Series.load(input_path)
    assert len(input_series) > 0

    # Assert that all lines have text
    for subtitle in input_series:
        assert subtitle.text
        assert subtitle.text.strip()

    with get_temp_file_path(".srt") as temp_file_path:
        input_series.save(temp_file_path)
        assert temp_file_path.exists()
        assert temp_file_path.stat().st_size > 0
