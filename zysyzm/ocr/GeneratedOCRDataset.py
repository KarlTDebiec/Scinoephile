#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.ocr.GeneratedOCRDataset,py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from zysyzm.ocr import LabeledOCRDataset
from IPython import embed


################################### CLASSES ###################################
class GeneratedOCRDataset(LabeledOCRDataset):
    """
    Represents a collection of generated character images

    Todo:
      - [x] Read image directory
      - [x] Add images
      - [x] Write hdf5
      - [x] Read hdf5
      - [x] Write image directory
      - [ ] Initialize
      - [ ] Support creation of training and validation datasets, with at
            least on image of each character in each
      - [ ] Document
    """

    # region Builtins

    def __init__(self, font_names=None, font_sizes=None, font_widths=None,
                 font_x_offsets=None, font_y_offsets=None, n_chars=None,
                 **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if font_names is not None:
            self.font_names = font_names
        if font_sizes is not None:
            self.font_sizes = font_sizes
        if font_widths is not None:
            self._font_widths = font_widths
        if font_x_offsets is not None:
            self._font_x_offsets = font_x_offsets
        if font_y_offsets is not None:
            self.font_y_offsets = font_y_offsets
        if n_chars is not None:
            self.n_chars = n_chars

        # self.input_image_directory = \
        #     "/Users/kdebiec/Desktop/docs/subtitles/trn"
        # self.input_hdf5 = \
        #     "/Users/kdebiec/Desktop/docs/subtitles/trn/generated.h5"
        # self.output_hdf5 = \
        #     "/Users/kdebiec/Desktop/docs/subtitles/trn/generated.h5"
        # self.output_image_directory = \
        #     "/Users/kdebiec/Desktop/generated"

    def __call__(self):
        """ Core logic """

        # Input
        if self.input_hdf5 is not None:
            self.read_hdf5()
        if self.input_image_directory is not None:
            self.read_image_directory()

        # self.initialize_from_scratch()

        # Output
        if self.output_hdf5 is not None:
            self.write_hdf5()
        if self.output_image_directory is not None:
            self.write_image_directory()

        # Present IPython prompt
        if self.interactive:
            embed(**self.embed_kw)

    # endregion

    # region Public Properties

    @property
    def char_image_specs_available(self):
        """pandas.DataFrame: Available character image specifications"""
        if not hasattr(self, "_char_image_specs_available"):
            from itertools import product
            import pandas as pd

            self._char_image_specs_available = pd.DataFrame(
                list(product(self.font_names, self.font_sizes,
                             self.font_widths, self.font_x_offsets,
                             self.font_y_offsets)),
                columns=["font", "size", "width", "x_offset", "y_offset"])

        return self._char_image_specs_available

    @char_image_specs_available.setter
    def char_image_specs_available(self, value):
        # Todo: Validate
        self._char_image_specs_available = value

    @property
    def figure(self):
        """matplotlib.figure.Figure: Temporary figure used for images"""
        if not hasattr(self, "_figure"):
            from matplotlib.pyplot import figure

            self._figure = figure(figsize=(1.0, 1.0), dpi=80)
        return self._figure

    @property
    def font_names(self):
        """list(str): List of font names"""
        if not hasattr(self, "_font_names"):
            self._font_names = ["Hei", "STHeiti"]
        return self._font_names

    @font_names.setter
    def font_names(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [str(v) for v in list(value)]
                except Exception as e:
                    raise ValueError()
        self._font_names = value

    @property
    def font_sizes(self):
        """list(int): List of font sizes"""
        if not hasattr(self, "_font_sizes"):
            self._font_sizes = [60, 59, 61, 58, 62]
        return self._font_sizes

    @font_sizes.setter
    def font_sizes(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [int(v) for v in list(value)]
                except Exception as e:
                    raise ValueError()
        self._font_sizes = value

    @property
    def font_widths(self):
        """list(int): List of font border widths"""
        if not hasattr(self, "_font_widths"):
            self._font_widths = [5, 3, 6, 3, 7]
        return self._font_widths

    @font_widths.setter
    def font_widths(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [int(v) for v in list(value)]
                except Exception as e:
                    raise ValueError()
        self._font_widths = value

    @property
    def font_x_offsets(self):
        """list(int): List of font x offsets"""
        if not hasattr(self, "_font_x_offsets"):
            self._font_x_offsets = [0, -1, 1, -2, 2]
        return self._font_x_offsets

    @font_x_offsets.setter
    def font_x_offsets(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [int(v) for v in list(value)]
                except Exception as e:
                    raise ValueError()
        self._font_x_offsets = value

    @property
    def font_y_offsets(self):
        """list(int): List of font y offsets"""
        if not hasattr(self, "_font_y_offsets"):
            self._font_y_offsets = [0, -1, 1, -2, 2]
        return self._font_y_offsets

    @font_y_offsets.setter
    def font_y_offsets(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [int(v) for v in list(value)]
                except Exception as e:
                    raise ValueError()
        self._font_y_offsets = value

    @property
    def n_chars(self):
        """int: Number of characters to generate images of"""
        if not hasattr(self, "_n_chars"):
            self._n_chars = 100
        return self._n_chars

    @n_chars.setter
    def n_chars(self, value):
        if not isinstance(value, int) and value is not None:
            try:
                value = int(value)
            except Exception as e:
                raise ValueError()
        if value < 1 and value is not None:
            raise ValueError()
        self._n_chars = value

    # endregion

    # region Private Properties

    @property
    def _char_image_spec_columns(self):
        """list(str): Character image specification columns"""

        if hasattr(self, "_char_image_specs"):
            return self.char_image_specs.columns.values
        else:
            return ["path", "character", "font", "size", "width", "x_offset",
                    "y_offset"]

    @property
    def _char_image_spec_dtypes(self):
        """list(str): Character image specification dtypes"""
        return {"path": str, "character": str, "font": str, "size": int,
                "width": int, "x_offset": int, "y_offset": int}

    # endregion

    # region Public Methods

    def add_images_of_chars(self, chars, n_images=1):
        """
        Todo:
          - Prepare empty spec and data of size len(chars) * n_images, keep
            track of how many are actually added append once at the end
          - Handle case in which more images are requested than specs remain
            available
          - Support varying number of images per character
        """
        import numpy as np
        from random import sample

        if not isinstance(chars, list):
            chars = list(chars)
        columns = self.char_image_specs.columns.values
        all_specs = self.char_image_specs_available.values.tolist()
        all_specs = set(map(tuple, all_specs))

        for char in chars:
            print(char)
            old_specs = self.char_image_specs.loc[
                self.char_image_specs["character"] == char].drop(
                "character", axis=1).values
            old_specs = set(map(tuple, list(old_specs)))
            new_specs = all_specs.difference(old_specs)
            for new_spec in list(sample(new_specs, n_images)):
                new_spec = [char] + list(new_spec)
                new_spec_kw = {k: v for k, v in zip(columns, new_spec)}
                new_image = self.generate_char_image_data(**new_spec_kw)
                self.char_image_specs = self.char_image_specs.append(
                    new_spec_kw, ignore_index=True)
                self.char_image_data = np.append(
                    self.char_image_data, np.expand_dims(new_image, 0), axis=0)

    def generate_char_image(self, character, font="Hei", size=60, width=5,
                            x_offset=0, y_offset=0, tmpfile="/tmp/zysyzm.png"):
        from os import remove
        from matplotlib.font_manager import FontProperties
        from matplotlib.patheffects import Stroke, Normal
        from PIL import Image
        from zysyzm.ocr import (convert_8bit_grayscale_to_2bit, trim_image,
                                resize_image)

        # Draw initial image with matplotlib
        self.figure.clear()
        fp = FontProperties(family=font, size=size)
        text = self.figure.text(x=0.5, y=0.475, s=character,
                                ha="center", va="center",
                                fontproperties=fp,
                                color=(0.67, 0.67, 0.67))
        text.set_path_effects([Stroke(linewidth=width,
                                      foreground=(0.00, 0.00, 0.00)),
                               Normal()])
        self.figure.savefig(tmpfile, dpi=80, transparent=True)

        # Reload with pillow to trim, resize, and adjust color
        img = trim_image(Image.open(tmpfile).convert("L"), 0)
        img = resize_image(img, (80, 80), x_offset, y_offset)
        remove(tmpfile)

        # Convert to configured format
        if self.image_mode == "8bit":
            pass
        elif self.image_mode == "2bit":
            img = convert_8bit_grayscale_to_2bit(img)
        elif self.image_mode == "1bit":
            raise NotImplementedError()

        return img

    def initialize_from_scratch(self):
        import numpy as np
        import pandas as pd

        # Prepare empty arrays
        self.char_image_specs = pd.DataFrame(
            index=range(self.n_chars),
            columns=self.char_image_specs.columns.values)
        self.char_image_data = np.zeros(
            (self.n_chars, self._image_data_size), dtype=self._image_data_dtype)

        # Fill in arrays with specs and data
        for i, char in enumerate(self.chars[:self.n_chars]):
            row = self.char_image_specs_available.loc[0].to_dict()
            row["character"] = char
            self.char_image_specs.loc[i] = row
            self.char_image_data[i] = self.image_to_data(
                self.generate_char_image(**row))

    # endregion

    # Private Methods

    def _read_hdf5_spec_formatter(self, columns):
        """Provides spec formatter compatible with both numpy and h5py"""
        columns = list(columns)
        str_indexes = []
        if "path" in columns:
            str_indexes += [columns.index("path")]
        if "character" in columns:
            str_indexes += [columns.index("character")]
        if "font" in columns:
            str_indexes += [columns.index("font")]

        def func(x):
            x = list(x)
            for str_index in str_indexes:
                x[str_index] = x[str_index].decode("utf8")
            return tuple(x)

        return func

    def _read_image_directory_specs(self, infiles):
        """Provides specs of infiles"""
        import pandas as pd
        from os.path import basename

        chars = list(map(
            lambda x: basename(x).split("_")[0],
            infiles))
        sizes = list(map(
            lambda x: int(basename(x).split("_")[1]),
            infiles))
        widths = list(map(
            lambda x: int(basename(x).split("_")[2]),
            infiles))
        x_offsets = list(map(
            lambda x: int(basename(x).split("_")[3]),
            infiles))
        y_offsets = list(map(
            lambda x: int(basename(x).split("_")[4]),
            infiles))
        fonts = list(map(
            lambda x: basename(x).split("_")[5].split(".")[0],
            infiles))

        specs = {
            "path": pd.Series(
                infiles, dtype=self._char_image_spec_dtypes["path"]),
            "character": pd.Series(
                chars, dtype=self._char_image_spec_dtypes["character"]),
            "font": pd.Series(
                fonts, dtype=self._char_image_spec_dtypes["font"]),
            "size": pd.Series(
                sizes, dtype=self._char_image_spec_dtypes["size"]),
            "width": pd.Series(
                widths, dtype=self._char_image_spec_dtypes["width"]),
            "x_offset": pd.Series(
                x_offsets, dtype=self._char_image_spec_dtypes["x_offset"]),
            "y_offset": pd.Series(
                y_offsets, dtype=self._char_image_spec_dtypes["y_offset"])}

        return pd.DataFrame(data=specs, index=range(len(infiles)))

    def _write_hdf5_spec_dtypes(self, columns):
        """Provides spec dtypes compatible with both numpy and h5py"""
        dtypes = {"path": "S255", "character": "S3", "font": "S10",
                  "size": "i1", "width": "i1", "x_offset": "i1",
                  "y_offset": "i1"}
        return list(zip(columns, [dtypes[k] for k in columns]))

    def _write_hdf5_spec_formatter(self, columns):
        """Provides spec formatter compatible with both numpy and h5py"""
        columns = list(columns)
        str_indexes = []
        if "path" in columns:
            str_indexes += [columns.index("path")]
        if "character" in columns:
            str_indexes += [columns.index("character")]
        if "font" in columns:
            str_indexes += [columns.index("font")]

        def func(x):
            x = list(x)
            for str_index in str_indexes:
                x[str_index] = x[str_index].encode("utf8")
            return tuple(x)

        return func

    def _write_image_directory_formatter(self, specs):
        """Provides formatter for image outfile paths"""
        from os.path import dirname

        def get_base_path_remover(paths):
            """Provides function to remove shared base path"""

            for i in range(max(map(len, paths))):
                if len(set([path[i] for path in paths])) != 1:
                    break
            i = len(dirname(paths[0][:i])) + 1
            return lambda x: x[i:]

        if "path" in specs.columns:
            base_path_remover = get_base_path_remover(list(specs["path"]))

            def func(spec):
                return f"{self.output_image_directory}/" \
                       f"{base_path_remover(spec[1]['path'])}"

            return func
        else:
            def func(spec):
                return f"{self.output_image_directory}/" \
                       f"{spec[1]['character']}_" \
                       f"{spec[1]['size']:02d}_" \
                       f"{spec[1]['width']:02d}_" \
                       f"{spec[1]['x_offset']:+d}_" \
                       f"{spec[1]['y_offset']:+d}_" \
                       f"{spec[1]['font'].replace(' ', '')}.png"

        return func

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    GeneratedOCRDataset.main()
