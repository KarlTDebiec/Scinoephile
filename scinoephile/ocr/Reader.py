#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.Reader.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile import CLToolBase
from IPython import embed


################################### CLASSES ###################################
class Reader(CLToolBase):
    """
    Extracts individual characters from image-based subtitles
    """

    # region Instance Variables
    help_message = ("Tool for extracting individual characters from"
                    "image-based subtitles")

    # endregion

    # region Builtins
    def __init__(self, input_sub=None, output_hdf5=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if input_sub is not None:
            self.input_sub = input_sub
        if output_hdf5 is not None:
            self.output_hdf5 = output_hdf5

        # Temporary manual configuration for testing
        self.input_sub = \
            "/Users/kdebiec/Dropbox/code/subtitles/spirited_away/original/en-US.sup"

    def __call__(self):
        """Core logic"""

        with open(self.input_sub, "rb") as infile:
            embed(**self.embed_kw)

    # endregion

    # region Properties
    @property
    def input_sup(self):
        """str: Path to input hdf5 file"""
        if not hasattr(self, "_input_sup"):
            self._input_sup = None
        return self._input_sup

    @input_sup.setter
    def input_sup(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._input_sup = value

    @property
    def output_hdf5(self):
        """str: Path to output hdf5 file"""
        if not hasattr(self, "_output_hdf5"):
            self._output_hdf5 = None
        return self._output_hdf5

    @output_hdf5.setter
    def output_hdf5(self, value):
        from os import access, getcwd, R_OK, W_OK
        from os.path import dirname, expandvars, isfile

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
            elif isfile(value) and not access(value, R_OK):
                raise ValueError(self._generate_setter_exception(value))
            elif dirname(value) == "" and not access(getcwd(), W_OK):
                raise ValueError(self._generate_setter_exception(value))
            elif not access(dirname(value), W_OK):
                raise ValueError(self._generate_setter_exception(value))
        self._output_hdf5 = value

    # endregion

    # region Class Methods

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    Reader.main()
