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
import numpy as np
import pandas as pd
from IPython import embed
from zysyzm.CLToolBase import CLToolBase

################################## SETTINGS ###################################
pd.set_option("display.width", 110)
pd.set_option("display.max_colwidth", 16)
pd.set_option("display.max_rows", None)


################################### CLASSES ###################################
class ExtractionManager(CLToolBase):
    """
    Class for extracting individual characters from a collection of subtitles

    """

    # region Instance Variables

    # endregion

    # region Builtins
    def __init__(self, verbosity=1, interactive=False, **kwargs):
        self.verbosity = verbosity
        self.interactive = interactive

    def __call__(self):
        """
        Core logic
        """

        from os.path import expandvars

        infile = "${DROPBOX}/code/test/cmn-Hans-0002.png"

        from PIL import Image, ImageChops
        im = Image.open(expandvars(infile))

        def trim(image):
            background = Image.new(image.mode, image.size, image.getpixel((0, 0)))
            diff = ImageChops.difference(image, bg)
            diff = ImageChops.add(diff, diff, 2.0, -100)
            bbox = diff.getbbox()
            if bbox:
                return image.crop(bbox)

        im = trim(im)

        # Interactive
        if self.interactive:
            embed()

    # endregion

    # region Properties

    # endregion Properties

    # region Methods

    # endregion

    # region Static Methods
    @staticmethod
    def construct_argparser():
        """
        Prepares argument parser

        Returns:
            parser (argparse.ArgumentParser): Argument parser
        """
        import argparse

        help_message = ("ExtractionManager.py")

        parser = argparse.ArgumentParser(description=help_message)

        # General
        verbosity = parser.add_mutually_exclusive_group()
        verbosity.add_argument("-v", "--verbose", action="count",
                               dest="verbosity", default=1,
                               help="enable verbose output, may be specified "
                                    "more than once")
        verbosity.add_argument("-q", "--quiet", action="store_const",
                               dest="verbosity", const=0,
                               help="disable verbose output")
        parser.add_argument("-i", "--interactive", action="store_true",
                            dest="interactive",
                            help="present IPython prompt after loading and "
                                 "processing")

        # Input

        # Operation

        # Output

        return parser

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    ExtractionManager.main()
