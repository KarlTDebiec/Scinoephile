#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.OCRDataset.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from abc import ABC, abstractmethod
from scinoephile import DatasetBase
from scinoephile.ocr import OCRBase
from IPython import embed


################################### CLASSES ###################################
class OCRDataset(DatasetBase, OCRBase, ABC):
    """
    A collection of character images
    """

    # region Public Properties

    @property
    def data(self):
        """numpy.ndarray(bool): Character image data"""
        if not hasattr(self, "_data"):
            import numpy as np

            self._data = np.zeros((0, 80, 80), self.data_dtype)
        return self._data

    @data.setter
    def data(self, value):
        import numpy as np

        if not isinstance(value, np.ndarray):
            raise ValueError(self._generate_setter_exception(value))
        if value.shape[1] != 80 or value.shape[2] != 80:
            raise ValueError(self._generate_setter_exception(value))
        if value.dtype != self.data_dtype:
            raise ValueError(self._generate_setter_exception(value))
        self._data = value

    @property
    def data_dtype(self):
        """type: dtype of image arrays"""
        import numpy as np

        if self.mode == "8 bit":
            return np.uint8
        elif self.mode == "1 bit":
            return np.bool
        else:
            raise NotImplementedError()

    @property
    def spec(self):
        """pandas.DataFrame: Character image specifications"""
        if not hasattr(self, "_spec"):
            import pandas as pd

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
        import numpy as np

        new = spec.apply(
            lambda x: tuple(x.values) not in set(map(tuple, self.spec.values)),
            axis=1).values
        if new.sum() >= 1:
            self.spec = self.spec.append(
                spec.loc[new], ignore_index=True, sort=False)
            self.data = np.append(
                self.data, data[new], axis=0)

    def load(self, infile=None, **kwargs):
        """
        Loads character images from an input file
        """
        from os.path import expandvars

        # Process arguments
        if infile is not None:
            infile = expandvars(infile)
        elif self.infile is not None:
            infile = self.infile
        else:
            raise ValueError()

        # Read infile
        if self.verbosity >= 1:
            print(f"Reading character images from '{infile}'")
        if (infile.endswith(".hdf5") or infile.endswith(".h5")):
            import h5py

            with h5py.File(infile) as fp:
                self._load_hdf5(fp, **kwargs)
        else:
            raise NotImplementedError()

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
        from PIL import Image

        # Process arguments
        if data is None and indexes is None:
            data = self.data
            indexes = range(self.data.shape[0])
        elif data is None and indexes is not None:
            data = self.data
        elif data is not None and indexes is None:
            indexes = range(data.shape[0])
        if isinstance(indexes, int):
            indexes = [indexes]
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

    # region Private Methods

    @abstractmethod
    def _load_hdf5(self, fp, **kwargs):
        pass

    @abstractmethod
    def _save_hdf5(self, fp, **kwargs):
        pass

    # endregion
