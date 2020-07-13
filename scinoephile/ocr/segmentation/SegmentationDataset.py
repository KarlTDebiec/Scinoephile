#!/usr/bin/env python3
#   scinoephile.ocr.SegmentationDataset.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from abc import ABC
from scinoephile import todo
from scinoephile.ocr import OCRDataset


################################### CLASSES ###################################
class SegmentationDataset(OCRDataset, ABC):
    """
    Base dataset for character segmentation
    """

    # region Public Properties

    @property
    def data_shape(self):
        """numpy.ndarray(int): Image data shape"""
        return 1600, 80

    # endregion

    # region Public Methods

    @todo
    def show(self, indexes=None, data=None, **kwargs):
        """
        Shows selected images

        If called from within Jupyter notebook, shows inline. If called from
        within terminal and imgcat module is available, shows inline.
        Otherwise opens a new window.

        Args:
            indexes (int, list, ndarray, optional): Indexes of images to show;
              defaults to all
            data (ndarray, optional): Image data to show; defaults to self.data
            **kwargs: Additional keyword arguments
        """
        pass

    # endregion
