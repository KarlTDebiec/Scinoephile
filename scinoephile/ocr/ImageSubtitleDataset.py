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
from IPython import embed


################################### CLASSES ###################################
class ImageSubtitleDataset(SubtitleDataset):
    """
    Extracts individual characters from image-based subtitles

    TODO:
      - [x] Open SUP file and loop over bytes
      - [x] Read images
      - [x] Read and apply image palettes
      - [x] Read times and locations
      - [ ] Store times and locations in hdf5 or text
      - [ ] Store images in hdf5
      - [ ] Think about using a metaclass
      - [ ] Document
    """

    # region Instance Variables
    help_message = ("Tool for extracting individual characters from"
                    "image-based subtitles")

    # endregion

    # region Builtins
    def __init__(self, infile=None, outfile=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if infile is not None:
            self.infile = infile
        if outfile is not None:
            self.outfile = outfile

        # Temporary manual configuration for testing
        self.infile = "/Users/kdebiec/Dropbox/code/subtitles/" \
                      "magnificent_mcdull/original/" \
                      "Magnificent Mcdull.3.zho.sup"
        self.outfile = "/Users/kdebiec/Dropbox/code/subtitles/" \
                       "magnificent_mcdull/" \
                       "mcdull.h5"
        self.infile = self.outfile
        self.outfile = None

    # endregion

    # region Private Properties

    @property
    def _series_class(self):
        from scinoephile.ocr import ImageSubtitleSeries

        return ImageSubtitleSeries

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    ImageSubtitleDataset.main()
