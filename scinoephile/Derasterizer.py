#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.Derasterizer.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Converts image-based subtitles into text using deep a neural network-based
optical character recognition model.
"""
################################### MODULES ###################################
import numpy as np
import pandas as pd
from os.path import expandvars, isfile
from IPython import embed
from scinoephile import CLToolBase, Metavar
from scinoephile.ocr import ImageSubtitleSeries


################################### CLASSES ###################################
class Derasterizer(CLToolBase):
    """
    Converts image-based subtitles to text
    """

    # region Builtins

    def __init__(self, **kwargs):
        """
        Initializes command-line tool

            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

    def __call__(self):
        """
        Performs operations
        """
        pass

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, **kwargs):
        """
        Constructs argument parser

        Returns:
            parser (argparse.ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__, **kwargs)

        # Files
        parser_file = parser.add_argument_group("file arguments")
        parser_file.add_argument("-i", "--infile", type=str,
                                 nargs="+",
                                 action=cls.get_filepath_action(),
                                 metavar="FILE",
                                 help="Input image-based subtitle file")
        parser_file.add_argument("-o", "--outfile", type=str,
                                 nargs="+",
                                 action=cls.get_filepath_action(),
                                 metavar="FILE",
                                 help="Output subtitle file")
        parser_file.add_argument("-s", "--standard", type=str,
                                 nargs="+",
                                 action=cls.get_filepath_action(),
                                 metavar=Metavar(["FILE", "overwrite"]),
                                 help="Standard subtitle file against which "
                                      "to compare results")
        # Model file for recognition

        # Operations
        parser_ops = parser.add_argument_group("operation arguments")
        # Segmentation_method (standard or dnn)

        return parser

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    Derasterizer.main()
