#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.TestOCRDataset,py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import pandas as pd
import numpy as np
from collections import OrderedDict
from IPython import embed
from scinoephile.ocr import hanzi_chars, get_labels_of_chars, OCRDataset


################################### CLASSES ###################################
class TestOCRDataset(OCRDataset):
    """
    A collection of labeled character images for testing
    """

    # region Builtins

    def __init__(self, chars=None, subtitle_series=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if chars is not None:
            self.chars = chars
        if subtitle_series is not None:
            self.subtitle_series = subtitle_series

    # endregion

    # region Public Properties

    @property
    def spec_dtypes(self):
        """OrderedDict(str, type): Names and dtypes of columns in spec"""
        return OrderedDict(char=str, indexes=object)

    @property
    def subtitle_series(self):
        """list(str): Characters that may be present in this dataset"""
        if not hasattr(self, "_subtitle_series"):
            self._subtitle_series = None
        return self._subtitle_series

    @subtitle_series.setter
    def subtitle_series(self, value):
        # TODO: Validate
        if not isinstance(value, list):
            value = [value]
        self._subtitle_series = value
        self._initialize_char_data()

    # endregion

    # region Public Properties

    def get_data_for_tensorflow(self):

        img = self.data.astype(np.float16) / 255.0
        lbl = get_labels_of_chars(self.spec["char"].values)

        return img, lbl

    # endregion

    # region Private Methods

    def _initialize_char_data(self):
        """
        Initializes deduplicated character image data structure
        """
        if self.verbosity >= 1:
            print("Initializing character data structures")

        for i, series in enumerate(self.subtitle_series):
            indexes = series.spec["char"].apply(lambda c: c in self.chars)

            spec = series.spec[indexes].copy()
            spec = spec.drop(columns="indexes")
            spec["indexes"] = [(i, v) for v in spec.index.values]
            data = series.data[indexes]

            self.add_img(spec, data)

    # endregion
