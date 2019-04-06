#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.OCRDataset.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from scinoephile import Base
from IPython import embed


################################### CLASSES ###################################
class OCRDataset(Base, ABC):
    """
    A collection of character images
    """

    # region Public Properties
    @property
    def data(self):
        """numpy.ndarray(int): Character image data"""
        if not hasattr(self, "_data"):
            self._data = np.zeros((0, 80, 80), np.uint8)
        return self._data

    @data.setter
    def data(self, value):
        if not isinstance(value, np.ndarray):
            raise ValueError(self._generate_setter_exception(value))
        if value.shape[1] != 80 or value.shape[2] != 80:
            raise ValueError(self._generate_setter_exception(value))
        if value.dtype != np.uint8:
            raise ValueError(self._generate_setter_exception(value))
        self._data = value

    @property
    def figure(self):
        """Figure: Temporary figure used for images"""
        if not hasattr(self, "_figure"):
            from matplotlib.pyplot import figure

            self._figure = figure(figsize=(1.0, 1.0), dpi=80)
        return self._figure

    @property
    def labels(self):
        """ndarray: Labels of char_index in dataset"""
        return self.get_labels_of_chars(self.spec["char"].values)

    @property
    def spec(self):
        """pandas.DataFrame: Character image specifications"""
        if not hasattr(self, "_spec"):
            self._spec = pd.DataFrame(
                {c: pd.Series([], dtype=self.spec_dtypes[c])
                 for c in self.spec_cols})
        return self._spec

    @spec.setter
    def spec(self, value):
        # TODO: Validate
        self._spec = value

    @property
    @abstractmethod
    def spec_cols(self):
        """list(str): Character image specification columns"""
        pass

    @property
    @abstractmethod
    def spec_dtypes(self):
        """list(str): Character image specification dtypes"""
        pass

    # endregion

    # region Public Methods

    def add_img(self, spec, data):
        """
        Adds new images

        Args:
            spec (pandas.DataFrame): New image specifications
            data (numpy.ndarray): New image data
        """
        spec_is_new = lambda x: tuple(x.values) not in \
                                set(map(tuple, self.spec.values))

        new = spec.apply(spec_is_new, axis=1).values
        if new.sum() >= 1:
            self.spec = self.spec.append(
                spec.loc[new], ignore_index=True, sort=False)
            self.data = np.append(
                self.data, data[new], axis=0)

    @abstractmethod
    def get_present_specs_of_char(self, char):
        pass

    @abstractmethod
    def get_present_specs_of_char_set(self, char):
        pass

    def save(self, outfile=None, **kwargs):
        """
        Saves character images to an output file
        """
        from os.path import expandvars

        # Process arguments
        if outfile is not None:
            outfile = expandvars(outfile)
        elif self.outfile is not None:
            outfile = self.outfile
        else:
            raise ValueError()

        # Write outfile
        if self.verbosity >= 1:
            print(f"Writing character images to '{outfile}'")
        if (outfile.endswith(".hdf5") or outfile.endswith(".h5")):
            import h5py

            with h5py.File(outfile) as fp:
                self._save_hdf5(fp, **kwargs)
        else:
            raise NotImplementedError()

    def show(self, data=None, indexes=None, cols=20):
        import numpy as np
        from pandas import DataFrame
        from PIL import Image

        # Process arguments
        if data is None and indexes is None:
            data = self.data
            indexes = range(self.data.shape[0])
        elif data is not None and indexes is None:
            indexes = range(data.shape[0])
        elif data is None and indexes is not None:
            data = self.data
        if isinstance(indexes, int):
            indexes = [indexes]
        elif isinstance(indexes, DataFrame):
            indexes = indexes.index.values
        indexes = np.array(indexes, np.int)
        if np.any(indexes >= data.shape[0]):
            raise ValueError()
        if cols is None:
            cols = indexes.size
            rows = 1
        else:
            rows = int(np.ceil(indexes.size / cols))

        # Draw image
        if self.mode == "8 bit":
            img = Image.new("L", (cols * 100, rows * 100), 255)
        elif self.mode == "1 bit":
            img = Image.new("1", (cols * 100, rows * 100), 1)
        for i, index in enumerate(indexes):
            column = (i // cols)
            row = i - (column * cols)
            if self.mode == "8 bit":
                char_img = Image.fromarray(data[index])
            elif self.mode == "1 bit":
                char_img = Image.fromarray(
                    data[index].astype(np.uint8) * 255)
            img.paste(char_img, (100 * row + 10,
                                 100 * column + 10,
                                 100 * (row + 1) - 10,
                                 100 * (column + 1) - 10))
        img.show()

    # endregion

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

    # region Private Methods

    @abstractmethod
    def _save_hdf5(self, fp, **kwargs):
        pass

    # endregion

    # region Private Class Methods

    @classmethod
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
        decode = lambda x: x.decode("utf8")

        # Initialize
        dataset = cls(verbosity=verbosity)

        # Load image specs
        if "spec" not in fp:
            raise ValueError()
        spec = np.array(fp["spec"])
        spec = pd.DataFrame(data=spec, index=range(spec.size),
                            columns=spec.dtype.names)
        spec["char"] = spec["char"].apply(decode)
        spec["font"] = spec["font"].apply(decode)

        # Load image data
        if "data" not in fp:
            raise ValueError()
        data = np.array(fp["data"])

        # Add images and return
        dataset.add_img(spec, data)

        return dataset

    # endregion
