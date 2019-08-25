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
from IPython import embed
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

            self._spec_dtypes = OrderedDict(char=str, indexes=object,
                                            confirmed=bool)
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

    def _initialize_data(self, verbosity=None):
        """
        Initializes deduplicated character image data structure
        """

        if verbosity is None:
            verbosity = self.verbosity
        if verbosity >= 1:
            print("Initializing character data structures")

        # Load character data
        n_total_chars = sum([e.char_count for e in self.events])
        raw_data = np.zeros((n_total_chars, 80, 80), np.uint8)
        raw_subchar_indexes = np.empty(n_total_chars, dtype="O")
        char_index = 0
        for event_index, event in enumerate(self.events):
            for event_char_index, datum in enumerate(event.char_data):
                raw_data[char_index] = datum
                raw_subchar_indexes[char_index] = (
                    event_index, event_char_index)
                char_index += 1

        # Clear prior indexes
        for event in self.events:
            event._char_indexes = np.zeros(event.char_count, np.int)

        # Deduplicate character data
        raw_data = raw_data.reshape((n_total_chars, 80 * 80))
        sorted_index = np.lexsort(raw_data.T)
        sorted_data = raw_data[sorted_index]
        datum_is_unique = np.append(
            [True], np.any(np.diff(sorted_data, axis=0) != 0, axis=1), 0)
        unique_indexes = np.sort(sorted_index[datum_is_unique])
        n_unique_chars = datum_is_unique.sum()
        data = raw_data[unique_indexes].reshape(-1, 80, 80)

        # Organize specs
        chars = np.array([""] * n_unique_chars)
        subchar_indexes = np.empty(n_unique_chars, dtype="O")
        confirmed = np.array([False] * n_unique_chars)
        for a, unique, subchar_index in zip(sorted_index, datum_is_unique,
                                            raw_subchar_indexes[sorted_index]):
            if unique:
                final_index = np.where(unique_indexes == a)[0][0]
                subchar_indexes[final_index] = [subchar_index]
            else:
                subchar_indexes[final_index] += [subchar_index]
            self.events[subchar_index[0]].char_indexes[
                subchar_index[1]] = final_index
        spec = pd.DataFrame.from_dict(
            {"char": chars, "indexes": subchar_indexes,
             "confirmed": confirmed})

        # Transfer prior character assignments
        if (hasattr(self, "_data") and self._data is not None and
                hasattr(self, "_spec") and self._spec is not None):
            if verbosity >= 1:
                print("Transferring prior character assignments")
            sums = np.array([datum.sum() for datum in self._data])
            for i, datum in enumerate(data):
                for j in np.where(sums == datum.sum())[0]:
                    if np.all(datum == self._data[j]):
                        if verbosity >= 3:
                            print(f"Copying assingment of char {j} as "
                                  f"'{self._spec.at[j, 'char']}'")

                        spec.at[i, 'char'] = self._spec.at[j, 'char']
                        spec.at[i, 'confirmed'] = self._spec.at[j, 'confirmed']

        # Store
        self._data = data
        self._spec = spec

    def _merge_chars(self, index_1, index_2, char=None):
        """
        Merges two adjacent characters

        Args:
            index_1 (int): Index of first character
            index_1 (int): Index of second character
            char (str): Character to assign to merged result
        """
        # Make sure that all are adjacent
        if self.verbosity >= 2:
            print(f"Merging chars {index_1} and {index_2}")
        if len(self.spec.loc[index_1, "indexes"]) > 1:
            embed(**self.embed_kw)
        if len(self.spec.loc[index_1, "indexes"]) != len(
                self.spec.loc[index_2, "indexes"]):
            raise ValueError()
        for (s1, c1), (s2, c2) in zip(self.spec.loc[index_1, "indexes"],
                                      self.spec.loc[index_2, "indexes"]):
            if s1 != s2:
                raise ValueError()
            if c1 + 1 != c2:
                raise ValueError()
        for s_i, c_i in self.spec.loc[index_1, "indexes"]:
            event = self.events[s_i]
            event._char_bounds = np.concatenate(
                (event.char_bounds[:c_i],
                 np.array([[event.char_bounds[c_i, 0],
                            event.char_bounds[c_i + 1, 1]]]),
                 event.char_bounds[c_i + 2:]))
            event._initialize_char_data()
        self._initialize_data(verbosity=self.verbosity - 1)
        if char is not None:
            new_index = event.char_spec.iloc[c1].name
            if self.verbosity >= 2:
                print(f"Confirming char {new_index} as '{char}'")
            self.spec.loc[new_index, "char"] = char
            self.spec.loc[new_index, "confirmed"] = True

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
                  ("subtitle char index", "i8"),
                  ("confirmed", "?")]
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
                fp["full_data"][f"{i:04d}"].attrs[
                    "char_bounds"] = event.char_bounds

        # Save char image specs
        if "spec" in fp:
            del fp["spec"]
        if hasattr(self, "_spec"):
            fp.create_dataset("spec",
                              data=np.array(list(map(tuple, list(pd.DataFrame(
                                  [(i, encode(s["char"]), j, k, s["confirmed"])
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
                attrs = dict(fp["full_data"][f"{i:04d}"].attrs)
                if "char_bounds" in attrs:
                    event._char_bounds = attrs["char_bounds"]

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
                     "indexes": np.empty((n_unique_chars, 0)).tolist(),
                     "confirmed": [False] * n_unique_chars, })
                for i, char, j, k, confirmed in encoded.values:
                    spec.at[i, "char"] = decode(char)
                    spec.at[i, "indexes"] += [(j, k)]
                    spec.at[i, "confirmed"] = confirmed

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
