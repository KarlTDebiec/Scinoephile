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

    # region Public Properties

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

    def get_images_and_labels(self, indexes=None):
        """
        if indexes is None:
            img = self.data
            lbl = self.chars_to_labels(self.spec["char"].values)
        else:
            img = self.data[indexes]
            lbl = self.chars_to_labels(self.spec["char"].loc[indexes].values)

        return img, lbl
        """
        return NotImplementedError()

    # endregion
