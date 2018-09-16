#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.SubtitleDataset.py
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
class SubtitleDataset(CLToolBase):
    """
    Represents a collection of subtitles

    Todo:
      - [ ] Read from SRT/VTT
      - [ ] Write to SRT/VTT
      - [ ] Reindex
      - [ ] Document
    """

    # region Instance Variables

    help_message = ("Represents a collection of subtitles")

    # endregion

    # region Builtins

    def __init__(self, input_srt=None, output_srt=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if input_srt is not None:
            self.input_srt = input_srt
        if output_srt is not None:
            self.output_srt = output_srt

    def __call__(self):
        """ Core logic """
        pass

    # endregion

    # region Public Properties

    @property
    def input_srt(self):
        """str: Path to input srt file"""
        if not hasattr(self, "_input_srt"):
            self._input_srt = None
        return self._input_srt

    @input_srt.setter
    def input_srt(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._input_srt = value

    @property
    def output_srt(self):
        """str: Path to output srt file"""
        if not hasattr(self, "_output_srt"):
            self._output_srt = None
        return self._output_srt

    @output_srt.setter
    def output_srt(self, value):
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
        self._output_srt = value

    # endregion

    # region Private Properties

    # endregion

    # region Public Methods

    # endregion

    # region Private Methods

    # endregion
