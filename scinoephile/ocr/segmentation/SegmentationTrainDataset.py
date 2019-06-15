#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.SegmentationTrainDataset,py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from collections import OrderedDict
from scinoephile import todo
from scinoephile.ocr import OCRTrainDataset
from scinoephile.ocr.segmentation import SegmentationDataset


################################### CLASSES ###################################
class SegmentationTrainDataset(SegmentationDataset, OCRTrainDataset):
    """
    A collection of subtitle images for training
    """

    # region Public Properties

    @property
    def spec_dtypes(self):
        """OrderedDict(str, type): Names and dtypes of columns in spec"""
        return OrderedDict(text=str, font=str, size=int, width=int,
                           x_offset=int, y_offset=int)

    # endregion

    # region Public Methods

    @todo
    def generate_training_data(self):
        pass

    @todo
    def get_data_for_tensorflow(self, val_portion=0.1):
        pass

    # endregion

    # region Private Methods

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
            SegmentationTrainDataset: Loaded dataset
        """
        pass

    # endregion
