#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for SubtitleSeries."""
from __future__ import annotations

from scinoephile.common import package_root
from scinoephile.common.file import get_temp_file_path
from scinoephile.core import SubtitleSeries

subtitles_0 = package_root.parent / "test" / "data" / "subtitles_0.srt"


def test_subtitle_series():
    subtitles = SubtitleSeries.load(subtitles_0)
    assert len(subtitles) == 5

    # Assert that all lines have text
    for subtitle in subtitles:
        assert subtitle.text
        assert subtitle.text.strip()

    with get_temp_file_path(".srt") as temp_file_path:
        subtitles.save(temp_file_path)
        assert temp_file_path.exists()
        assert temp_file_path.stat().st_size > 0
