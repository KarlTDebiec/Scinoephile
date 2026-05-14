#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of SUP subtitle parsing."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("numba")

from scinoephile.image.subtitles.sup import read_sup_image_array, read_sup_series


def test_read_sup_image_array_rejects_row_overflow():
    """Test SUP image RLE data cannot exceed the declared row width."""
    data = np.array([0x00, 0x02], dtype=np.uint8)

    with pytest.raises(ValueError, match="declared row width"):
        read_sup_image_array(data, height=1, width=1)


def test_read_sup_series_rejects_truncated_segment_data():
    """Test SUP segments cannot declare more bytes than are available."""
    data = np.array(
        [
            0x50,
            0x47,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x99,
            0x00,
            0x04,
        ],
        dtype=np.uint8,
    )

    with pytest.raises(ValueError, match="segment data is truncated"):
        read_sup_series(data)


def test_read_sup_series_rejects_truncated_palette_entry():
    """Test SUP palette entries cannot contain fewer than five bytes."""
    data = np.array(
        [
            0x50,
            0x47,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x14,
            0x00,
            0x03,
            0x00,
            0x00,
            0x01,
        ],
        dtype=np.uint8,
    )

    with pytest.raises(ValueError, match="palette segment is truncated"):
        read_sup_series(data)
