#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.series."""
from __future__ import annotations

import pytest

from scinoephile.common.file import get_temp_file_path
from scinoephile.core import Series
from scinoephile.testing import test_data_root


@pytest.mark.parametrize(
    "relative_path",
    [
        "kob/input/eng.srt",
        "mnt/input/eng.srt",
        "pdp/input/eng.srt",
        "t/input/eng.srt",
    ],
)
def test_series(relative_path):
    path = test_data_root / relative_path

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
