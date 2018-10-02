#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.SUPFormat.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from pysubs2.formatbase import FormatBase
from IPython import embed


################################### CLASSES ###################################
class SUPFormat(FormatBase):
    """
    Subtitle format for Blu-Ray SUP

    TODO:
      - [ ] Load from SUP
      - [ ] Document
    """

    # region Public Class Methods

    @classmethod
    def from_file(cls, subs, fp, **kwargs):
        """
        TODO:
          - [ ] Support verbosity
        """
        import numpy as np
        from pysubs2.time import make_time
        from scinoephile.ocr import ImageSubtitleEvent

        bytes2int = lambda x: int.from_bytes(x, byteorder="big")
        segment_kinds = {0x14: "PDS", 0x15: "ODS", 0x16: "PCS",
                         0x17: "WDS", 0x80: "END"}
        # Load infile
        # if self.verbosity >= 1:
        #     print(f"Reading subtitles from '{path}'")
        sup_bytes = fp.read()

        # Parse infile
        events = []
        byte_offset = 0
        start_time = None
        image = None
        palette = None
        compressed_image = None
        # if self.verbosity >= 2:
        #     print(f"KIND   :     START      TIME      SIZE    OFFSET")
        while True:
            if bytes2int(sup_bytes[byte_offset:byte_offset + 2]) != 0x5047:
                raise ValueError()

            header_offset = byte_offset
            timestamp = bytes2int(sup_bytes[header_offset + 2:header_offset + 6])
            segment_kind = sup_bytes[header_offset + 10]
            content_size = bytes2int(sup_bytes[header_offset + 11: header_offset + 13])
            content_offset = header_offset + 13

            if segment_kind == 0x14:  # Palette
                palette_bytes = sup_bytes[content_offset + 2:content_offset + content_size]
                palette = cls.read_palette(palette_bytes)
            elif segment_kind == 0x15:  # Image
                image_bytes = sup_bytes[content_offset + 11:content_offset + content_size]
                width = bytes2int(sup_bytes[content_offset + 7:content_offset + 9])
                height = bytes2int(sup_bytes[content_offset + 9:content_offset + 11])
                compressed_image = cls.read_image(image_bytes, width, height)
            elif segment_kind == 0x80:  # End
                if start_time is None:
                    start_time = timestamp / 90000
                    image = np.zeros((*compressed_image.shape, 4), np.uint8)
                    for color_index, color in enumerate(palette):
                        image[np.where(compressed_image == color_index)] = color
                else:
                    end_time = timestamp / 90000
                    subs.events.append(ImageSubtitleEvent(
                        start=make_time(s=start_time),
                        end=make_time(s=end_time), image=image))

                    start_time = None
                    palette = None
                    compressed_image = None

            # if self.verbosity >= 2:
            #     print(f"{segment_kinds.get(segment_kind, 'UNKNOWN'):<8s} "
            #           f"{hex(segment_kind)}: "
            #           f"{header_offset:>9d} "
            #           f"{timestamp:>9d} "
            #           f"{content_size:>9d} "
            #           f"{content_offset:>9d} ")

            byte_offset += 13 + content_size
            if byte_offset >= len(sup_bytes):  # >= 100000:
                break

        return subs

    # endregion

    # region Static Methods

    @staticmethod
    def read_palette(bytes):
        import numpy as np

        palette = np.zeros((256, 4), np.uint8)
        bytes_index = 0
        while bytes_index < len(bytes):
            color_index = bytes[bytes_index]
            y = bytes[bytes_index + 1]
            cb = bytes[bytes_index + 2]
            cr = bytes[bytes_index + 3]
            palette[color_index, 0] = y + 1.402 * (cr - 128)
            palette[color_index, 1] = y - .34414 * (cb - 128) - .71414 * (cr - 128)
            palette[color_index, 2] = y + 1.772 * (cb - 128)
            palette[color_index, 3] = bytes[bytes_index + 4]
            bytes_index += 5
        palette[255] = [16, 128, 128, 0]

        return palette

    @staticmethod
    def read_image(bytes, width, height):
        import numpy as np

        image = np.zeros((width * height), np.uint8)
        bytes_index = 0
        pixel_index = 0
        while bytes_index < len(bytes):
            byte_1 = bytes[bytes_index]
            if byte_1 == 0x00:  # 00 | Special behaviors
                byte_2 = bytes[bytes_index + 1]
                if byte_2 == 0x00:  # 00 00 | New line
                    bytes_index += 2
                elif (byte_2 & 0xC0) == 0x40:  # 00 4X XX | 0 X times
                    byte_3 = bytes[bytes_index + 2]
                    n_pixels = ((byte_2 - 0x40) << 8) + byte_3
                    color = 0
                    image[pixel_index:pixel_index + n_pixels] = color
                    pixel_index += n_pixels
                    bytes_index += 3
                elif (byte_2 & 0xC0) == 0x80:  # 00 8Y XX | X Y times
                    byte_3 = bytes[bytes_index + 2]
                    n_pixels = byte_2 - 0x80
                    color = byte_3
                    image[pixel_index:pixel_index + n_pixels] = color
                    pixel_index += n_pixels
                    bytes_index += 3
                elif (byte_2 & 0xC0) != 0x00:  # 00 CY YY XX | X Y times
                    byte_3 = bytes[bytes_index + 2]
                    byte_4 = bytes[bytes_index + 3]
                    n_pixels = ((byte_2 - 0xC0) << 8) + byte_3
                    color = byte_4
                    image[pixel_index:pixel_index + n_pixels] = color
                    pixel_index += n_pixels
                    bytes_index += 4
                else:  # 00 XX | 0 X times
                    n_pixels = byte_2
                    color = 0
                    image[pixel_index:pixel_index + n_pixels] = color
                    pixel_index += n_pixels
                    bytes_index += 2
            else:  # XX | X once
                color = byte_1
                image[pixel_index] = color
                pixel_index += 1
                bytes_index += 1
        image.resize((height, width))

        return image

    # endregion
