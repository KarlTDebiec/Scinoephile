#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from scinoephile import Base


class OCRDataset(Base, ABC):
    """
    Base dataset for optical character recognition
    """

    # region Public Properties

    @property
    def data(self):
        """numpy.ndarray(int): Image data"""
        if not hasattr(self, "_data"):
            self._data = np.zeros((0, *self.data_shape), np.uint8)
        return self._data

    @data.setter
    def data(self, value):
        if not isinstance(value, np.ndarray):
            raise ValueError(self._generate_setter_exception(value))
        if value.shape[1:] != self.data_shape:
            raise ValueError(self._generate_setter_exception(value))
        if value.dtype != np.uint8:
            raise ValueError(self._generate_setter_exception(value))
        self._data = value

    @property
    @abstractmethod
    def data_shape(self):
        """numpy.ndarray(int): Image data shape"""
        pass

    @property
    def figure(self):
        """Figure: Temporary figure used for images"""
        if not hasattr(self, "_figure"):
            from matplotlib.pyplot import figure

            self._figure = figure(
                figsize=(self.data_shape[0] / 80, self.data_shape[1] / 80), dpi=80
            )
        return self._figure

    @property
    def spec(self):
        """pandas.DataFrame: Image specifications"""
        if not hasattr(self, "_spec"):
            self._spec = pd.DataFrame(
                {c: pd.Series([], dtype=d) for c, d in self.spec_dtypes.items()}
            )
        return self._spec

    @spec.setter
    def spec(self, value):
        # TODO: Validate
        self._spec = value

    @property
    @abstractmethod
    def spec_dtypes(self):
        """OrderedDict(str, type): Names and dtypes of columns in spec"""
        pass

    # endregion

    # region Public Methods

    def append(self, spec, data):
        """
        Appends images, excluding images whose spec is already present

        Args:
            spec (pandas.DataFrame): New image specifications
            data (numpy.ndarray): New image data
        """
        current_spec = set(map(tuple, self.spec.values))
        spec_is_new = lambda x: tuple(x.values) not in current_spec

        new = spec.apply(spec_is_new, axis=1).values
        if new.sum() >= 1:
            self.spec = self.spec.append(spec.loc[new], ignore_index=True, sort=False)
            self.data = np.append(self.data, data[new], axis=0)

    @abstractmethod
    def get_data_for_tensorflow(self):
        pass

    def save(self, path=None, **kwargs):
        """
        Saves images to an output file
        """
        import h5py
        from os.path import expandvars

        # Process arguments
        path = expandvars(path).replace("//", "/")
        if self.verbosity >= 1:
            print(f"Writing images to '{path}'")

        # Write outfile
        with h5py.File(path) as fp:
            self._save_hdf5(fp, **kwargs)

    @abstractmethod
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

    # region Private Methods

    @abstractmethod
    def _save_hdf5(self, fp, **kwargs):
        """
        Saves images to an output hdf5 file

        Args:
            fp (h5py._hl.files.File): Open hdf5 output file
            **kwargs: Additional keyword arguments
        """
        pass

    # endregion

    # region Public Class Methods

    @classmethod
    def load(cls, path, verbosity=1, **kwargs):
        """
        Loads dataset from an input file

        Args:
            path (str): Path to input file
            verbosity (int, optional): Level of verbose output
            **kwargs: Additional keyword arguments

        Returns:
            OCRDataset: Loaded dataset
        """
        import h5py
        from os.path import expandvars

        # Process arguments
        path = expandvars(path).replace("//", "/")
        if verbosity >= 1:
            print(f"Reading dataset from '{path}'")

        # Load
        with h5py.File(path) as fp:
            return cls._load_hdf5(fp, verbosity=verbosity, **kwargs)

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
