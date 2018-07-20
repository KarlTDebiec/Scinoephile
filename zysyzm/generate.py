#!/usr/bin/python
# -*- coding: utf-8 -*-
#   generate.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython import embed

################################## SETTINGS ###################################
pd.set_option("display.width", 110)
pd.set_option("display.max_colwidth", 16)
pd.set_option("display.max_rows", None)


################################### CLASSES ###################################
class DataGenerationManager(object):
    """
    Class for managing subtitles

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

        TODO:
            - Decide between setting within each function or returning
            - Move actual merging to another function 'complile_subtitles'
        """

        # Interactive
        if self.interactive:
            embed()

    # endregion

    # region Properties
    @property
    def directory(self):
        """str: Path to this Python file"""
        if not hasattr(self, "_directory"):
            import os
            self._directory = os.path.dirname(os.path.realpath(__file__))
        return self._directory

    @property
    def interactive(self):
        """bool: Present IPython prompt after processing subtitles"""
        if not hasattr(self, "_interactive"):
            self._interactive = False
        return self._interactive

    @interactive.setter
    def interactive(self, value):
        if not isinstance(value, bool):
            raise ValueError()
        self._interactive = value

    @property
    def verbosity(self):
        """int: Level of output to provide"""
        if not hasattr(self, "_verbosity"):
            self._verbosity = 1
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value):
        if not isinstance(value, int) and value >= 0:
            raise ValueError()
        self._verbosity = value

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

        help_message = ("Help message")

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

    @staticmethod
    def validate_args(parser, args):
        """
        Validates arguments

        Args:
            parser (argparse.ArgumentParser): Argument parser
            args: Arguments

        """
        pass

    # endregion

    @classmethod
    def main(cls):
        """
        Parses and validates arguments, constructs and calls object

        """

        parser = cls.construct_argparser()
        args = parser.parse_args()
        cls.validate_args(parser, args)
        cls(**vars(args))()


#################################### MAIN #####################################
if __name__ == "__main__":
    DataGenerationManager.main()
