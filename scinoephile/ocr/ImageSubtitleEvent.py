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
        """str: Images of individual characters """
        if not hasattr(self, "_char_bounds"):
            self._char_bounds = None
        return self._char_bounds

    @char_bounds.setter
    def char_bounds(self, value):
        if value is not None:
            import numpy as np

            if not isinstance(value, list):
                raise ValueError(self._generate_setter_exception(value))

        self._char_bounds = value

    @property
    def char_imagedata(self):
        """str: Images of individual characters """
        if not hasattr(self, "_char_imagedata"):
            self._char_imagedata = None
        return self._char_imagedata

    @char_imagedata.setter
    def char_imagedata(self, value):
        if value is not None:
            import numpy as np

            if not isinstance(value, list):
                raise ValueError(self._generate_setter_exception(value))

        self._char_imagedata = value

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

    def show(self, char_bounds=False):
        import numpy as np
        from PIL import Image, ImageDraw

        if self.imagedata is not None:
            if self.image_mode == "8 bit":
                image = Image.fromarray(self.imagedata)
            elif self.image_mode == "1 bit":
                image = Image.fromarray(self.imagedata.astype(np.uint8) * 255,
                                        mode="L").convert("1")
            if char_bounds:
                draw = ImageDraw.Draw(image)
                for bound in self.char_bounds[1:]:
                    draw.line((bound, 0, bound, image.size[1]), fill=0, width=2)
            image.show()
        else:
            raise ValueError()

    # endregion

    # region Private Methods

    def _find_char_bounds(self):
        import numpy as np

        threshold = 0.04
        if self.imagedata is None:
            return

        # Identify blank columns containing only white pixels
        nonwhite_pixels_in_column = (
                self.imagedata < self.imagedata.max()).sum(axis=0)
        blank_columns = np.where(nonwhite_pixels_in_column == 0)[0]
        if len(blank_columns) == 0:
            if self.verbosity >= 1:
                print("Whitespace between characters not found")
            # return

        embed(**self.embed_kw)

        # Identify boundaries between characters
        char_bounds = np.array([0])
        char_width = 75

        # Loop over characters in subtitle
        while True:
            # Estimate location of next boundary between characters
            next_bound = char_bounds[-1] + char_width
            if next_bound >= self.imagedata.size[0] - (char_width / 2):
                break

            # Identify blank columns closest to estimated boundary
            delta = np.abs(blank_columns - next_bound) / next_bound
            try:
                close = np.where(delta < threshold)[0]
                if close.size == 0:
                    close = np.where(delta < threshold * 2)[0]
                if close.size == 0:
                    close = np.where(delta < threshold * 3)[0]
                if close.size == 0:
                    # Look for half-width characters
                    next_bound -= 37
                    delta = np.abs(blank_columns - next_bound
                                   ) / next_bound
                    close = np.where(delta < threshold)[0]
                    if close.size == 0:
                        close = np.where(delta < threshold * 2)[0]
                    if close.size == 0:
                        close = np.where(delta < threshold * 3)[0]
                    if close.size == 0:
                        # Last-ditch check for very thin characters
                        next_bound -= 10
                        delta = np.abs(blank_columns - next_bound
                                       ) / next_bound
                        close = np.where(delta < threshold)[0]
                        if close.size == 0:
                            close = np.where(delta < threshold * 2)[0]
                        if close.size == 0:
                            close = np.where(delta < threshold * 3)[0]
                bound_index = int(np.median(close))
            except ValueError as e:
                if self.verbosity >= 1:
                    print("Problem finding spaces between characters")
                return

            bound = blank_columns[bound_index]

            # Add to list of boundaries, refine estimate of character
            #   width, and estimate location of next boundary
            char_bounds = np.append(char_bounds, bound)
            char_widths = (char_bounds[1:] - char_bounds[:-1])
            full_width_chars = np.extract(char_widths > 56, char_widths)
            if full_width_chars.size >= 1:
                char_width = np.mean(full_width_chars)
            else:
                char_width = 75
        char_bounds = np.append(char_bounds, self.imagedata.size[0])

    # endregion
