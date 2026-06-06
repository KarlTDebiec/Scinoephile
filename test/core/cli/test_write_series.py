#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of shared subtitle-series CLI output helpers."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.core.cli import write_series
from scinoephile.core.subtitles import Series, Subtitle


def test_write_series_defaults_to_srt_format(tmp_path: Path):
    """Test subtitle output helper writes SRT by default.

    Arguments:
        tmp_path: temporary test directory
    """
    parser = ArgumentParser(prog="test")
    series = Series(events=[Subtitle(start=1000, end=2000, text="recognized")])
    outfile_path = tmp_path / "recognized.ass"

    write_series(parser, series, outfile_path, overwrite=True)

    output_text = outfile_path.read_text(encoding="utf-8")
    assert output_text.startswith("1\n00:00:01,000 --> 00:00:02,000\n")
    assert "[Script Info]" not in output_text
