#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.ImageSubtitleSeries.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile import SubtitleSeries
from IPython import embed


################################### CLASSES ###################################
class ImageSubtitleSeries(SubtitleSeries):
    """
    Subtitle series that includes images

    TODO:
      - [ ] Document
    """

    # region Public Methods

    def save(self, path, format_=None, **kwargs):
        """
        Warn that data will be lost if not saved to hdf5
        """

        # Check if hdf5
        if (format_ == "hdf5" or path.endswith(".hdf5")
                or path.endswith(".h5")):
            import h5py
            from scinoephile import HDF5Format

            with h5py.File(path) as fp:
                HDF5Format.to_file(self, fp, format_=format_,
                                   verbosity=self.verbosity, **kwargs)
        # Otherwise, continue as superclass SSAFile
        else:
            from warnings import warn
            from pysubs2 import SSAFile

            warn(f"{self.__class__.__name__}'s image data may only be saved "
                 f"to hdf5")
            SSAFile.save(self, path, format_=format_, **kwargs)

    # endregion

    # region Public Class Methods

    @classmethod
    def load(cls, path, encoding="utf-8", verbosity=1, **kwargs):
        """
        SSAFile.from_file expects an open text file, so we open hdf5 here
        """

        # Check if hdf5
        if (encoding == "hdf5" or path.endswith(".hdf5")
                or path.endswith(".h5")):
            import h5py
            from scinoephile import HDF5Format

            if verbosity >= 1:
                print(f"Loading from '{path}' as hdf5")
            with h5py.File(path) as fp:
                subs = cls()
                subs.format = "hdf5"
                return HDF5Format.from_file(subs, fp,
                                            verbosity=verbosity, **kwargs)
        # Check if sup
        if encoding == "sup" or path.endswith("sup"):
            from scinoephile.ocr import SUPFormat

            if verbosity >= 1:
                print(f"Loading from '{path}' as sup")
            with open(path, "rb") as fp:
                subs = cls()
                subs.format = "sup"
                return SUPFormat.from_file(subs, fp, verbosity=verbosity,
                                           **kwargs)
        # Otherwise, continue as superclass SSAFile
        else:
            if verbosity >= 1:
                print(f"Loading from '{path}'")
            with open(path, encoding=encoding) as fp:
                return cls.from_file(fp, **kwargs)

    # endregion
