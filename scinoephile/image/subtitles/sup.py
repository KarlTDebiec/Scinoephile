#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to the SUP subtitle format."""

from __future__ import annotations

import numba as nb
import numpy as np

__all__ = ["read_sup_image_array", "read_sup_palette", "read_sup_series"]


@nb.jit(nopython=True, nogil=True, cache=True, fastmath=True)
def read_sup_image_array(  # noqa: PLR0912, PLR0915
    bytes_: np.ndarray, height: int, width: int
) -> np.ndarray:
    """Read a palette-compressed image from a block of bytes.

    Arguments:
        bytes_: block of bytes
        height: height of image
        width: width of image
    Returns:
        compressed image
    Raises:
        ValueError: if a value is invalid
    """
    array = np.zeros((height, width), np.uint8)
    byte_i = 0
    row_i = 0
    col_i = 0
    while byte_i < len(bytes_):
        if row_i >= height:
            raise ValueError("SUP image data extends past declared image height.")
        byte_1 = bytes_[byte_i]
        if byte_1 == 0x00:  # 00 | Special behaviors
            if byte_i + 1 >= len(bytes_):
                raise ValueError("SUP image data ended inside an RLE sequence.")
            byte_2 = bytes_[byte_i + 1]
            if byte_2 == 0x00:  # 00 00 | New line
                byte_i += 2
                row_i += 1
                col_i = 0
            else:
                if (byte_2 & 0xC0) == 0x40:  # 00 4X XX | Color 0, X times
                    if byte_i + 2 >= len(bytes_):
                        raise ValueError("SUP image data ended inside an RLE sequence.")
                    byte_3 = bytes_[byte_i + 2]
                    n_pixels = ((byte_2 - 0x40) << 8) + byte_3
                    color = 0
                    byte_i += 3
                elif (byte_2 & 0xC0) == 0x80:  # 00 8Y XX | Color X,  Y times
                    if byte_i + 2 >= len(bytes_):
                        raise ValueError("SUP image data ended inside an RLE sequence.")
                    byte_3 = bytes_[byte_i + 2]
                    n_pixels = byte_2 - 0x80
                    color = byte_3
                    byte_i += 3
                elif (byte_2 & 0xC0) != 0x00:  # 00 CY YY XX | Color X, Y times
                    if byte_i + 3 >= len(bytes_):
                        raise ValueError("SUP image data ended inside an RLE sequence.")
                    byte_3 = bytes_[byte_i + 2]
                    byte_4 = bytes_[byte_i + 3]
                    n_pixels = ((byte_2 - 0xC0) << 8) + byte_3
                    color = byte_4
                    byte_i += 4
                else:  # 00 XX | 0 X times
                    n_pixels = byte_2
                    color = 0
                    byte_i += 2
                if col_i + n_pixels > width:
                    raise ValueError("SUP image data extends past declared row width.")
                array[row_i, col_i : col_i + n_pixels] = color
                col_i += n_pixels
        else:  # XX | Color X, once
            if col_i >= width:
                raise ValueError("SUP image data extends past declared row width.")
            color = byte_1
            array[row_i, col_i] = color
            col_i += 1
            byte_i += 1
    return array


@nb.jit(nopython=True, nogil=True, cache=True, fastmath=True)
def read_sup_palette(bytes_: np.ndarray) -> np.ndarray:
    """Read a color palette from a block of bytes.

    Arguments:
        bytes_: block of bytes
    Returns:
        palette; first index is color, second is channel
    """
    palette = np.zeros((256, 4), np.uint8)
    byte_i = 0
    while byte_i < len(bytes_):
        color_i = bytes_[byte_i]
        y = bytes_[byte_i + 1]
        cb = bytes_[byte_i + 2]
        cr = bytes_[byte_i + 3]
        palette[color_i, 0] = y + 1.402 * (cr - 128)
        palette[color_i, 1] = y - 0.34414 * (cb - 128) - 0.71414 * (cr - 128)
        palette[color_i, 2] = y + 1.772 * (cb - 128)
        palette[color_i, 3] = bytes_[byte_i + 4]
        byte_i += 5
    palette[255] = [16, 128, 128, 0]

    return palette


@nb.jit(nopython=True, nogil=True, cache=True, fastmath=True)
def read_sup_series(  # noqa: PLR0912, PLR0915
    bytes_: np.ndarray,
) -> tuple[list[float], list[float], list[np.ndarray]]:
    """Read subtitle images and times from a block of bytes.

    Combine referenced image objects using their screen positions and source crops.
    Output canvases cover the object rectangles rather than the complete video frame.

    Arguments:
        bytes_: block of bytes
    Returns:
        subtitle starts, ends, and images
    Raises:
        ValueError: if a value is invalid
    """
    starts = []
    ends = []
    images = []

    palette = np.zeros((256, 4), np.uint8)
    object_images = {}

    pending_image_data = np.zeros(0, np.uint8)
    pending_image_data_length = -1
    pending_image_height = 0
    pending_image_object_id = -1
    pending_image_version = -1
    pending_image_width = 0

    active_start = -1.0
    active_image = np.zeros((0, 0, 4), np.uint8)
    has_active_image = False
    active_composition_number = -1

    set_timestamp = -1.0
    set_composition_number = -1
    set_composition = np.zeros((0, 7), np.int64)
    set_height = 0
    set_width = 0

    byte_i = 0
    while byte_i < len(bytes_):
        if byte_i + 13 > len(bytes_):
            raise ValueError("SUP segment header is truncated.")
        byte_i += 2
        timestamp = (
            int(bytes_[byte_i]) * 16777216
            + int(bytes_[byte_i + 1]) * 65536
            + int(bytes_[byte_i + 2]) * 256
            + int(bytes_[byte_i + 3])
        ) / 90000
        byte_i += 8
        segment_kind = bytes_[byte_i]
        byte_i += 1
        size = int(bytes_[byte_i]) * 256 + int(bytes_[byte_i + 1])
        byte_i += 2
        if byte_i + size > len(bytes_):
            raise ValueError("SUP segment data is truncated.")
        segment_bytes = bytes_[byte_i : byte_i + size]

        if set_timestamp < 0:
            set_timestamp = timestamp

        if segment_kind == 0x14:  # Palette
            if size < 2 or (size - 2) % 5 != 0:
                raise ValueError("SUP palette segment is truncated.")
            palette = read_sup_palette(segment_bytes[2:])
        elif segment_kind == 0x15:  # Image
            if size < 4:
                raise ValueError("SUP image segment is truncated.")
            object_id = int(segment_bytes[0]) * 256 + int(segment_bytes[1])
            object_version = int(segment_bytes[2])
            sequence_descriptor = int(segment_bytes[3])
            if (sequence_descriptor & 0x3F) != 0:
                raise ValueError("SUP image segment has invalid sequence descriptor.")

            if (sequence_descriptor & 0x80) != 0:
                if pending_image_object_id >= 0:
                    raise ValueError(
                        "SUP image segment started before previous image completed."
                    )
                if size < 11:
                    raise ValueError("SUP image segment is truncated.")
                object_data_length = (
                    int(segment_bytes[4]) * 65536
                    + int(segment_bytes[5]) * 256
                    + int(segment_bytes[6])
                )
                if object_data_length < 4:
                    raise ValueError("SUP image segment is truncated.")
                pending_image_data = segment_bytes[11:]
                pending_image_data_length = object_data_length - 4
                pending_image_height = int(segment_bytes[9]) * 256 + int(
                    segment_bytes[10]
                )
                pending_image_object_id = object_id
                pending_image_version = object_version
                pending_image_width = int(segment_bytes[7]) * 256 + int(
                    segment_bytes[8]
                )
            else:
                if pending_image_object_id < 0:
                    raise ValueError(
                        "Encountered SUP image continuation without initial image "
                        "segment."
                    )
                if (
                    object_id != pending_image_object_id
                    or object_version != pending_image_version
                ):
                    raise ValueError(
                        "SUP image continuation does not match initial image segment."
                    )
                pending_image_data = np.concatenate(
                    (pending_image_data, segment_bytes[4:])
                )

            if len(pending_image_data) > pending_image_data_length:
                raise ValueError(
                    "SUP image data extends past declared object data length."
                )
            if (sequence_descriptor & 0x40) != 0:
                if len(pending_image_data) != pending_image_data_length:
                    raise ValueError("SUP image segment data is truncated.")
                object_images[pending_image_object_id] = read_sup_image_array(
                    pending_image_data, pending_image_height, pending_image_width
                )
                pending_image_data = np.zeros(0, np.uint8)
                pending_image_data_length = -1
                pending_image_height = 0
                pending_image_object_id = -1
                pending_image_version = -1
                pending_image_width = 0
        elif segment_kind == 0x16:  # Presentation Composition
            if size < 11:
                raise ValueError("SUP presentation composition segment is truncated.")
            if (segment_bytes[7] & 0xC0) != 0:
                object_images.clear()
            set_composition_number = int(segment_bytes[5]) * 256 + int(segment_bytes[6])
            set_width = int(segment_bytes[0]) * 256 + int(segment_bytes[1])
            set_height = int(segment_bytes[2]) * 256 + int(segment_bytes[3])
            set_composition = _read_sup_composition(segment_bytes)
        elif segment_kind == 0x80:  # End
            if set_timestamp < 0:
                raise ValueError("Unexpected empty display set in SUP data.")

            if len(set_composition) > 0:
                if set_composition_number != active_composition_number:
                    if has_active_image:
                        starts.append(active_start)
                        ends.append(set_timestamp)
                        images.append(active_image)
                    active_start = set_timestamp
                    active_image = _render_sup_composition(
                        object_images, set_composition, palette, set_width, set_height
                    )
                    has_active_image = True
                    active_composition_number = set_composition_number
            elif has_active_image:
                starts.append(active_start)
                ends.append(set_timestamp)
                images.append(active_image)
                active_start = -1.0
                active_image = np.zeros((0, 0, 4), np.uint8)
                has_active_image = False
                active_composition_number = -1

            set_timestamp = -1.0
            set_composition_number = -1
            set_composition = np.zeros((0, 7), np.int64)

        byte_i += size

    if pending_image_object_id >= 0:
        raise ValueError("SUP image segment data is truncated.")

    if has_active_image:
        starts.append(active_start)
        ends.append(active_start)
        images.append(active_image)

    return starts, ends, images


@nb.jit(nopython=True, nogil=True, cache=True, fastmath=True)
def _composite_sup_image(target: np.ndarray, source: np.ndarray, x: int, y: int):
    """Composite one RGBA object over an existing subtitle canvas.

    Arguments:
        target: destination RGBA canvas
        source: source RGBA object
        x: destination horizontal position
        y: destination vertical position
    """
    for row in range(source.shape[0]):
        for col in range(source.shape[1]):
            source_alpha = int(source[row, col, 3]) / 255.0
            if source_alpha == 0:
                continue
            target_alpha = int(target[y + row, x + col, 3]) / 255.0
            output_alpha = source_alpha + target_alpha * (1 - source_alpha)
            for channel in range(3):
                target[y + row, x + col, channel] = round(
                    (
                        int(source[row, col, channel]) * source_alpha
                        + int(target[y + row, x + col, channel])
                        * target_alpha
                        * (1 - source_alpha)
                    )
                    / output_alpha
                )
            target[y + row, x + col, 3] = round(output_alpha * 255)


@nb.jit(nopython=True, nogil=True, cache=True, fastmath=True)
def _read_sup_composition(bytes_: np.ndarray) -> np.ndarray:
    """Read object references, placements, and optional source crops from a PCS.

    Arguments:
        bytes_: complete presentation composition segment payload
    Returns:
        rows containing object ID, x, y, crop x, crop y, crop width, and crop height
    Raises:
        ValueError: if an object reference or crop is truncated
    """
    composition = np.zeros((int(bytes_[10]), 7), np.int64)
    byte_i = 11
    for object_i in range(len(composition)):
        if byte_i + 8 > len(bytes_):
            raise ValueError("SUP composition object reference is truncated.")
        composition[object_i, 0] = int(bytes_[byte_i]) * 256 + int(bytes_[byte_i + 1])
        composition[object_i, 1] = int(bytes_[byte_i + 4]) * 256 + int(
            bytes_[byte_i + 5]
        )
        composition[object_i, 2] = int(bytes_[byte_i + 6]) * 256 + int(
            bytes_[byte_i + 7]
        )
        is_cropped = (bytes_[byte_i + 3] & 0x80) != 0
        byte_i += 8
        composition[object_i, 5] = -1
        composition[object_i, 6] = -1
        if is_cropped:
            if byte_i + 8 > len(bytes_):
                raise ValueError("SUP composition object crop is truncated.")
            for crop_i in range(4):
                composition[object_i, crop_i + 3] = int(
                    bytes_[byte_i + crop_i * 2]
                ) * 256 + int(bytes_[byte_i + crop_i * 2 + 1])
            byte_i += 8
    return composition


@nb.jit(nopython=True, nogil=True, cache=True, fastmath=True)
def _render_sup_composition(
    object_images: dict[int, np.ndarray],
    composition: np.ndarray,
    palette: np.ndarray,
    screen_width: int,
    screen_height: int,
) -> np.ndarray:
    """Render referenced objects into their combined bounding rectangle.

    Preserve object dimensions for single-object compositions and retain relative
    screen positions when a composition contains multiple objects.

    Arguments:
        object_images: decoded palette-index images keyed by object ID
        composition: referenced object IDs, placements, and optional source crops
        palette: RGBA palette
        screen_width: declared video width
        screen_height: declared video height
    Returns:
        RGBA subtitle canvas trimmed to its object rectangles
    Raises:
        ValueError: if an object is undefined or its crop or placement is invalid
    """
    rendered_images = []
    positions = []
    min_x = screen_width
    min_y = screen_height
    max_x = 0
    max_y = 0
    for reference in composition:
        object_id = reference[0]
        if object_id not in object_images:
            raise ValueError("SUP composition references an undefined image object.")
        compressed_image = object_images[object_id]
        x, y, crop_x, crop_y, width, height = reference[1:]
        if width < 0:
            height, width = compressed_image.shape
        if (
            width <= 0
            or height <= 0
            or crop_x + width > compressed_image.shape[1]
            or crop_y + height > compressed_image.shape[0]
        ):
            raise ValueError("SUP composition object crop exceeds image bounds.")
        if x + width > screen_width or y + height > screen_height:
            raise ValueError("SUP composition object placement exceeds video bounds.")
        rendered_images.append(
            _render_sup_image(
                compressed_image[crop_y : crop_y + height, crop_x : crop_x + width],
                height,
                width,
                palette,
            )
        )
        positions.append((x, y))
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x + width)
        max_y = max(max_y, y + height)

    image = np.zeros((max_y - min_y, max_x - min_x, 4), np.uint8)
    for object_image, (x, y) in zip(rendered_images, positions):
        _composite_sup_image(image, object_image, x - min_x, y - min_y)
    return image


@nb.jit(nopython=True, nogil=True, cache=True, fastmath=True)
def _render_sup_image(
    compressed_image: np.ndarray, height: int, width: int, palette: np.ndarray
) -> np.ndarray:
    """Render an RGBA subtitle image from palette and compressed image data.

    Arguments:
        compressed_image: palette-index image data
        height: image height
        width: image width
        palette: RGBA palette
    Returns:
        rendered RGBA image
    """
    image = np.zeros((height, width, 4), np.uint8)
    for i in range(height):
        for j in range(width):
            image[i, j] = palette[compressed_image[i, j]]
    return image
