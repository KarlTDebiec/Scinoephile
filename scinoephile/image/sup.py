#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to the SUP subtitle format."""

from __future__ import annotations

import numba as nb
import numpy as np


@nb.jit(nopython=True, nogil=True, cache=True, fastmath=True)
def read_sup_image_array(bytes_: bytearray, height: int, width: int) -> np.ndarray:
    """Read a palette-compressed image from a block of bytes.

    Arguments:
        bytes_: Block of bytes
        height: height of image
        width: width of image
    Returns:
        Compressed image
    """
    array = np.zeros((height, width), np.uint8)
    byte_i = 0
    row_i = 0
    col_i = 0
    while byte_i < len(bytes_):
        byte_1 = bytes_[byte_i]
        if byte_1 == 0x00:  # 00 | Special behaviors
            byte_2 = bytes_[byte_i + 1]
            if byte_2 == 0x00:  # 00 00 | New line
                byte_i += 2
                row_i += 1
                col_i = 0
            else:
                if (byte_2 & 0xC0) == 0x40:  # 00 4X XX | Color 0, X times
                    byte_3 = bytes_[byte_i + 2]
                    n_pixels = ((byte_2 - 0x40) << 8) + byte_3
                    color = 0
                    byte_i += 3
                elif (byte_2 & 0xC0) == 0x80:  # 00 8Y XX | Color X,  Y times
                    byte_3 = bytes_[byte_i + 2]
                    n_pixels = byte_2 - 0x80
                    color = byte_3
                    byte_i += 3
                elif (byte_2 & 0xC0) != 0x00:  # 00 CY YY XX | Color X, Y times
                    byte_3 = bytes_[byte_i + 2]
                    byte_4 = bytes_[byte_i + 3]
                    n_pixels = ((byte_2 - 0xC0) << 8) + byte_3
                    color = byte_4
                    byte_i += 4
                else:  # 00 XX | 0 X times
                    n_pixels = byte_2
                    color = 0
                    byte_i += 2
                array[row_i, col_i : col_i + n_pixels] = color
                col_i += n_pixels
        else:  # XX | Color X, once
            color = byte_1
            array[row_i, col_i] = color
            col_i += 1
            byte_i += 1
    return array


@nb.jit(nopython=True, nogil=True, cache=True, fastmath=True)
def read_sup_palette(bytes_: bytearray) -> np.ndarray:
    """Read a color palette from a block of bytes.

    Arguments:
        bytes_: Block of bytes
    Returns:
        Palette; first index is color, second is channel
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
def read_sup_series(
    bytes_: bytearray,
) -> tuple[list[float], list[float], list[np.ndarray]]:
    """Read subtitle images and times from a block of bytes.

    Arguments:
        bytes_: Block of bytes
    Returns:
        Subtitle starts, ends, and images
    """
    starts = []
    ends = []
    images = []

    byte_i = 0
    seeking_start = True
    while byte_i < len(bytes_):
        # Load header
        byte_i += 2
        timestamp = (
            bytes_[byte_i] * 16777216
            + bytes_[byte_i + 1] * 65536
            + bytes_[byte_i + 2] * 256
            + bytes_[byte_i + 3]
        )
        byte_i += 8
        segment_kind = bytes_[byte_i]
        byte_i += 1
        size = bytes_[byte_i] * 256 + bytes_[byte_i + 1]
        byte_i += 2

        # Load content
        if segment_kind == 0x14:  # Palette
            palette_bytes = bytes_[byte_i + 2 : byte_i + size]
            palette = read_sup_palette(palette_bytes)
        elif segment_kind == 0x15:  # Image
            width = bytes_[byte_i + 7] * 256 + bytes_[byte_i + 8]
            height = bytes_[byte_i + 9] * 256 + bytes_[byte_i + 10]
            image_bytes = bytes_[byte_i + 11 : byte_i + size]
            compressed_image = read_sup_image_array(image_bytes, height, width)
        elif segment_kind == 0x80:  # End
            if seeking_start:
                starts.append(timestamp / 90000)
                image = np.zeros((height, width, 4), np.uint8)
                for i in range(height):
                    for j in range(width):
                        image[i, j] = palette[compressed_image[i, j]]
                images.append(image)
                seeking_start = False
            else:
                ends.append(timestamp / 90000)
                seeking_start = True
        byte_i += size
    return starts, ends, images
