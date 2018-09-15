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
from scinoephile import CLToolBase
from IPython import embed


################################### CLASSES ###################################
class Reader(CLToolBase):
    """
    Extracts individual characters from image-based subtitles

    TODO:
      - [x] Open SUP file and loop over bytes
      - [x] Read images
      - [ ] Read and apply image palettes
      - [ ] Read times and locations
      - [ ] Store times and locations in hdf5
      - [ ] Store images in hdf5
      - [ ] Implement equivalent support for BDSup2Sub/vobsub2srt workflow
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
                         "mcdull_prince_de_la_bun/original/" \
                         "Mcdull Prince de la Bun.6.zho.sup"

    def __call__(self):
        """Core logic"""
        import numpy as np
        from PIL import Image

        with open(self.input_sub, "rb") as infile:
            raw = infile.read()

        b2i = lambda x: int.from_bytes(x, byteorder="big")

        def read_image(bytes, width, height):
            image = np.zeros((width * height), np.uint8)
            bytes_index = 0
            pixel_index = 0
            while bytes_index <= len(bytes) - 1:
                byte_1 = bytes[bytes_index]
                if byte_1 == 0x00:
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

        offset = 0
        last_header_offset = 0
        print(f"TYPE      HEX:     START      TIME      SIZE    OFFSET     BYTES")
        while True:
            if b2i(raw[offset:offset + 2]) != 0x5047:
                raise ValueError()

            header_offset = offset
            timestamp = b2i(raw[header_offset + 2:header_offset + 6])
            type = raw[header_offset + 10]
            size = b2i(raw[header_offset + 11: header_offset + 13])
            content_offset = header_offset + 13
            if type == 0x14:
                kind = "PDS"
            elif type == 0x15:
                kind = "ODS"
                image_bytes = raw[content_offset + 11:content_offset + size]
                width = b2i(raw[content_offset + 7:content_offset + 9])
                height = b2i(raw[content_offset + 9:content_offset + 11])
                image = read_image(image_bytes, width, height)
                Image.fromarray(image).show()
            elif type == 0x16:
                kind = "PCS"
            elif type == 0x17:
                kind = "WDS"
            elif type == 0x80:
                kind = "END"
            else:
                kind = "UNKNOWN"
            if header_offset != 0:
                print(f"{header_offset - last_content_start:>9d}")
            print(f"{kind:<8s} {hex(type)}: "
                  f"{header_offset:>9d} "
                  f"{timestamp:>9d} "
                  f"{size:>9d} "
                  f"{content_offset:>9d} ", end='')
            last_content_start = content_offset

            offset += 13 + size
            # if offset >= 100000:
            #     break
            if offset >= len(raw):
                break
        print(f"{offset - last_content_start:>9d}")

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
    Reader.main()
