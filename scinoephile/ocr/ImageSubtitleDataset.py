#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.ImageSubtitleDataset.py
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
      - [ ] Document
    """
    from scinoephile.ocr import ImageSubtitleSeries

    # region Instance Variables
    help_message = ("Tool for extracting individual characters from"
                    "image-based subtitles")
    series_class = ImageSubtitleSeries

    # endregion

    # region Builtins
    def __init__(self, infile=None, outfile=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if infile is not None:
            self.infile = infile
        if outfile is not None:
            self.outfile = outfile

        # Temporary manual configuration for testing
        self.infile = "/Users/kdebiec/Dropbox/code/subtitles/" \
                      "magnificent_mcdull/original/" \
                      "Magnificent Mcdull.3.zho.sup"
        self.outfile = "/Users/kdebiec/Dropbox/code/subtitles/" \
                       "magnificent_mcdull/" \
                       "mcdull.h5"
        # self.infile = self.outfile
        # self.outfile = None

    # endregion

    # region Public Properties

    @property
    def image_mode(self):
        """str: Image mode"""
        if not hasattr(self, "_image_mode"):
            self._image_mode = "8bit"
        return self._image_mode

    @image_mode.setter
    def image_mode(self, value):
        if value is not None:
            if not isinstance(value, str):
                try:
                    value = str(value)
                except Exception:
                    raise ValueError(self._generate_setter_exception(value))
            elif value == "2bit":
                raise NotImplementedError()
            elif value == "1bit":
                raise NotImplementedError()
            elif value not in ["2bit"]:
                raise ValueError(self._generate_setter_exception(value))

        self._image_mode = value

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    ImageSubtitleDataset.main()
