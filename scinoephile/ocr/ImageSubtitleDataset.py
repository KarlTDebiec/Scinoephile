#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.Reader.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile import SubtitleDataset
from IPython import embed


################################### CLASSES ###################################
class ImageSubtitleDataset(SubtitleDataset):
    """
    Extracts individual characters from image-based subtitles

    TODO:
      - [x] Open SUP file and loop over bytes
      - [x] Read images
      - [x] Read and apply image palettes
      - [x] Read times and locations
      - [ ] Store times and locations in hdf5 or text
      - [ ] Store images in hdf5
    """

    # region Instance Variables
    help_message = ("Tool for extracting individual characters from"
                    "image-based subtitles")

    # endregion

    # region Builtins
    def __init__(self, input_sub=None, output_hdf5=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if input_sub is not None:
            self.input_sub = input_sub
        if output_hdf5 is not None:
            self.output_hdf5 = output_hdf5

        # Temporary manual configuration for testing
        self.input_sub = "/Users/kdebiec/Dropbox/code/subtitles/" \
                         "magnificent_mcdull/original/" \
                         "Magnificent Mcdull.3.zho.sup"

    def __call__(self):
        """Core logic"""
        import numpy as np
        from PIL import Image

        def read_palette(bytes):
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

        def read_image(bytes, width, height):
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

        with open(self.input_sub, "rb") as infile:
            sup_bytes = infile.read()

        bytes2int = lambda x: int.from_bytes(x, byteorder="big")

        subtitle_index = 1
        byte_offset = 0
        start_time = None
        palette = None
        reduced_image = None
        segment_kinds = {0x14: "PDS", 0x15: "ODS", 0x16: "PCS",
                         0x17: "WDS", 0x80: "END"}
        if self.verbosity >= 2:
            print(f"KIND   :     START      TIME      SIZE    OFFSET")
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
                palette = read_palette(palette_bytes)
            elif segment_kind == 0x15:  # Image
                image_bytes = sup_bytes[content_offset + 11:content_offset + content_size]
                width = bytes2int(sup_bytes[content_offset + 7:content_offset + 9])
                height = bytes2int(sup_bytes[content_offset + 9:content_offset + 11])
                reduced_image = read_image(image_bytes, width, height)
            elif segment_kind == 0x80:  # End
                if start_time is None:
                    start_time = timestamp / 90000
                    image = np.zeros((*reduced_image.shape, 4), np.uint8)
                    for color_index, color in enumerate(palette):
                        image[np.where(reduced_image == color_index)] = color
                else:
                    end_time = timestamp / 90000
                    # outfile = f"/Users/kdebiec/Desktop/magnificent_mcdull/{subtitle_index:06d}.png"
                    # print(f"{start_time:>9.3f} {end_time:>9.3f} {outfile}")
                    # Image.fromarray(image).save(outfile)
                    # Add image to nascent collection
                    subtitle_index += 1
                    start_time = None
                    palette = None
                    reduced_image = None
            if self.verbosity >= 2:
                print(f"{segment_kinds.get(segment_kind, 'UNKNOWN'):<8s} "
                      f"{hex(segment_kind)}: "
                      f"{header_offset:>9d} "
                      f"{timestamp:>9d} "
                      f"{content_size:>9d} "
                      f"{content_offset:>9d} ")

            byte_offset += 13 + content_size
            if byte_offset >= len(sup_bytes):
                break
        # embed(**self.embed_kw)

    # endregion

    # region Properties
    @property
    def input_sup(self):
        """str: Path to input hdf5 file"""
        if not hasattr(self, "_input_sup"):
            self._input_sup = None
        return self._input_sup

    @input_sup.setter
    def input_sup(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._input_sup = value

    @property
    def output_hdf5(self):
        """str: Path to output hdf5 file"""
        if not hasattr(self, "_output_hdf5"):
            self._output_hdf5 = None
        return self._output_hdf5

    @output_hdf5.setter
    def output_hdf5(self, value):
        from os import access, getcwd, R_OK, W_OK
        from os.path import dirname, expandvars, isfile

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
            elif isfile(value) and not access(value, R_OK):
                raise ValueError(self._generate_setter_exception(value))
            elif dirname(value) == "" and not access(getcwd(), W_OK):
                raise ValueError(self._generate_setter_exception(value))
            elif not access(dirname(value), W_OK):
                raise ValueError(self._generate_setter_exception(value))
        self._output_hdf5 = value

    # endregion

    # region Class Methods

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    ImageSubtitleDataset.main()
