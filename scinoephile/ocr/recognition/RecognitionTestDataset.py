#!/usr/bin/env python3
#   scinoephile.ocr.RecognitionTestDataset,py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import numpy as np
from collections import OrderedDict
from scinoephile import todo
from scinoephile.ocr import OCRTestDataset
from scinoephile.ocr.recognition import RecognitionDataset


################################### CLASSES ###################################
class RecognitionTestDataset(RecognitionDataset, OCRTestDataset):
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

    # endregion

    # region Public Properties

    def get_data_for_tensorflow(self):

        img = self.data.astype(np.float16) / 255.0
        lbl = self.get_labels_of_chars(self.spec["char"].values)

        return img, lbl

    # endregion

    # region Private Methods

    def _initialize_data(self):
        """
        Initializes image data structure
        """
        if self.verbosity >= 1:
            print("Initializing character data structures")

        for i, series in enumerate(self.subtitle_series):
            indexes = series.spec["char"].apply(lambda c: c in self.chars)

            spec = series.spec[indexes].copy()
            spec = spec.drop(columns="indexes")
            spec["indexes"] = [(i, v) for v in spec.index.values]
            data = series.data[indexes]

            self.append(spec, data)

    @todo
    def _save_hdf5(self, fp, **kwargs):
        """
        Saves images to an output hdf5 file

        Args:
            fp (h5py._hl.files.File): Open hdf5 output file
            **kwargs: Additional keyword arguments
        """
        pass

    # endregion

    # region Private Class Methods

    @classmethod
    @todo
    def _load_hdf5(cls, fp, verbosity=1, **kwargs):
        """
        Loads dataset from an input hdf5 file

        Args:
            fp (h5py._hl.files.File): Open hdf5 input file
            verbosity (int, optional): Level of verbose output
            **kwargs: Additional keyword arguments

        Returns:
            RecognitionTestDataset: Loaded dataset
        """
        pass

    # endregion
