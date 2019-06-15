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
from tensorflow import keras
from IPython import embed
from scinoephile import CLToolBase, Metavar, SubtitleSeries
from scinoephile.ocr import ImageSubtitleSeries


################################### CLASSES ###################################
class Derasterizer(CLToolBase):
    """
    Converts image-based subtitles to text
    """

    # region Builtins

    def __init__(self, infile, recognition_model, outfile=None, standard=None,
                 **kwargs):
        """
        Initializes command-line tool

            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Catalogue input and output operations
        # TODO: Add useful exception text
        infile = expandvars(infile)
        if isfile(infile):
            self.operations["load_infile"] = infile
        else:
            raise ValueError()
        recognition_model = expandvars(recognition_model)
        if isfile(recognition_model):
            self.operations["load_recognition_model"] = recognition_model
        else:
            raise ValueError()
        if outfile is not None:
            outfile = expandvars(outfile)
            self.operations["save_outfile"] = outfile
        if standard is not None:
            standard = expandvars(standard)
            self.operations["load_standard"] = standard

    def __call__(self):
        """
        Performs operations
        """

        # Read infiles
        if "load_infile" in self.operations:
            self.image_subtitles = ImageSubtitleSeries.load(
                self.operations["load_infile"])
        if "load_recognition_model" in self.operations:
            self.recognition_model = keras.models.load_model(
                self.operations["load_recognition_model"])
        if "load_standard" in self.operations:
            self.standard_subtitles = SubtitleSeries.load(
                self.operations["load_standard"])

        # Perform operations
        from IPython import embed
        embed(**self.embed_kw)

        # Write outfiles
        if "save_outfile" in self.operations:
            self.image_subtitles.save(self.operations["save_outfile"])

    # endregion

    # region Public Properties

    @property
    def image_subtitles(self):
        """ImageSubtitleSeries: Image-based subtitles"""
        if not hasattr(self, "_image_subtitles"):
            self._image_subtitles = None
        return self._image_subtitles

    @image_subtitles.setter
    def image_subtitles(self, value):
        if not isinstance(value, ImageSubtitleSeries):
            raise ValueError(self._generate_setter_exception(value))
        self._image_subtitles = value

    @property
    def operations(self):
        """dict: Collection of operations to perform, with associated
        arguments"""
        if not hasattr(self, "_operations"):
            self._operations = {}
        return self._operations

    @property
    def recognition_model(self):
        """Model: Character recognition model"""
        if not hasattr(self, "_recognition_model"):
            raise ValueError()
        return self._recognition_model

    @recognition_model.setter
    def recognition_model(self, value):
        if not isinstance(value, keras.Model):
            raise ValueError(self._generate_setter_exception(value))
        self._recognition_model = value

    @property
    def standard_subtitles(self):
        """SubtitleSeries: Standard subtitles against which to compare
        results"""
        if not hasattr(self, "_standard_subtitles"):
            self._standard_subtitles = None
        return self._standard_subtitles

    @standard_subtitles.setter
    def standard_subtitles(self, value):
        if not isinstance(value, SubtitleSeries):
            raise ValueError(self._generate_setter_exception(value))
        self._standard_subtitles = value

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
                                 nargs="+", required=True,
                                 action=cls.get_filepath_action(),
                                 metavar="FILE",
                                 help="Input image-based subtitle file")
        parser_file.add_argument("-m", "--model", type=str,
                                 nargs="+",
                                 action=cls.get_filepath_action(),
                                 metavar="FILE", dest="recognition_model",
                                 help="Input model file")
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
