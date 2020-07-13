#!/usr/bin/env python3
#   scinoephile.ocr.ImageSubtitleEvent.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import numpy as np
from scinoephile import SubtitleEvent


################################### CLASSES ###################################
class ImageSubtitleEvent(SubtitleEvent):
    """
    An individual image-based subtitle
    """

    # TODO: rename data to full_data, char_data to data

    # region Builtins

    def __init__(self, data=None, **kwargs):
        """
        Initializes

        Args:
            data (ndarray): Subtitle image data
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store property values
        if data is not None:
            self.full_data = data

    # endregion

    # region Public Properties

    @property
    def char_bounds(self):
        """ndarray(int): Boundaries of individual characters within subtitle"""
        if not hasattr(self, "_char_bounds"):
            self._initialize_char_bounds()
        return self._char_bounds

    @property
    def char_count(self):
        """int: Number of individual characters within subtitle"""
        return self.char_bounds.shape[0]

    @property
    def char_data(self):
        """ndarray: Image data of individual characters within subtitle"""
        if not hasattr(self, "_char_data"):
            self._initialize_char_data()
        return self._char_data

    @property
    def char_indexes(self):
        """ndarray(int): Indexes of character images within series'
         deduplicated character image data"""
        if not hasattr(self, "_char_indexes"):
            self._char_indexes = np.zeros(self.char_count, np.int)
        return self._char_indexes

    @property
    def char_separations(self):
        """ndarray(int): Widths of spaces between individual characters within
        subtitle"""
        return self.char_bounds[1:, 0] - self.char_bounds[:-1, 1]

    @property
    def char_spec(self):
        """DataFrame: Specification of individual characters within subtitle"""
        return self.series.spec.iloc[self.char_indexes]

    @property
    def char_widths(self):
        """ndarray(int): Widths of individual characters within subtitle"""
        return self.char_bounds[:, 1] - self.char_bounds[:, 0]

    @property
    def full_data(self):
        """ndarray: Subtitle image data"""
        if not hasattr(self, "_full_data"):
            self._full_data = None
        return self._full_data

    @full_data.setter
    def full_data(self, value):
        if value is not None:
            from PIL import Image

            if not isinstance(value, np.ndarray):
                raise ValueError(self._generate_setter_exception(value))

            if len(value.shape) == 3:  # Convert RGB to L
                trans_bg = Image.fromarray(value)
                white_bg = Image.new("RGBA", trans_bg.size,
                                     (255, 255, 255, 255))
                white_bg.paste(trans_bg, mask=trans_bg)
                value = np.array(white_bg.convert("L"))

        self._full_data = value

    @property
    def img(self):
        """Image: Image of subtitle"""
        if not hasattr(self, "_img"):
            from PIL import Image

            if self.full_data is not None:
                self._img = Image.fromarray(self.full_data)
            else:
                raise ValueError()
        return self._img

    @property
    def index(self):
        """int: Index of subtitle within series"""
        if not hasattr(self, "_index"):
            self._index = self.series.events.index(self)
        return self._index

    @property
    def series(self):
        """Image SubtitleSeries: Subtitle series of which this subtitle is a
        part"""
        if not hasattr(self, "_series"):
            self._series = None
        return self._series

    @series.setter
    def series(self, value):
        from scinoephile.ocr import ImageSubtitleSeries

        if not isinstance(value, ImageSubtitleSeries):
            raise ValueError(self._generate_setter_exception(value))
        self._series = value

    # endregion

    # region Public Methods

    def save(self, path):
        """
        Saves subtitle image to an output file

        Args:
            path (str): Path to output file
        """
        from os.path import expandvars

        path = expandvars(path).replace("//", "/")
        if self.verbosity >= 1:
            print(f"Writing subtitle to '{path}'")
        self.img.save(path)

    def show(self):
        """
        Shows subtitle image
        """
        from scinoephile.ocr import show_img

        show_img(self.img)

    # endregion

    # region Private Methods

    def _initialize_char_bounds(self):
        """
        Identifies boundaries between characters
        """
        white_cols = (self.full_data == self.full_data.max()).all(axis=0)
        diff = np.diff(np.array(white_cols, np.int))
        # Get starts of chars, ends of chars, first nonwhite, last nonwhite
        bounds = np.unique(((np.where(diff == -1)[0] + 1).tolist()
                            + np.where(diff == 1)[0].tolist()
                            + [np.argmin(white_cols)]
                            + [white_cols.size - 1
                               - np.argmin(white_cols[::-1])]))
        bounds = bounds.reshape((-1, 2))
        self._char_bounds = bounds

    def _initialize_char_data(self):
        char_data = np.ones((self.char_bounds.shape[0], 80, 80),
                            np.uint8) * 255
        for i, (x1, x2) in enumerate(self.char_bounds):
            char = self.full_data[:, x1:x2 + 1]
            white_rows = (char == char.max()).all(axis=1)
            char = char[np.argmin(white_rows):
                        white_rows.size - np.argmin(white_rows[::-1])]
            x = int(np.floor((80 - char.shape[1]) / 2))
            y = int(np.floor((80 - char.shape[0]) / 2))
            char_data[i, y:y + char.shape[0], x:x + char.shape[1]] = char
        self._char_data = char_data

    # endregion
