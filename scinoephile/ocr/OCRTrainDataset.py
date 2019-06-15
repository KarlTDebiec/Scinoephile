#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.TrainOCRDataset,py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from abc import abstractmethod, ABC
from scinoephile.ocr import OCRDataset


################################### CLASSES ###################################
class OCRTrainDataset(OCRDataset, ABC):
    """
    A collection of images for training
    """

    # region Builtins

    def __init__(self, chars=None, font_names=None, font_sizes=None,
                 font_widths=None, x_offsets=None, y_offsets=None,
                 **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if chars is not None:
            self.chars = chars
        if font_names is not None:
            self.font_names = font_names
        if font_sizes is not None:
            self.font_sizes = font_sizes
        if font_widths is not None:
            self._font_widths = font_widths
        if x_offsets is not None:
            self._x_offsets = x_offsets
        if y_offsets is not None:
            self.y_offsets = y_offsets

    # endregion

    # region Public Properties

    @property
    def font_names(self):
        """list(str): Font names that may be present in this dataset"""
        if not hasattr(self, "_font_names"):
            # TODO: Don't hardcode defaults for macOS
            self._font_names = [
                "/System/Library/Fonts/STHeiti Light.ttc",
                "/System/Library/Fonts/STHeiti Medium.ttc",
                "/Library/Fonts/Songti.ttc"]
        return self._font_names

    @font_names.setter
    def font_names(self, value):
        # TODO: Validate better
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [str(v) for v in list(value)]
                except Exception:
                    raise ValueError(self._generate_setter_exception(value))
        self._font_names = value

    @property
    def font_sizes(self):
        """list(int): Font sizes that may be present in this dataset"""
        if not hasattr(self, "_font_sizes"):
            self._font_sizes = [60, 59, 61, 58, 62]
        return self._font_sizes

    @font_sizes.setter
    def font_sizes(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [int(v) for v in list(value)]
                except Exception:
                    raise ValueError(self._generate_setter_exception(value))
        self._font_sizes = value

    @property
    def font_widths(self):
        """list(int): Font border widths that may be present in this dataset"""
        if not hasattr(self, "_font_widths"):
            self._font_widths = [5, 3, 6, 3]
        return self._font_widths

    @font_widths.setter
    def font_widths(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [int(v) for v in list(value)]
                except Exception as e:
                    raise ValueError(self._generate_setter_exception(value))
        self._font_widths = value

    @property
    def x_offsets(self):
        """list(int): X offsets that may be present in this dataset"""
        if not hasattr(self, "_x_offsets"):
            self._x_offsets = [0, -1, 1, -2, 2]
        return self._x_offsets

    @x_offsets.setter
    def x_offsets(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [int(v) for v in list(value)]
                except Exception as e:
                    raise ValueError(self._generate_setter_exception(value))
        self._x_offsets = value

    @property
    def y_offsets(self):
        """list(int): Y offsets that may be present in this dataset"""
        if not hasattr(self, "_y_offsets"):
            self._y_offsets = [0, -1, 1, -2, 2]
        return self._y_offsets

    @y_offsets.setter
    def y_offsets(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [int(v) for v in list(value)]
                except Exception as e:
                    raise ValueError(self._generate_setter_exception(value))
        self._y_offsets = value

    # endregion

    # region Public Methods

    @abstractmethod
    def generate_training_data(self):
        pass

    # endregion

    # region Private Class Methods

    @classmethod
    @abstractmethod
    def _load_hdf5(cls, fp, verbosity=1, **kwargs):
        """
        Loads dataset from an input hdf5 file

        Args:
            fp (h5py._hl.files.File): Open hdf5 input file
            verbosity (int, optional): Level of verbose output
            **kwargs: Additional keyword arguments

        Returns:
            OCRDataset: Loaded dataset
        """
        pass

    # endregion
