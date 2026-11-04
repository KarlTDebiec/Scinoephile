#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of SUP subtitle parsing."""

from __future__ import annotations

import numpy as np
from pytest import raises

from scinoephile.image.subtitles.sup import read_sup_image_array, read_sup_series


def test_read_sup_image_array_rejects_row_overflow():
    """Test SUP image RLE data cannot exceed the declared row width."""
    data = np.array([0x00, 0x02], dtype=np.uint8)

    with raises(ValueError, match="declared row width"):
        read_sup_image_array(data, height=1, width=1)


def test_read_sup_series_composes_multiple_objects_at_relative_positions():
    """Retain every referenced object and the transparent space between them."""
    data = _sup_stream(
        _presentation_segment(1, objects=[(3, 10, 20, None), (7, 14, 23, None)]),
        [(3, np.ones((2, 3), dtype=np.uint8)), (7, np.full((1, 2), 2, dtype=np.uint8))],
    )

    starts, ends, images = read_sup_series(data)

    assert starts == [1.0]
    assert ends == [2.0]
    assert images[0].shape == (4, 6, 4)
    expected_alpha = np.zeros((4, 6), dtype=np.uint8)
    expected_alpha[:2, :3] = 255
    expected_alpha[3, 4:] = 255
    np.testing.assert_array_equal(images[0][:, :, 3], expected_alpha)
    assert np.all(images[0][:2, :3, :3] == 128)
    assert np.all(images[0][3, 4:, :3] == 64)


def test_read_sup_series_crops_objects_before_screen_placement():
    """Apply source crops while retaining destination placement between objects."""
    pixels = np.array([[1, 2, 3], [3, 2, 1]], dtype=np.uint8)
    data = _sup_stream(
        _presentation_segment(
            1, objects=[(1, 10, 20, (1, 0, 2, 2)), (2, 13, 22, None)]
        ),
        [(1, pixels), (2, np.ones((1, 1), dtype=np.uint8))],
    )

    _, _, images = read_sup_series(data)

    assert images[0].shape == (3, 4, 4)
    np.testing.assert_array_equal(images[0][:2, :2, 0], [[64, 192], [64, 128]])
    assert images[0][2, 3, 0] == 128
    assert np.count_nonzero(images[0][:, :, 3]) == 5


def test_read_sup_series_keeps_transparent_pixels_from_erasing_prior_objects():
    """Overlay transparent and partially opaque objects over earlier pixels."""
    data = _sup_stream(
        _presentation_segment(1, objects=[(1, 10, 20, None), (2, 10, 20, None)]),
        [(1, np.ones((1, 2), dtype=np.uint8)), (2, np.array([[0, 2]], dtype=np.uint8))],
        alpha=128,
    )

    _, _, images = read_sup_series(data)

    np.testing.assert_array_equal(images[0][0, :, 0], [128, 96])
    np.testing.assert_array_equal(images[0][0, :, 3], [255, 255])


def test_read_sup_series_rejects_crop_outside_object_bounds():
    """Reject source crop rectangles that extend beyond their referenced object."""
    data = _sup_stream(
        _presentation_segment(1, objects=[(1, 10, 20, (2, 0, 2, 1))]),
        [(1, np.ones((1, 3), dtype=np.uint8))],
    )

    with raises(ValueError, match="crop exceeds image bounds"):
        read_sup_series(data)


def test_read_sup_series_rejects_missing_object_reference():
    """Do not substitute an unrelated decoded image for an undefined object ID."""
    data = _sup_stream(
        _presentation_segment(1, objects=[(9, 0, 0, None)]),
        [(1, np.ones((1, 3), dtype=np.uint8))],
    )

    with raises(ValueError, match="undefined image object"):
        read_sup_series(data)


def test_read_sup_series_rejects_placement_outside_video_bounds():
    """Reject positions that would allocate a canvas outside the video dimensions."""
    data = _sup_stream(
        _presentation_segment(1, objects=[(1, 1919, 0, None)]),
        [(1, np.ones((1, 3), dtype=np.uint8))],
    )

    with raises(ValueError, match="placement exceeds video bounds"):
        read_sup_series(data)


def test_read_sup_series_rejects_truncated_composition_crop():
    """Validate all crop fields before reading the presentation object table."""
    composition = _presentation_segment(1, objects=[(1, 0, 0, (0, 0, 1, 1))])
    data = np.frombuffer(_sup_segment(90000, 0x16, composition[:-1]), dtype=np.uint8)

    with raises(ValueError, match="object crop is truncated"):
        read_sup_series(data)


def test_read_sup_series_rejects_truncated_composition_reference():
    """Validate every referenced object's fixed fields before reading them."""
    composition = _presentation_segment(1, objects=[(1, 0, 0, None)])
    data = np.frombuffer(_sup_segment(90000, 0x16, composition[:-1]), dtype=np.uint8)

    with raises(ValueError, match="object reference is truncated"):
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

    with raises(ValueError, match="palette segment is truncated"):
        read_sup_series(data)


def test_read_sup_series_rejects_truncated_segment_data():
    """Test SUP segments cannot declare more bytes than are available."""
    data = np.array(
        [0x50, 0x47, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x99, 0x00, 0x04],
        dtype=np.uint8,
    )

    with raises(ValueError, match="segment data is truncated"):
        read_sup_series(data)


def test_read_sup_series_resets_objects_at_epoch_boundaries():
    """Reject references to objects from an earlier epoch after an epoch start."""
    data = np.frombuffer(
        _display_set(
            _presentation_segment(1, objects=[(1, 0, 0, None)]),
            [(1, np.ones((1, 3), dtype=np.uint8))],
        )
        + _display_set(
            _presentation_segment(2, objects=[(1, 0, 0, None)], state=0x80),
            [],
            timestamp=180000,
        ),
        dtype=np.uint8,
    )

    with raises(ValueError, match="undefined image object"):
        read_sup_series(data)


def test_read_sup_series_reuses_objects_by_id_across_compositions():
    """A later display may select an earlier object without retransmitting its data."""
    data = np.frombuffer(
        _display_set(
            _presentation_segment(1, objects=[(1, 20, 30, None)]),
            [
                (1, np.ones((2, 3), dtype=np.uint8)),
                (2, np.full((1, 2), 2, dtype=np.uint8)),
            ],
        )
        + _display_set(
            _presentation_segment(2, objects=[(2, 40, 50, None)]), [], timestamp=180000
        )
        + _display_set(_presentation_segment(3), [], timestamp=270000),
        dtype=np.uint8,
    )

    starts, ends, images = read_sup_series(data)

    assert starts == [1.0, 2.0]
    assert ends == [2.0, 3.0]
    assert [image.shape for image in images] == [(2, 3, 4), (1, 2, 4)]
    assert np.all(images[0][:, :, :3] == 128)
    assert np.all(images[1][:, :, :3] == 64)


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


def _display_set(
    composition: bytes,
    objects: list[tuple[int, np.ndarray]],
    *,
    timestamp: int = 90000,
    alpha: int = 255,
) -> bytes:
    """Build a display set with simple palette-index images.

    Arguments:
        composition: presentation composition payload
        objects: object IDs and decoded palette-index images
        timestamp: display timestamp in 90 kHz units
        alpha: opacity of the second palette entry
    Returns:
        complete display set bytes
    """
    segments = [
        _sup_segment(timestamp, 0x16, composition),
        _sup_segment(
            timestamp,
            0x14,
            b"\x00\x00\x01\x80\x80\x80\xff\x02\x40\x80\x80"
            + bytes([alpha])
            + b"\x03\xc0\x80\x80\xff",
        ),
    ]
    for object_id, pixels in objects:
        rle = bytearray()
        for row in pixels:
            for color in row:
                if color == 0:
                    rle.extend(b"\x00\x01")
                else:
                    rle.append(int(color))
            rle.extend(b"\x00\x00")
        payload = (
            object_id.to_bytes(2, "big")
            + b"\x00\xc0"
            + (len(rle) + 4).to_bytes(3, "big")
            + pixels.shape[1].to_bytes(2, "big")
            + pixels.shape[0].to_bytes(2, "big")
            + rle
        )
        segments.append(_sup_segment(timestamp, 0x15, payload))
    segments.append(_sup_segment(timestamp, 0x80, b""))
    return b"".join(segments)


def _presentation_segment(
    composition_number: int,
    object_count: int = 0,
    *,
    objects: list[tuple[int, int, int, tuple[int, int, int, int] | None]] | None = None,
    state: int = 0,
) -> bytes:
    """Build a minimal presentation composition segment.

    Arguments:
        composition_number: presentation composition number
        object_count: number of referenced objects
        objects: explicit object IDs, screen positions, and optional crop rectangles
        state: composition state flag
    Returns:
        presentation composition payload bytes
    """
    payload = bytearray(11)
    payload[:2] = (1920).to_bytes(2, "big")
    payload[2:4] = (1080).to_bytes(2, "big")
    payload[5:7] = composition_number.to_bytes(2, "big")
    payload[7] = state
    if objects is None:
        objects = [(object_id, 0, 0, None) for object_id in range(object_count)]
    payload[10] = len(objects)
    for object_id, x, y, crop in objects:
        payload.extend(object_id.to_bytes(2, "big"))
        flags = 0
        if crop is not None:
            flags = 0x80
        payload.extend(bytes([0, flags]))
        payload.extend(x.to_bytes(2, "big") + y.to_bytes(2, "big"))
        if crop is not None:
            for value in crop:
                payload.extend(value.to_bytes(2, "big"))
    return bytes(payload)


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


def _sup_stream(
    composition: bytes, objects: list[tuple[int, np.ndarray]], *, alpha: int = 255
) -> np.ndarray:
    """Build a single subtitle followed by a clear composition.

    Arguments:
        composition: presentation composition payload
        objects: object IDs and decoded palette-index images
        alpha: opacity of the second palette entry
    Returns:
        complete SUP stream bytes as a NumPy array
    """
    return np.frombuffer(
        _display_set(composition, objects, alpha=alpha)
        + _display_set(_presentation_segment(2), [], timestamp=180000),
        dtype=np.uint8,
    )
