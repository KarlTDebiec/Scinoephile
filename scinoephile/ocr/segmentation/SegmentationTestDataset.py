#!python
#   scinoephile.ocr.SegmentationTestDataset,py
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
from scinoephile.ocr.segmentation import SegmentationDataset


################################### CLASSES ###################################
class SegmentationTestDataset(SegmentationDataset, OCRTestDataset):
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
        return OrderedDict(text=str, char_bounds=np.ndarray)

    # endregion

    # region Public Properties

    @todo
    def get_data_for_tensorflow(self, val_portion=0.1):
        pass

    # endregion

    # region Private Methods

    @todo
    def _initialize_data(self):
        """
        Initializes image data structure
        """
        pass

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
            SegmentationTestDataset: Loaded dataset
        """
        pass

    # endregion
