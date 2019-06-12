#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.RecognitionDataset.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import numpy as np
from abc import ABC
from scinoephile.ocr import hanzi_chars, OCRDataset


################################### CLASSES ###################################
class RecognitionDataset(OCRDataset, ABC):
    """
    Base dataset for character recognition
    """

    # region Public Properties

    @property
    def chars(self):
        """list(str): Characters that may be present in this dataset"""
        if not hasattr(self, "_chars"):
            from scinoephile.ocr import hanzi_chars
            self._chars = list(hanzi_chars[:10])
        return self._chars

    @chars.setter
    def chars(self, value):
        # TODO: Validate
        if isinstance(value, int):
            value = list(hanzi_chars[:value])
        self._chars = value

    @property
    def data_shape(self):
        """numpy.ndarray(int): Image data shape"""
        return 80, 80

    # endregion

    # region Public Methods

    def get_present_specs_of_char(self, char, as_set=True):
        if as_set:
            return set(map(tuple, self.spec.loc[
                self.spec["char"] == char].drop("char", axis=1).values))
        else:
            return self.spec.loc[
                self.spec["char"] == char].drop("char", axis=1)

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
        from scinoephile.ocr import draw_char_imgs, show_img

        # Process arguments
        if data is None:
            data = self.data
        if indexes is None:
            indexes = range(data.shape[0])
        elif isinstance(indexes, int):
            indexes = [indexes]
        indexes = np.array(indexes, np.int)
        if np.any(indexes >= data.shape[0]):
            raise ValueError()
        data = data[indexes]

        # Draw image
        img = draw_char_imgs(data, **kwargs)

        # Show image
        show_img(img, **kwargs)

    # endregion
