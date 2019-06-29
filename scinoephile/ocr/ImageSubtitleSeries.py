#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.ImageSubtitleSeries.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import numpy as np
import pandas as pd
from scinoephile import SubtitleSeries
from scinoephile.ocr import (ImageSubtitleEvent)
from scinoephile.ocr.numba import read_sup_subtitles


################################### CLASSES ###################################
class ImageSubtitleSeries(SubtitleSeries):
    """
    A series of image-based subtitles
    """

    # region Class Attributes

    event_class = ImageSubtitleEvent
    """Class of individual subtitle events"""

    # endregion

    # region Public Properties

    @property
    def data(self):
        """ndarray: Dedupulicated character image data collected from all
        subtitles"""
        if not hasattr(self, "_data"):
            self._initialize_data()
        return self._data

    @property
    def spec(self):
        """DataFrame: Specifications describing each character image"""
        if not hasattr(self, "_spec"):
            self._initialize_data()
        return self._spec

    @property
    def spec_dtypes(self):
        """OrderedDict(str, type): names and dtypes of columns in spec"""
        if not hasattr(self, "_spec_dtypes"):
            from collections import OrderedDict

            self._spec_dtypes = OrderedDict(char=str, indexes=object)
        return self._spec_dtypes

    # endregion

    # region Public Methods

    def get_char_index_of_subchar_indexes(self, sub_index, char_index):
        raise NotImplementedError()

    def get_subchar_indexes_of_char_index(self, index):
        """
        Converts the index of a deduplicated character into a list of indexes
        of that character's appearances within subtitles

        Args:
            index (int): Index of deduplicated character

        Returns:
            list(tuple(int, int)): Indexes of character within subtitles in the
              form of (subtitle index within series, character index within
              subtitle)
        """
        return self.spec.loc[index].indexes

    def save(self, path, format_=None, **kwargs):
        """
        Saves subtitles to an output file

        Note:
            pysubs2.SSAFile.save expects an open text file, so we open the
            hdf5 file here for consistency.

        Args:
            path (str): Path to output file
            format_ (str, optional): Output file format
            **kwargs: Additional keyword arguments
        """
        from os.path import expandvars, isdir
        from pysubs2 import SSAFile

        # Process arguments
        path = expandvars(path).replace("//", "/")
        if self.verbosity >= 1:
            print(f"Writing subtitles to '{path}'")

        # Check if hdf5
        if format_ == "hdf5" or path.endswith(".hdf5") or path.endswith(".h5"):
            import h5py

            with h5py.File(path) as fp:
                self._save_hdf5(fp, **kwargs)
        # Check if directory
        elif format_ == "png" or path.endswith("/") or isdir(path):
            self._save_png(path, **kwargs)
        # Otherwise, continue as superclass SSAFile
        else:
            SSAFile.save(self, path, format_=format_, **kwargs)

    def show(self, indexes=None, data=None, **kwargs):
        """
        Shows images of selected characters

        If called from within Jupyter notebook, shows inline. If imgcat module
        is available, shows inline in terminal. Otherwise opens a new window.

        Args:
            indexes (int, list, ndarray, optional): Indexes of character image
              data to show
            data (ndarray, optional): Character image data to show
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

    # region Public Class Methods

    @classmethod
    def load(cls, path, format_=None, verbosity=1, **kwargs):
        """
        Loads subtitles from an input file

        Notes:
            pysubs2.SSAFile.from_file expects an open text file, so we open
             the hdf5 file here for consistency

        Args:
            path (str): Path to input file
            format_ (str, optional): Input file format
            verbosity (int, optional): Level of verbose output
            **kwargs: Additional keyword arguments

        Returns:
            ImageSubtitleSeries: Loaded subtitles
        """
        from os.path import expandvars

        # Process arguments
        path = expandvars(path).replace("//", "/")
        if verbosity >= 1:
            print(f"Reading subtitles from '{path}'")

        # Check if hdf5
        if format_ == "hdf5" or path.endswith(".hdf5") or path.endswith(".h5"):
            import h5py

            with h5py.File(path) as fp:
                return cls._load_hdf5(fp, verbosity=verbosity, **kwargs)
        # Check if sup
        if format_ == "sup" or path.endswith(".sup"):
            with open(path, "rb") as fp:
                return cls._load_sup(fp, verbosity=verbosity, **kwargs)
        # Other formats not supported for this class
        else:
            raise ValueError()

    # endregion

    # region Private Methods

    def _initialize_data(self):
        """
        Initializes deduplicated character image data structure
        """
        if self.verbosity >= 1:
            print("Initializing character data structures")

        if (hasattr(self, "_data") and self._data is not None
                and hasattr(self, "_spec") and self._spec is not None):
            prior_data = self._data
            prior_spec = self._spec
            if self.verbosity >= 1:
                print("Retaining prior character assignments")
        else:
            prior_data = prior_spec = None

        n_total_chars = sum([e.char_count for e in self.events])
        n_checked_chars = 0
        n_unique_chars = 0
        data = np.zeros((n_total_chars, 80, 80), np.uint8)
        chars = []
        subchar_indexes = []

        # Loop over subtitles within this series
        for i, event in enumerate(self.events):
            if self.verbosity >= 2:
                print(f"Analyzing characters for event "
                      f"{i + 1}/{len(self.events)}")
            n_checked_chars += event.char_count

            # Loop over characters within this subtitle
            for j, datum in enumerate(event.char_data):

                # Check if character is already in nascent array
                match = np.where(
                    (data[:n_unique_chars] == datum).all(axis=(1, 2)))[0]
                if match.size > 0:
                    # Character previously seen, update index
                    subchar_indexes[match[0]].append((i, j))
                else:
                    # Character is new, add to nascent array
                    data[n_unique_chars] = datum
                    subchar_indexes.append([(i, j)])
                    n_unique_chars += 1

                    # Check prior data for assignment of this image
                    if prior_data is not None:
                        prior_match = np.where(
                            (prior_data == datum).all(axis=(1, 2)))[0]
                        if prior_match.size > 0:
                            # Copy over prior assignment
                            chars.append(
                                prior_spec.loc[prior_match[0]]["char"])
                        else:
                            chars.append("")
                    else:
                        chars.append("")
        self._data = data[:n_unique_chars]
        self._spec = pd.DataFrame.from_dict({"char": chars,
                                             "indexes": subchar_indexes})

    def _save_hdf5(self, fp, **kwargs):
        """
        Saves subtitles to an output hdf5 file

        Args:
            fp (h5py._hl.files.File): Open hdf5 output file
            **kwargs: Additional keyword arguments
        """

        dtypes = [("series char index", "i8"),
                  ("char", "S3"),
                  ("subtitle index", "i8"),
                  ("subtitle char index", "i8")]
        encode = lambda x: x.encode("utf8")

        # Save info, styles and subtitles
        SubtitleSeries._save_hdf5(self, fp, **kwargs)

        # Save subtitle image data
        if "full_data" in fp:
            del fp["full_data"]
        fp.create_group("full_data")
        for i, event in enumerate(self.events):
            if hasattr(event, "full_data"):
                fp["full_data"].create_dataset(f"{i:04d}",
                                               data=event.full_data,
                                               dtype=np.uint8,
                                               chunks=True,
                                               compression="gzip")

        # Save char image specs
        if "spec" in fp:
            del fp["spec"]
        if hasattr(self, "_spec"):
            fp.create_dataset("spec",
                              data=np.array(list(map(tuple, list(pd.DataFrame(
                                  [(i, encode(s["char"]), j, k)
                                   for i, s in self.spec.iterrows()
                                   for j, k in s["indexes"]],
                                  columns=[d[0] for d in dtypes]).values))),
                                            dtype=dtypes),
                              dtype=dtypes,
                              chunks=True,
                              compression="gzip")

        # Save char image data
        if "data" in fp:
            del fp["data"]
        if hasattr(self, "_data"):
            fp.create_dataset("data",
                              data=self.data,
                              dtype=np.uint8,
                              chunks=True,
                              compression="gzip")

    def _save_png(self, fp, **kwargs):
        """
        Saves subtitles to directory of png files

        Args:
            fp (str): Directory path
            **kwargs: Additional keyword arguments
        """
        from os import makedirs
        from os.path import isdir

        # TODO: Also save srt file in folder using pysubs2 code

        if not isdir(fp):
            makedirs(fp)
        for i, event in enumerate(self.events):
            event.save(f"{fp}/{i:04d}.png")

    # endregion

    # region Private Class Methods

    @classmethod
    def _load_hdf5(cls, fp, verbosity=1, **kwargs):
        """
        Loads subtitles from an input hdf5 file

        Args:
            fp (h5py._hl.files.File): Open hdf5 input file
            verbosity (int, optional): Level of verbose output
            **kwargs: Additional keyword arguments

        Returns:
            ImageSubtitleSeries: Loaded subtitles
        """
        # TODO: Load project info

        decode = lambda x: x.decode("utf8")

        # Load info, styles, and events
        subs = super()._load_hdf5(fp=fp, verbosity=verbosity, **kwargs)

        # Load images
        if "full_data" in fp and "events" in fp:

            for i, event in enumerate(subs.events):
                event.full_data = np.array(fp["full_data"][f"{i:04d}"],
                                           np.uint8)

            # Load char image specs
            if "spec" in fp:
                encoded = np.array(fp["spec"])
                encoded = pd.DataFrame(data=encoded,
                                       index=range(encoded.size),
                                       columns=encoded.dtype.names)
                n_unique_chars = encoded["series char index"].max() + 1
                # np.empty and tolist are used to create unique empty lists
                spec = pd.DataFrame(
                    {"char": [""] * n_unique_chars,
                     "indexes": np.empty((n_unique_chars, 0)).tolist()})
                for i, char, j, k in encoded.values:
                    spec["char"].loc[i] = decode(char)
                    spec["indexes"].loc[i] += [(j, k)]

                subs._spec = spec

            # Load char image data
            if "data" in fp:
                subs._data = np.array(fp["data"])

        return subs

    @classmethod
    def _load_sup(cls, fp, verbosity=1, **kwargs):
        """
        Loads subtitles from an input sup file

        Args:
            fp (): Open binary file
            verbosity (int, optional): Level of verbose output
            **kwargs: Additional keyword arguments

        Returns:
            SubtitleSeries: Loaded subtitles
        """
        from pysubs2.time import make_time

        # Initialize
        subs = cls(verbosity=verbosity)
        subs.format = "sup"

        # Parse infile
        bytes = fp.read()
        starts, ends, images = read_sup_subtitles(bytes)
        for start, end, image in zip(starts, ends, images):
            subs.events.append(cls.event_class(
                start=make_time(s=start),
                end=make_time(s=end),
                data=image,
                series=subs))

        return subs

    # endregion
