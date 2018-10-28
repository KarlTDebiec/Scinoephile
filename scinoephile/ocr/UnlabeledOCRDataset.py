#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.UnlabeledOCRDataset,py
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
class UnlabeledOCRDataset(OCRDataset):
    """
    A collection of unlabeled character images
    """

    # region Public Properties

    @property
    def spec_cols(self):
        """list(str): Character image specification columns"""
        return ["path"]

    @property
    def spec_dtypes(self):
        """list(str): Character image specification dtypes"""
        return {"path": str}

    # endregion
