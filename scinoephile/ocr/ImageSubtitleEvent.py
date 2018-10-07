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
      - [ ] Decide if image should be a property
      - [ ] Document
    """

    # region Builtins

    def __init__(self, image=None, verbosity=None, **kwargs):
        super().__init__(**kwargs)

        self.image = image

        if verbosity is not None:
            self.verbosity = verbosity

    # endregion

    # region Public Methods

    def show(self):
        from PIL import Image

        if self.image is not None:
            Image.fromarray(self.image).show()
        else:
            raise ValueError()

    # endregion
