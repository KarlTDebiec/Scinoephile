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
            self._initialize_char_data()
        return self._char_bounds

    @property
    def char_count(self):
        """int: Number of individual characters within subtitle"""
        return self.char_data.shape[0]

    @property
    def char_data(self):
        """ndarray: Image data of individual characters within subtitle"""
        if not hasattr(self, "_char_data"):
            self._initialize_char_data()
        return self._char_data

    @property
    def char_indexes(self):
        """numpy.ndarray(bool): Indexes of character images within
        SubtitleSeries' deduplicated character image data"""
        if not hasattr(self, "_char_indexes"):
            self._char_indexes = None
        return self._char_indexes

    @char_indexes.setter
    def char_indexes(self, value):
        if not isinstance(value, np.ndarray):
            try:
                value = np.array(value, np.int)
            except:
                raise ValueError(self._generate_setter_exception(value))
        if value.ndim != 1:
            raise ValueError(self._generate_setter_exception(value))
        if value.size != self.char_count:
            raise ValueError(self._generate_setter_exception(value))
        self._char_indexes = value

    @property
    def char_predictions(self):
        """ndarray(float): Predicted confidence that each character image is
        each matchable character"""
        if not hasattr(self, "_char_predictions"):
            self._char_predictions = None
        return self._char_predictions

    @char_predictions.setter
    def char_predictions(self, value):
        if not isinstance(value, np.ndarray):
            embed(**self.embed_kw)
            raise ValueError(self._generate_setter_exception(value))
        if value.shape[0] != self.char_data.shape[0]:
            embed(**self.embed_kw)
            raise ValueError(self._generate_setter_exception(value))
        self._char_predictions = value

    @property
    def char_separations(self):
        """ndarray(int): Spaces between individual characters within subtitle"""
        return self.char_bounds[1:, 0] - self.char_bounds[:-1, 1]

    @property
    def char_widths(self):
        """ndarray(int): Widths of individual characters within subtitle"""
        if not hasattr(self, "_char_widths"):
            self._char_widths = self.char_bounds[:, 1] - self.char_bounds[:, 0]
        return self._char_widths

    @property
    def full_data(self):
        """str: Image data"""
        if not hasattr(self, "_full_data"):
            self._full_data = None
        return self._full_data

    @full_data.setter
    def full_data(self, value):
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

        self._full_data = value

    @property
    def img(self):
        """Image: Image of subtitle"""
        if not hasattr(self, "_img"):
            import numpy as np
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

    # endregion

    # region Public Methods

    def predict(self, model):
        """
        Predicts confidence that each character image is each matchable
        chararcter

        Arguments:
            model(model?): TensorFlow model with which to predict characters
        """
        self.char_predictions = model.model.predict(self.char_data)

    def reconstruct_text(self):
        import numpy as np

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
        Shows image of subtitle
        """
        self.img.show()

    def show_predictions(self):
        for i in range(self.char_count):
            poss_lbls = np.argsort(self.char_predictions[i])[::-1]
            poss_chars = self.get_chars_of_labels(poss_lbls)
            poss_probs = np.round(self.char_predictions[i][poss_lbls], 2)
            matches = [f"{a}:{b:4.2f}" for a, b in
                       zip(poss_chars[:10], poss_probs[:10])]
            print(f"{i} | {' '.join(matches)}")

    # endregion

    # region Private Methods

    def _initialize_char_data(self):
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

        if self.mode == "8 bit":
            chars = np.ones((self.char_bounds.shape[0], 80, 80),
                            np.uint8) * 255
        elif self.mode == "1 bit":
            chars = np.ones((self.char_bounds.shape[0], 80, 80),
                            np.bool)
        for i, (x1, x2) in enumerate(self.char_bounds):
            char = self.full_data[:, x1:x2 + 1]
            white_rows = (char == char.max()).all(axis=1)
            char = char[np.argmin(white_rows):
                        white_rows.size - np.argmin(white_rows[::-1])]
            x = int(np.floor((80 - char.shape[1]) / 2))
            y = int(np.floor((80 - char.shape[0]) / 2))
            chars[i, y:y + char.shape[0], x:x + char.shape[1]] = char
        self._char_data = chars

    # endregion
