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

    # endregion
