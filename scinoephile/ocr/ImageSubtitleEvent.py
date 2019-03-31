#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.ImageSubtitleEvent.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import numpy as np
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
        if not hasattr(self, "_char_bounds"):
            self._initialize_char_bounds()
        return self.char_bounds.shape[0]

    @property
    def char_data(self):
        """ndarray: Image data of individual characters within subtitle"""
        if not hasattr(self, "_char_bounds"):
            self._initialize_char_bounds()

        if self.mode == "8 bit":
            _char_data = np.ones(
                (self.char_bounds.shape[0], 80, 80), np.uint8) * 255
        elif self.mode == "1 bit":
            _char_data = np.ones(
                (self.char_bounds.shape[0], 80, 80), np.bool)
        for i, (x1, x2) in enumerate(self.char_bounds):
            char = self.full_data[:, x1:x2 + 1]
            white_rows = (char == char.max()).all(axis=1)
            char = char[np.argmin(white_rows):
                        white_rows.size - np.argmin(white_rows[::-1])]
            x = int(np.floor((80 - char.shape[1]) / 2))
            y = int(np.floor((80 - char.shape[0]) / 2))
            _char_data[i, y:y + char.shape[0], x:x + char.shape[1]] = char
        return _char_data

    @property
    def char_indexes(self):
        """numpy.ndarray(int): Indexes of character images within series'
         deduplicated character image data"""
        flatten = lambda l: [item for sublist in l for item in sublist]

        char_indexes = sorted(flatten(
            self.series.spec[self.series.spec.apply(
                lambda x: np.any([self.index in [s for s, c in x["indexes"]]]),
                axis=1)].apply(
                lambda x: [(c, x.name) for s, c in x["indexes"]
                           if s == self.index],
                axis=1)))
        return [i for c, i in char_indexes]

    @property
    def char_predictions(self):
        """ndarray(float): Predicted confidence that each character image is
        each matchable character"""
        raise NotImplementedError()

    @property
    def char_separations(self):
        """ndarray(int): Widths of spaces between individual characters within
        subtitle"""
        if not hasattr(self, "_char_bounds"):
            self._initialize_char_bounds()
        return self.char_bounds[1:, 0] - self.char_bounds[:-1, 1]

    @property
    def char_spec(self):
        return self.series.spec.iloc[self.char_indexes]

    @property
    def char_widths(self):
        """ndarray(int): Widths of individual characters within subtitle"""
        if not hasattr(self, "_char_bounds"):
            self._initialize_char_bounds()
        return self.char_bounds[:, 1] - self.char_bounds[:, 0]

    @property
    def full_data(self):
        """str: Image data"""
        if not hasattr(self, "_full_data"):
            self._full_data = None
        return self._full_data

    @full_data.setter
    def full_data(self, value):
        if value is not None:
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

        self._full_data = value

    @property
    def img(self):
        """Image: Image of subtitle"""
        if not hasattr(self, "_img"):
            from PIL import Image

            if self.full_data is not None:
                if self.mode == "8 bit":
                    self._img = Image.fromarray(self.full_data)
                elif self.mode == "1 bit":
                    self._img = Image.fromarray(
                        self.full_data.astype(np.uint8) * 255,
                        mode="L").convert("1")
            else:
                raise ValueError()
        return self._img

    @property
    def index(self):
        if self.series is not None:
            return self.series.events.index(self)
        else:
            return None

    @property
    def series(self):
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

    def merge_chars(self, index):
        """
        Merges two adjacent characters

        Args:
            index (int): Index of first of two characters to merge
        """
        self._char_bounds = np.append(
            self.char_bounds.flatten()[:index * 2 + 1],
            self.char_bounds.flatten()[index * 2 + 3:]).reshape((-1, 2))

    def reconstruct_text(self):
        """"""
        chars = self.get_chars_of_labels(
            np.argsort(self.char_predictions, axis=1)[:, -1])
        text = ""
        items = zip(chars[:-1], chars[1:], self.char_widths[:-1],
                    self.char_widths[1:], self.char_separations)
        for i, (char_i, char_j, width_i, width_j, sep) in enumerate(items):
            text += char_i

            # Two Hanzi: separation cutoff of 40 to add double-width space
            if width_i >= 45 and width_j >= 45 and sep >= 40:
                # print("Adding a double-width space")
                text += "　"
            # Two Roman: separation cutoff of 35 to add single-width space
            elif width_i < 45 and width_j < 45 and sep >= 36:
                # print("Adding a single-width space")
                text += " "
        text += chars[-1]

        self.text = text
        # TODO: Improve handling of roman characters
        # TODO: Reconstruct ellipsis and any other characters that get split

    def save(self, path):
        self.img.save(path)

    def show(self):
        """
        Shows event image

        If called from within Jupyter notebook, shows inline. If imgcat module
        is available, shows inline in terminal. Otherwise opens a new window.
        """
        from scinoephile import in_ipython

        # Show image
        if in_ipython() == "ZMQInteractiveShell":
            from io import BytesIO
            from IPython.display import display, Image

            bytes = BytesIO()
            self.img.save(bytes, "png")
            display(Image(data=bytes.getvalue()))
        elif in_ipython() == "InteractiveShellEmbed":
            self.img.show()
        else:
            try:
                from imgcat import imgcat

                imgcat(self.img)
            except ImportError:
                self.img.show()

    # endregion

    # region Private Methods

    def _initialize_char_bounds(self):
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

    # endregion
