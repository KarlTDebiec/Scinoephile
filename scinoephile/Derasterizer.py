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
from scinoephile import CLToolBase
from scinoephile.ocr import ImageSubtitleSeries


################################### CLASSES ###################################
class Derasterizer(CLToolBase):
    """
    Compiles Chinese and English subtitles
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
    def construct_argparser(cls, parser=None):
        """
        Constructs argument parser

        Returns:
            parser (argparse.ArgumentParser): Argument parser
        """
        import argparse

        if isinstance(parser, argparse.ArgumentParser):
            parser = parser
        elif isinstance(parser, argparse._SubParsersAction):
            parser = parser.add_parser(
                name=cls.__name__.lower(),
                description=__doc__,
                help=__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter)
        elif parser is None:
            parser = argparse.ArgumentParser(
                description=__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter)
        super().construct_argparser(parser)

        return parser

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    Derasterizer.main()
