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
from scinoephile.ocr import ImageSubtitleSeries, OCRBase
from IPython import embed


################################### CLASSES ###################################
class ImageSubtitleDataset(SubtitleDataset, OCRBase):
    """
    A collection of image-based subtitles
    """

    # region Class Attributes

    series_class = ImageSubtitleSeries

    # endregion

    # region Public Properties

    @property
    def subtitles(self):
        """pandas.core.frame.DataFrame: Subtitles"""
        if not hasattr(self, "_subtitles"):
            self._subtitles = self.series_class(mode=self.mode,
                                                interactive=self.interactive,
                                                verbosity=self.verbosity)
        return self._subtitles

    @subtitles.setter
    def subtitles(self, value):
        if value is not None:
            if not isinstance(value, self.series_class):
                raise ValueError()
        self._subtitles = value

    # endregion

    # region Public Methods

    def load(self, infile=None):
        from os.path import expandvars

        # Process arguments
        if infile is not None:
            infile = expandvars(infile)
        elif self.infile is not None:
            infile = self.infile
        else:
            raise ValueError()

        # Load infile
        if self.verbosity >= 1:
            print(f"Reading subtitles from '{infile}'")
        self.subtitles = self.series_class.load(infile,
                                                mode=self.mode,
                                                verbosity=self.verbosity)
        self.subtitles.verbosity = self.verbosity

    def show(self, data=None, indexes=None, cols=20):
        import numpy as np
        from PIL import Image

        # Process arguments
        if data is None and indexes is None:
            data = self.char_data
            indexes = range(self.char_data.shape[0])
        elif data is None and indexes is not None:
            data = self.char_data
        elif data is not None and indexes is None:
            indexes = range(data.shape[0])
        if isinstance(indexes, int):
            indexes = [indexes]
        indexes = np.array(indexes, np.int)
        if np.any(indexes >= data.shape[0]):
            raise ValueError()
        if cols is None:
            cols = indexes.size
            rows = 1
        else:
            rows = int(np.ceil(indexes.size / cols))

        # Draw image
        if self.mode == "8 bit":
            img = Image.new("L", (cols * 100, rows * 100), 255)
        elif self.mode == "1 bit":
            img = Image.new("1", (cols * 100, rows * 100), 1)
        for i, index in enumerate(indexes):
            column = (i // cols)
            row = i - (column * cols)
            if self.mode == "8 bit":
                char_img = Image.fromarray(data[index])
            elif self.mode == "1 bit":
                char_img = Image.fromarray(
                    data[index].astype(np.uint8) * 255)
            img.paste(char_img, (100 * row + 10,
                                 100 * column + 10,
                                 100 * (row + 1) - 10,
                                 100 * (column + 1) - 10))
        img.show()

    # endregion
