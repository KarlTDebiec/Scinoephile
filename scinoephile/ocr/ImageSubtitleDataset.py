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
from scinoephile.ocr import ImageSubtitleSeries
from IPython import embed


################################### CLASSES ###################################
class ImageSubtitleDataset(SubtitleDataset):
    """
    A collection of image-based subtitles
    """

    # region Class Attributes

    series_class = ImageSubtitleSeries

    # endregion

    # region Builtins

    def __init__(self, mode=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if mode is not None:
            self.mode = mode

    # endregion

    # region Public Properties

    @property
    def char_data(self):
        """ndarray: Image data of individual characters within subtitles"""
        return self.subtitles.char_data

    @property
    def char_indexes(self):
        """tuple(int, int): Indexes of char data in form of (subtitle, char)"""
        return self.subtitles.char_indexes

    @property
    def mode(self):
        """str: Image mode"""
        if not hasattr(self, "_mode"):
            self._mode = "1 bit"
        return self._mode

    @mode.setter
    def mode(self, value):
        if value is not None:
            if not isinstance(value, str):
                try:
                    value = str(value)
                except Exception:
                    raise ValueError(self._generate_setter_exception(value))
            if value == "8 bit":
                pass
            elif value == "1 bit":
                pass
            else:
                raise ValueError(self._generate_setter_exception(value))
        # TODO: If changed, change on self.subtitles as well

        self._mode = value

    @property
    def subtitles(self):
        """pandas.core.frame.DataFrame: Subtitles"""
        if not hasattr(self, "_subtitles"):
            self._subtitles = self.series_class(imgmode=self.mode,
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

    def char_index_to_sub_char_indexes(self, index):
        return self.char_indexes[index]

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
                                                imgmode=self.mode,
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
        else:
            raise NotImplementedError()
        for i, index in enumerate(indexes):
            column = (i // cols)
            row = i - (column * cols)
            if self.mode == "8 bit":
                char_img = Image.fromarray(data[index])
            elif self.mode == "1 bit":
                char_img = Image.fromarray(
                    data[index].astype(np.uint8) * 255)
            else:
                raise NotImplementedError()
            img.paste(char_img, (100 * row + 10,
                                 100 * column + 10,
                                 100 * (row + 1) - 10,
                                 100 * (column + 1) - 10))
        img.show()

    def sub_char_indexes_to_char_index(self, sub_index, char_index):
        return self.char_indexes.index((sub_index, char_index))

    # endregion
