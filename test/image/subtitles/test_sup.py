#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of SUP subtitle parsing."""

from __future__ import annotations

import numpy as np
from pytest import raises

from scinoephile.image.subtitles.sup import read_sup_image_array, read_sup_series


def _sup_segment(timestamp: int, kind: int, payload: bytes) -> bytes:
    """Build one SUP segment for parser tests.

    Arguments:
        timestamp: 90 kHz timestamp
        kind: segment kind
        payload: segment payload bytes
    Returns:
        complete segment bytes
    """
    pts = timestamp.to_bytes(4, "big")
    return b"PG" + pts + pts + bytes([kind]) + len(payload).to_bytes(2, "big") + payload


def _presentation_segment(composition_number: int, object_count: int) -> bytes:
    """Build a minimal presentation composition segment.

    Arguments:
        composition_number: presentation composition number
        object_count: number of referenced objects
    Returns:
        presentation composition payload bytes
    """
    payload = bytearray(11)
    payload[5:7] = composition_number.to_bytes(2, "big")
    payload[10] = object_count
    return bytes(payload)


def test_read_sup_image_array_rejects_row_overflow():
    """Test SUP image RLE data cannot exceed the declared row width."""
    data = np.array([0x00, 0x02], dtype=np.uint8)

    with raises(ValueError, match="declared row width"):
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

    with raises(ValueError, match="segment data is truncated"):
        read_sup_series(data)


def test_read_sup_series_supports_fragmented_image_segments():
    """Test SUP image objects split across multiple segments are assembled."""
    rle_data = b"\x01\x01\x01\x00\x00\x01\x01\x01"
    object_data_length = 4 + len(rle_data)
    first_fragment = rle_data[:3]
    middle_fragment = rle_data[3:5]
    last_fragment = rle_data[5:]
    data = np.frombuffer(
        b"".join(
            [
                _sup_segment(
                    90000,
                    0x16,
                    _presentation_segment(composition_number=1, object_count=1),
                ),
                _sup_segment(90000, 0x14, b"\x00\x00\x01\x80\x80\x80\xff"),
                _sup_segment(
                    90000,
                    0x15,
                    (
                        b"\x00\x00\x00\x80"
                        + object_data_length.to_bytes(3, "big")
                        + b"\x00\x03\x00\x02"
                        + first_fragment
                    ),
                ),
                _sup_segment(90000, 0x15, b"\x00\x00\x00\x00" + middle_fragment),
                _sup_segment(90000, 0x15, b"\x00\x00\x00\x40" + last_fragment),
                _sup_segment(90000, 0x80, b""),
                _sup_segment(
                    180000,
                    0x16,
                    _presentation_segment(composition_number=2, object_count=0),
                ),
                _sup_segment(180000, 0x80, b""),
            ]
        ),
        dtype=np.uint8,
    )

    starts, ends, images = read_sup_series(data)

    assert starts == [1.0]
    assert ends == [2.0]
    assert len(images) == 1
    assert images[0].shape == (2, 3, 4)
    assert np.all(images[0][:, :, 3] == 255)


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

    with raises(ValueError, match="palette segment is truncated"):
        read_sup_series(data)
