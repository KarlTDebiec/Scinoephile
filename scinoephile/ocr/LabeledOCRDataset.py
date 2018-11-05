#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.LabeledOCRDataset,py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile.ocr import OCRDataset
from IPython import embed


################################### CLASSES ###################################
class LabeledOCRDataset(OCRDataset):
    """
    A collection of labeled character images
    """

    # region Builtins

    def __init__(self, n_chars=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if n_chars is not None:
            self.n_chars = n_chars

    # endregion

    # region Public Properties

    @property
    def figure(self):
        """Figure: Temporary figure used for images"""
        if not hasattr(self, "_figure"):
            from matplotlib.pyplot import figure

            self._figure = figure(figsize=(1.0, 1.0), dpi=80)
        return self._figure

    @property
    def labels(self):
        """ndarray: Labels of chars in dataset"""
        return self.get_labels_of_chars(self.spec["char"].values)

    @property
    def n_chars(self):
        """int: Number of unique characters to support"""
        if not hasattr(self, "_n_chars"):
            self._n_chars = 10
        return self._n_chars

    @n_chars.setter
    def n_chars(self, value):
        if value is not None:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except Exception as e:
                    raise ValueError(self._generate_setter_exception(value))
            if value < 1:
                raise ValueError(self._generate_setter_exception(value))
        self._n_chars = value

    @property
    def spec_cols(self):
        """list(str): Character image specification columns"""
        return ["char"]

    @property
    def spec_dtypes(self):
        """list(str): Character image specification dtypes"""
        return {"char": str}

    # endregion

    # region Public Methods

    def get_present_specs_of_char(self, char):
        return self.spec.loc[self.spec["char"] == char].drop("char", axis=1)

    def get_present_specs_of_char_set(self, char):
        return set(map(tuple, self.spec.loc[self.spec["char"] == char].drop(
            "char", axis=1).values))

    # endregion
