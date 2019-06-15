#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.RecognitionTrainDataset,py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import pandas as pd
import numpy as np
from collections import OrderedDict
from scinoephile.ocr import OCRTrainDataset
from scinoephile.ocr.recognition import RecognitionDataset


################################### CLASSES ###################################
class RecognitionTrainDataset(RecognitionDataset, OCRTrainDataset):
    """
    A collection of character images for training
    """

    # region Public Properties

    @property
    def spec_dtypes(self):
        """OrderedDict(str, type): Names and dtypes of columns in spec"""
        return OrderedDict(char=str, font=str, size=int, width=int,
                           x_offset=int, y_offset=int)

    # endregion

    # region Public Methods

    def generate_training_data(self, min_images=None):
        """

        Args:
            min_images:

        Returns:

        """
        from itertools import product
        from random import sample
        from scinoephile.ocr import generate_char_datum

        # TODO: Document
        # TODO: Parallelize
        # TODO: Handle missing characters smoothly

        # Process arguments
        fonts, sizes, widths, x_offsets, y_offsets = tuple(zip(*product(
            self.font_names, self.font_sizes, self.font_widths,
            self.x_offsets, self.y_offsets)))
        spec_all = pd.DataFrame({
            "font": pd.Series(
                fonts,
                dtype=self.spec_dtypes["font"]),
            "size": pd.Series(
                sizes,
                dtype=self.spec_dtypes["size"]),
            "width": pd.Series(
                widths,
                dtype=self.spec_dtypes["width"]),
            "x_offset": pd.Series(
                x_offsets,
                dtype=self.spec_dtypes["x_offset"]),
            "y_offset": pd.Series(
                y_offsets,
                dtype=self.spec_dtypes["y_offset"])})
        spec_min = pd.DataFrame({
            "font": pd.Series(
                self.font_names,
                dtype=self.spec_dtypes["font"]),
            "size": pd.Series(
                [self.font_sizes[0]] * len(self.font_names),
                dtype=self.spec_dtypes["size"]),
            "width": pd.Series(
                [self.font_widths[0]] * len(self.font_names),
                dtype=self.spec_dtypes["width"]),
            "x_offset": pd.Series(
                [self.x_offsets[0]] * len(self.font_names),
                dtype=self.spec_dtypes["x_offset"]),
            "y_offset": pd.Series(
                [self.y_offsets[0]] * len(self.font_names),
                dtype=self.spec_dtypes["y_offset"])})
        spec_all_set = set(map(tuple, spec_all.values))
        spec_min_set = set(map(tuple, spec_min.values))
        if min_images is None:
            min_images = len(spec_min_set)
        min_images = max(len(spec_min_set), min_images)
        if self.verbosity >= 1:
            print(f"Checking that at least {min_images} images are present "
                  f"for each of {len(self.chars)} characters")

        # Build queue of needed specs
        min_queue = []
        to_dict = lambda x: {k: v for k, v in zip(self.spec_dtypes.keys(),
                                                  (char, *x))}
        for char in self.chars:
            existing = self.get_present_specs_of_char(char, True)
            minimal = spec_min_set.difference(existing)
            min_queue.extend(map(to_dict, minimal))
            n_additional = min_images - len(existing) - len(minimal)

            if n_additional >= 1:
                available = spec_all_set.difference(existing).difference(
                    minimal)
                selected = sample(available, min(n_additional, len(available)))
                min_queue.extend(map(to_dict, selected))

        # Generate and add images
        if len(min_queue) >= 1:
            if self.verbosity >= 1:
                print(f"Generating {len(min_queue)} new images for minimal "
                      f"set")

            spec = pd.DataFrame(min_queue)
            data = np.zeros((len(min_queue), 80, 80), np.uint8)

            for i, kw in enumerate(min_queue):
                data[i] = generate_char_datum(fig=self.figure, **kw)

            self.append(spec, data)
        else:
            if self.verbosity >= 1:
                print(f"Minimal image set already present, nothing to do")

    def get_data_for_tensorflow(self, val_portion=0.1):
        from random import sample

        if val_portion is None or val_portion == 0.0:
            trn_img = self.data.astype(np.float16) / 255.0
            trn_lbl = self.get_labels_of_chars(self.spec["char"].values)

            return trn_img, trn_lbl, None, None

        complete_trn_indexes = []
        complete_val_indexes = []

        # Prepare trn and val sets with at least one image of each character
        for char in self.chars:
            all_indexes_of_char = set(
                self.get_present_specs_of_char(char, as_set=False).index)

            # Add at least one image of each character to val and trn
            trn_index, val_index = sample(all_indexes_of_char, 2)
            complete_trn_indexes.append(trn_index)
            complete_val_indexes.append(val_index)
            all_indexes_of_char -= {trn_index, val_index}

            # Distribute remaining images across val and trn sets
            n_for_val = int(np.floor(len(all_indexes_of_char) * val_portion))
            if n_for_val > 0:
                val_indexes = sample(all_indexes_of_char, n_for_val)
                complete_val_indexes.extend(val_indexes)
                all_indexes_of_char -= set(val_indexes)
            complete_trn_indexes.extend(all_indexes_of_char)

        # Organize data
        trn_img = self.data[complete_trn_indexes]
        trn_lbl = self.get_labels_of_chars(
            self.spec["char"].loc[complete_trn_indexes].values)
        val_img = self.data[complete_val_indexes]
        val_lbl = self.get_labels_of_chars(
            self.spec["char"].loc[complete_val_indexes].values)

        trn_img = trn_img.astype(np.float16) / 255.0
        val_img = val_img.astype(np.float16) / 255.0

        return trn_img, trn_lbl, val_img, val_lbl

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

    # region Private Methods

    def _save_hdf5(self, fp, **kwargs):
        dtypes = [
            ("char", "S3"),
            ("font", "S255"),
            ("size", "i1"),
            ("width", "i1"),
            ("x_offset", "i1"),
            ("y_offset", "i1")]

        # Save characters
        if "chars" in fp:
            del fp["chars"]
        encoded = np.char.encode(self.chars, "utf8")
        fp.create_dataset("chars",
                          data=encoded, dtype="S3",
                          chunks=True, compression="gzip")

        # Save character image specs
        if "spec" in fp:
            del fp["spec"]
        encoded = self.spec.copy()
        encoded["char"] = np.char.encode(encoded["char"].values.astype(str))
        encoded["font"] = np.char.encode(encoded["font"].values.astype(str))
        encoded = np.array(list(map(tuple, list(encoded.values))),
                           dtype=dtypes)
        fp.create_dataset("spec",
                          data=encoded, dtype=dtypes,
                          chunks=True, compression="gzip")

        # Save character image data
        if "data" in fp:
            del fp["data"]
        fp.create_dataset("data",
                          data=self.data, dtype=np.uint8,
                          chunks=True, compression="gzip")

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
            RecognitionTrainDataset: Loaded dataset
        """

        # TODO: Improve expection text

        # Initialize
        dataset = cls(verbosity=verbosity)

        # Load characters
        if "chars" not in fp:
            raise ValueError()
        dataset.chars = np.chararray.decode(fp["chars"], "utf8")

        # Load image specs
        if "spec" not in fp:
            raise ValueError()
        spec = np.array(fp["spec"])
        spec = pd.DataFrame(data=spec, index=range(spec.size),
                            columns=spec.dtype.names)
        spec["char"] = np.char.decode(spec["char"].values.astype("S3"), "utf8")
        spec["font"] = np.char.decode(spec["font"].values.astype("S255"),
                                      "utf8")

        # Load image data
        if "data" not in fp:
            raise ValueError()
        data = np.array(fp["data"])

        # Add images
        dataset.append(spec, data)

        return dataset

    # endregion
