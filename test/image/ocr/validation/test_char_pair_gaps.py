#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR validation character pair gap data."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from scinoephile.image.ocr.validation.char_pair_gaps import (
    load_char_pair_gaps,
    save_char_pair_gaps,
)


def test_load_char_pair_gaps_rejects_nonmonotonic_cutoffs(tmp_path: Path):
    """Test loading rejects cutoffs that cannot be classified correctly.

    Arguments:
        tmp_path: temporary directory path
    """
    file_path = tmp_path / "char_pair_gaps.csv"
    file_path.write_text("⋯,〝,46,24,90,200\n", encoding="utf-8")

    with pytest.raises(ValueError, match="cutoffs must be monotonic"):
        load_char_pair_gaps(file_path)


def test_repo_char_pair_gaps_have_monotonic_cutoffs():
    """Test repository character pair gap data has ordered cutoffs."""
    file_path = Path(__file__).parents[4] / "scinoephile/data/ocr/char_pair_gaps.csv"

    with file_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for line_no, row in enumerate(reader, start=1):
            if not row:
                continue
            cutoffs = tuple(map(int, row[2:]))
            assert cutoffs == tuple(sorted(cutoffs)), (
                f"{file_path}:{line_no} has non-monotonic cutoffs {cutoffs}"
            )


def test_save_char_pair_gaps_rejects_nonmonotonic_cutoffs(tmp_path: Path):
    """Test saving rejects cutoffs that cannot be classified correctly.

    Arguments:
        tmp_path: temporary directory path
    """
    file_path = tmp_path / "char_pair_gaps.csv"

    with pytest.raises(ValueError, match="cutoffs must be monotonic"):
        save_char_pair_gaps({("⋯", "〝"): (46, 24, 90, 200)}, file_path)

    assert not file_path.exists()
