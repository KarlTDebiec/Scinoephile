#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.TestOCRDataset,py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile.ocr import UnlabeledOCRDataset
from IPython import embed


################################### CLASSES ###################################
class TestOCRDataset(UnlabeledOCRDataset):
    """
    A collection of unlabeled character images
    """

    # region Builtins

    def __init__(self, n_chars=None, sub_ds=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if n_chars is not None:
            self.n_chars = n_chars

        if sub_ds is not None:
            self.sub_ds = sub_ds

    def __call__(self):
        """ Core logic """

        # Input
        if self.infile is not None:
            self.load()

        # Output
        if self.outfile is not None:
            self.save()

        # Present IPython prompt
        if self.interactive:
            embed(**self.embed_kw)

    # endregion

    # region Public Properties
    @property
    def data(self):
        """ndarray: Image data of individual characters within subtitles"""
        return self.sub_ds.char_data

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
        return ["path"]

    @property
    def spec_dtypes(self):
        """list(str): Character image specification dtypes"""
        return {"path": str}

    @property
    def sub_ds(self):
        """scinoephile.ocr.ImageSubtitleDataset: Source subtitles"""
        if not hasattr(self, "_sub_ds"):
            self._sub_ds = None
        return self._sub_ds

    @sub_ds.setter
    def sub_ds(self, value):
        from scinoephile.ocr import ImageSubtitleDataset

        if value is not None:
            if not isinstance(value, ImageSubtitleDataset):
                raise ValueError(self._generate_setter_exception(value))
        self._sub_ds = value

    # endregion

    # region Private Methods

    def _load_hdf5(self, fp, **kwargs):
        pass

    def _save_hdf5(self, fp, **kwargs):
        pass

    # endregion
