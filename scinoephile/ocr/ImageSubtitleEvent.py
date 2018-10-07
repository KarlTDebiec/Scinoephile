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
from IPython import embed


################################### CLASSES ###################################
class ImageSubtitleEvent(SubtitleEvent):
    """
    Subtitle event that includes an image

    TODO:
      - [ ] Move over code for splitting subtitle into separate characters
      - [ ] Determine if this needs an image_mode property
      - [ ] Document
    """

    # region Builtins

    def __init__(self, image_mode=None, imagedata=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if image_mode is not None:
            self.image_mode = image_mode
        if imagedata is not None:
            self.imagedata = imagedata

    # endregion

    # region Public Properties

    @property
    def char_bounds(self):
        """array(int): Boundaries of individual characters """
        if not hasattr(self, "_char_bounds"):
            import numpy as np

            # Works for both 8 bit and 1 bit
            white_cols = (self.imagedata == self.imagedata.max()).all(axis=0)
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
        """str: Images of individual characters """
        if not hasattr(self, "_char_widths"):
            self._char_widths = self.char_bounds[:, 1] - self.char_bounds[:, 0]
        return self._char_widths

    @property
    def char_imagedata(self):
        """str: Images of individual characters """
        if not hasattr(self, "_char_imagedata"):
            import numpy as np

            if self.image_mode == "8 bit":
                raise NotImplementedError()
            elif self.image_mode == "1 bit":
                chars = np.ones((self.char_bounds.shape[0], 80, 80),
                                np.bool)
                for i, (x1, x2) in enumerate(self.char_bounds):
                    char = self.imagedata[:, x1:x2 + 1]
                    white_rows = (char == char.max()).all(axis=1)
                    char = char[np.argmin(white_rows):
                                white_rows.size - np.argmin(white_rows[::-1])]
                    x = int(np.floor((80 - char.shape[1]) / 2))
                    y = int(np.floor((80 - char.shape[0]) / 2))
                    chars[i, y:y + char.shape[0], x:x + char.shape[1]] = char
                self._char_imagedata = chars
        return self._char_imagedata

    @property
    def image_mode(self):
        """str: Image mode"""
        if not hasattr(self, "_image_mode"):
            self._image_mode = "1 bit"
        return self._image_mode

    @image_mode.setter
    def image_mode(self, value):
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
        # TODO: If changed, set self.imagedata = self.imagedata to convert

        self._image_mode = value

    @property
    def imagedata(self):
        """str: Image """
        if not hasattr(self, "_imagedata"):
            self._imagedata = None
        return self._imagedata

    @imagedata.setter
    def imagedata(self, value):
        if value is not None:
            import numpy as np
            from PIL import Image

            if not isinstance(value, np.ndarray):
                raise ValueError(self._generate_setter_exception(value))

            if self.image_mode == "8 bit":
                if len(value.shape) == 3:
                    trans_bg = Image.fromarray(value)
                    white_bg = Image.new("RGBA", trans_bg.size,
                                         (255, 255, 255, 255))
                    white_bg.paste(trans_bg, mask=trans_bg)
                    value = np.array(white_bg.convert("L"))
            elif self.image_mode == "1 bit":
                if len(value.shape) == 3:
                    trans_bg = Image.fromarray(value)
                    white_bg = Image.new("RGBA", trans_bg.size,
                                         (255, 255, 255, 255))
                    white_bg.paste(trans_bg, mask=trans_bg)
                    value = np.array(white_bg.convert("1", dither=0))
            else:
                raise ValueError(self._generate_setter_exception(value))

        self._imagedata = value

    # endregion

    # region Public Methods

    def show(self):
        import numpy as np
        from PIL import Image

        if self.imagedata is not None:
            if self.image_mode == "8 bit":
                image = Image.fromarray(self.imagedata)
            elif self.image_mode == "1 bit":
                image = Image.fromarray(self.imagedata.astype(np.uint8) * 255,
                                        mode="L").convert("1")
            image.show()
        else:
            raise ValueError()

    # endregion
