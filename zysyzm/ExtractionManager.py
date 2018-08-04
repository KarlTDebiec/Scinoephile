#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.ExtractionManager.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from IPython import embed
from zysyzm.CLToolBase import CLToolBase


################################### CLASSES ###################################
class ExtractionManager(CLToolBase):
    """ Extracs characters from image-based subtitles """

    # region Instance Variables
    help_message = ("Extracts characters from image-based subtitles")

    # endregion

    # region Builtins
    def __call__(self):
        from os.path import expandvars

        infile = "${DROPBOX}/code/test/cmn-Hans-0002.png"

        from PIL import Image, ImageChops
        im = Image.open(expandvars(infile))

        def trim(image):
            background = Image.new(image.mode, image.size,
                                   image.getpixel((0, 0)))
            diff = ImageChops.difference(image, background)
            diff = ImageChops.add(diff, diff, 2.0, -100)
            bbox = diff.getbbox()
            if bbox:
                return image.crop(bbox)

        im = trim(im)

        # Interactive
        if self.interactive:
            embed()

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    ExtractionManager.main()
