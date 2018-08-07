#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.ocr.TestDataCollector.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from zysyzm.ocr import OCRCLToolBase


################################### CLASSES ###################################
class TestDataCollector(OCRCLToolBase):
    """Collects test data based on interim model"""

    # region Properties
    @property
    def n_chars(self):
        """int: Number of characters to seek test data for"""
        if not hasattr(self, "_n_chars"):
            self._n_chars = 43
        return self._n_chars

    @n_chars.setter
    def n_chars(self, value):
        if not isinstance(value, int) and value is not None:
            try:
                value = int(value)
            except Exception as e:
                raise ValueError()
        if value < 1 and value is not None:
            raise ValueError()
        self._n_chars = value

    @property
    def tst_output_directory(self):
        """str: Path to directory for output test character images"""
        if not hasattr(self, "_tst_output_directory"):
            self._tst_output_directory = None
        return self._tst_output_directory

    @tst_output_directory.setter
    def tst_output_directory(self, value):
        from os import makedirs
        from os.path import expandvars, isdir

        if not isinstance(value, str) and value is not None:
            raise ValueError()
        elif isinstance(value, str):
            value = expandvars(value)
            if not isdir(value):
                try:
                    makedirs(value)
                except Exception as e:
                    raise ValueError()
        self._tst_output_directory = value

    @property
    def tst_input_directory(self):
        """str: Path to directory containing input subtitle images"""
        if not hasattr(self, "_tst_input_directory"):
            self._tst_input_directory = None
        return self._tst_input_directory

    @tst_input_directory.setter
    def tst_input_directory(self, value):
        from os.path import expandvars, isdir

        if not isinstance(value, str) and value is not None:
            raise ValueError()
        elif isinstance(value, str):
            value = expandvars(value)
            if not isdir(value):
                raise ValueError()
        self._tst_input_directory = value
    # endregion
