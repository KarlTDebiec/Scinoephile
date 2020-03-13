#!python
#   scinoephile.ocr.RecognitionDataset.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
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
            self._chars = hanzi_chars[:10]
        return self._chars

    @chars.setter
    def chars(self, value):
        # TODO: Validate
        if isinstance(value, int):
            value = np.array(hanzi_chars[:value])
        self._chars = value

    @property
    def data_shape(self):
        """numpy.ndarray(int): Image data shape"""
        return 80, 80

    # endregion

    # region Public Methods

    def get_labels_of_chars(self, chars):
        """
        Gets unique integer indexes of provided char strings

        Args:
            chars: Chars

        Returns:
             ndarray(int64): Labels
        """

        # Process arguments
        if isinstance(chars, str):
            if len(chars) == 1:
                return np.argwhere(self.chars == chars)[0, 0]
            elif len(chars) > 1:
                chars = list(chars)
        chars = np.array(chars)

        # Return labels
        sorter = np.argsort(self.chars)
        return np.array(
            sorter[np.searchsorted(self.chars, chars, sorter=sorter)])

    def get_chars_of_labels(self, labels):
        """
        Gets char strings of unique integer indexes

        Args:
            labels (ndarray(int64)): Labels

        Returns
            ndarray(U64): Chars
        """
        # TODO: Improve exception text

        # Process arguments and return chars
        if isinstance(labels, int):
            return self.chars[labels]
        elif isinstance(labels, np.ndarray):
            return self.chars[labels]
        else:
            try:
                return self.chars[np.array(labels)]
            except Exception as e:
                raise e

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
