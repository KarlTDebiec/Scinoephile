#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.Metadata.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Adds Metadata
"""
################################### MODULES ###################################
import numpy as np
from scinoephile import CLToolBase


################################### CLASSES ###################################
class Metadata(CLToolBase):
    """
    Adds Metadata
    """

    # region Builtins

    def __init__(self, **kwargs):
        """
        Initializes command-line tool and compiles list of operations

        Args:
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        for k in sorted(kwargs.keys()):
            if kwargs[k] is not None:
                print(f"{k:>16s} |{kwargs[k]}|")
        # Date (take simple date in any parsable format, put into TZ format)
        # Description (can be a path to a file)
        # Genre (validate and set code)
        # Language (could detect automatically)
        # Rating (validate)
        # Studio (make into list with 'and")
        # Director (set both artist and plist)


    def __call__(self):
        """
        Performs operations
        """
        from IPython import embed

    # endregion

    # region Public Properties

    @property
    def operations(self):
        """dict: Collection of operations to perform, with associated
        arguments"""
        if not hasattr(self, "_operations"):
            self._operations = {}
        return self._operations

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

        # Input
        parser_input = parser.add_argument_group("input arguments")
        parser_input.add_argument("-if", "--infile",
                                  help="MP4 infile",
                                  metavar="FILE",
                                  required=True)

        # Metadata
        parser_metadata = parser.add_argument_group("metadata arguments")
        parser_metadata.add_argument("--title",
                                     help="Title of film")
        parser_metadata.add_argument("--date",
                                     help="Date of film's release")
        parser_metadata.add_argument("--description",
                                     help="Description of film")
        parser_metadata.add_argument("--genre",
                                     help="Genre of film")
        parser_metadata.add_argument("--language",
                                     action="append",
                                     help="Language of film")
        parser_metadata.add_argument("--rating",
                                     default="Unrated",
                                     help="Rating of film")
        parser_metadata.add_argument("--studio",
                                     action="append",
                                     help="Studio of film")
        parser_metadata.add_argument("--cast",
                                     action="append",
                                     help="Cast of film")
        parser_metadata.add_argument("--director",
                                     action="append",
                                     help="Director of film")
        parser_metadata.add_argument("--producer",
                                     action="append",
                                     help="Producer of film")
        parser_metadata.add_argument("--writer",
                                     action="append",
                                     help="Writer of film")

        # Operations
        parser_ops = parser.add_argument_group("operation arguments")
        parser_ops.add_argument("-i", "--interactive",
                                action="store_true",
                                help="show IPython prompt after loading and "
                                     "processing")

        # Output
        parser_output = parser.add_argument_group("output arguments")
        parser_output.add_argument("-of", "--outfile",
                                   help="MP4 outfile",
                                   metavar="FILE",
                                   required=True)
        parser_output.add_argument("-o", "--overwrite",
                                   action="store_true",
                                   help="overwrite outfiles if they exist")

        return parser

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    Metadata.main()
