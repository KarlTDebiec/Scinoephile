#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.subtitles.series."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.common.file import get_temp_file_path
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from test.helpers import assert_series_equal, test_data_root


def test_series_round_trips_srt():
    """Test loading and saving an SRT series."""
    path = test_data_root / "kob/input/eng.srt"

    series = Series.load(path)
    with get_temp_file_path(".srt") as output_path:
        series.save(output_path)
        output = Series.load(output_path)

    assert_series_equal(output, series)


def test_series_load_wraps_input_path_errors(tmp_path: Path):
    """Test subtitle loading path errors are user-facing.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    path = tmp_path / "missing.srt"

    with pytest.raises(
        ScinoephileError,
        match="Unable to load Series from .*missing.srt",
    ) as excinfo:
        Series.load(path)

    assert isinstance(excinfo.value.__cause__, FileNotFoundError)
