#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.GeneratedOCRDataset,py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import pandas as pd
import numpy as np
from IPython import embed
from scinoephile.ocr import (hanzi_chars, get_chars_of_labels,
                             get_labels_of_chars, OCRDataset)


################################### CLASSES ###################################
class TrainOCRDataset(OCRDataset):
    """
    A collection of character images for training
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
    def chars(self):
        """list(str): Characters that may be present in this dataset"""
        if not hasattr(self, "_chars"):
            self._chars = list(hanzi_chars[:10])
        return self._chars

    @chars.setter
    def chars(self, value):
        # TODO: Validate
        if isinstance(value, int):
            value = list(hanzi_chars[:value])
        self._chars = value

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

    @property
    def spec_dtypes(self):
        """OrderedDict(str, type): Names and dtypes of columns in spec"""
        from collections import OrderedDict

        return OrderedDict(char=str, font=str, size=int, width=int,
                           x_offset=int, y_offset=int)

    # endregion

    # region Public Methods

    def generate_training_data(self, min_images=None):
        from itertools import product
        from random import sample
        from scinoephile.ocr import generate_char_datum

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
            existing = self.get_present_specs_of_char_set(char)
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
            for i, kwargs in enumerate(min_queue):
                data[i] = generate_char_datum(fig=self.figure, **kwargs)

            self.add_img(spec, data)
        else:
            if self.verbosity >= 1:
                print(f"Minimal image set already present, nothing to do")

    def get_present_specs_of_char(self, char):
        return self.spec.loc[self.spec["char"] == char].drop("char", axis=1)

    def get_present_specs_of_char_set(self, char):
        return set(map(tuple, self.spec.loc[self.spec["char"] == char].drop(
            "char", axis=1).values))

    def get_training_data(self, val_portion=0.1):
        from random import sample

        complete_trn_indexes = []
        complete_val_indexes = []

        # Prepare trn and val sets with at least one image of each character
        for char in self.chars:
            all_indexes_of_char = set(
                self.get_present_specs_of_char(char).index)

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
        trn_lbl = get_labels_of_chars(
            self.spec["char"].loc[complete_trn_indexes].values)
        val_img = self.data[complete_val_indexes]
        val_lbl = get_labels_of_chars(
            self.spec["char"].loc[complete_val_indexes].values)

        trn_img = trn_img.astype(np.float16) / 255.0
        val_img = val_img.astype(np.float16) / 255.0

        return trn_img, trn_lbl, val_img, val_lbl

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
        encode = lambda x: x.encode("utf8")

        # Save character image specs
        if "spec" in fp:
            del fp["spec"]
        encoded = self.spec.copy()
        encoded["char"] = encoded["char"].apply(encode)
        encoded["font"] = encoded["font"].apply(encode)
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
