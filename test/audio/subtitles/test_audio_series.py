#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.subtitles.series."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from pydub.exceptions import CouldntDecodeError

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core import ScinoephileError


def test_audio_series_load_wraps_input_path_errors(tmp_path: Path):
    """Test audio subtitle loading path errors are user-facing.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    input_path = tmp_path / "missing"

    with pytest.raises(
        ScinoephileError,
        match="Unable to load AudioSeries from .*missing",
    ) as excinfo:
        AudioSeries.load(input_path)

    assert isinstance(excinfo.value.__cause__, OSError)


def test_audio_series_load_wraps_decode_errors(tmp_path: Path):
    """Test audio subtitle loading decode errors are user-facing.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    input_path = tmp_path / "input"
    input_path.mkdir()
    (input_path / "input.srt").write_text(
        "1\n00:00:01,000 --> 00:00:02,000\nText\n", encoding="utf-8"
    )
    (input_path / "input.wav").touch()

    with patch(
        "scinoephile.audio.subtitles.series.AudioSegment.from_wav",
        side_effect=CouldntDecodeError("invalid audio"),
    ):
        with pytest.raises(
            ScinoephileError,
            match="Unable to load AudioSeries from .*input: invalid audio",
        ) as excinfo:
            AudioSeries.load(input_path)

    assert isinstance(excinfo.value.__cause__, CouldntDecodeError)
