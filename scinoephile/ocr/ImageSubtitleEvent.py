#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.ImageSubtitleEvent.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile import SubtitleEvent
from scinoephile.ocr import OCRBase
from IPython import embed


################################### CLASSES ###################################
class ImageSubtitleEvent(SubtitleEvent, OCRBase):
    """
    An individual image-based subtitle
    """

    # region Builtins

    def __init__(self, data=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if data is not None:
            self.data = data

    # endregion

    # region Public Properties

    @property
    def char_bounds(self):
        """ndarray(int): Boundaries of individual characters within subtitle"""
        if not hasattr(self, "_char_bounds"):
            import numpy as np

            white_cols = (self.data == self.data.max()).all(axis=0)
            diff = np.diff(np.array(white_cols, np.int))
            # Get starts of chars, ends of chars, first nonwhite, last nonwhite
            bounds = np.unique(((np.where(diff == -1)[0] + 1).tolist()
                                + np.where(diff == 1)[0].tolist()
                                + [np.argmin(white_cols)]
                                + [white_cols.size - 1
                                   - np.argmin(white_cols[::-1])]))
            bounds = bounds.reshape((-1, 2))
            self._char_bounds = bounds
        return self._char_bounds

    @property
    def char_widths(self):
        """ndarray(int): Widths of individual characters within subtitle"""
        if not hasattr(self, "_char_widths"):
            self._char_widths = self.char_bounds[:, 1] - self.char_bounds[:, 0]
        return self._char_widths

    @property
    def char_data(self):
        """ndarray: Image data of individual characters within subtitle"""
        if not hasattr(self, "_char_data"):
            import numpy as np

            if self.mode == "8 bit":
                chars = np.ones((self.char_bounds.shape[0], 80, 80),
                                np.uint8) * 255
            elif self.mode == "1 bit":
                chars = np.ones((self.char_bounds.shape[0], 80, 80),
                                np.bool)
            for i, (x1, x2) in enumerate(self.char_bounds):
                char = self.data[:, x1:x2 + 1]
                white_rows = (char == char.max()).all(axis=1)
                char = char[np.argmin(white_rows):
                            white_rows.size - np.argmin(white_rows[::-1])]
                x = int(np.floor((80 - char.shape[1]) / 2))
                y = int(np.floor((80 - char.shape[0]) / 2))
                chars[i, y:y + char.shape[0], x:x + char.shape[1]] = char
            self._char_data = chars
        return self._char_data

    @property
    def data(self):
        """str: Image data"""
        if not hasattr(self, "_data"):
            self._data = None
        return self._data

    @data.setter
    def data(self, value):
        if value is not None:
            import numpy as np
            from PIL import Image

            if not isinstance(value, np.ndarray):
                raise ValueError(self._generate_setter_exception(value))

            if self.mode == "8 bit":
                if len(value.shape) == 3:  # Convert RGB to L
                    trans_bg = Image.fromarray(value)
                    white_bg = Image.new("RGBA", trans_bg.size,
                                         (255, 255, 255, 255))
                    white_bg.paste(trans_bg, mask=trans_bg)
                    value = np.array(white_bg.convert("L"))
                # TODO: Should this also handle inputs of mode 1? Or error out?
            elif self.mode == "1 bit":
                if len(value.shape) == 3:  # Convert RGB to 1
                    trans_bg = Image.fromarray(value)
                    white_bg = Image.new("RGBA", trans_bg.size,
                                         (255, 255, 255, 255))
                    white_bg.paste(trans_bg, mask=trans_bg)
                    value = np.array(white_bg.convert("1", dither=0))
                # TODO: Should this also handle inputs of mode L?
            else:
                raise ValueError(self._generate_setter_exception(value))
        # TODO: If changed, clear cached properties

        self._data = value

    @property
    def img(self):
        """Image: Image of subtitle"""
        if not hasattr(self, "_img"):
            import numpy as np
            from PIL import Image

            if self.data is not None:
                if self.mode == "8 bit":
                    self._img = Image.fromarray(self.data)
                elif self.mode == "1 bit":
                    self._img = Image.fromarray(
                        self.data.astype(np.uint8) * 255,
                        mode="L").convert("1")
            else:
                raise ValueError()
        return self._img

    # endregion

    # region Public Methods

    def show(self):
        """
        Shows image of subtitle
        """
        self.img.show()

    # endregion
