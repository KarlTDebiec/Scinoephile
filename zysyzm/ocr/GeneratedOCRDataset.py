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
      - [ ] Remove temporary code used during troubleshooting
      - [ ] Expand training and validation sets when images are added, rather
            than recreating fully
      - [ ] Implement CL arguments
      - [ ] Validate CL arguments
      - [ ] Document
    """

    # region Builtins

    def __init__(self, n_chars=None, font_names=None, font_sizes=None,
                 font_widths=None, font_x_offsets=None, font_y_offsets=None,
                 **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if n_chars is not None:
            self.n_chars = n_chars
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

        # Temporary manual configuration for testing
        # self.input_image_dir = \
        #     "/Users/kdebiec/Desktop/docs/subtitles/trn"
        self.input_hdf5 = \
            "/Users/kdebiec/Desktop/docs/subtitles/trn.h5"
        self.output_hdf5 = \
            "/Users/kdebiec/Desktop/docs/subtitles/trn.h5"
        # self.output_image_dir = \
        #     "/Users/kdebiec/Desktop/docs/subtitles/trn"

    def __call__(self):
        """ Core logic """
        from os.path import isdir, isfile

        # Input
        if self.input_hdf5 is not None and isfile(self.input_hdf5):
            self.read_hdf5()
        if self.input_image_dir is not None and isdir(self.input_image_dir):
            self.read_image_dir()

        # Action
        self.generate_minimal_images()
        # self.generate_additional_images(1)

        # Output
        if self.output_hdf5 is not None:
            self.write_hdf5()
        if self.output_image_dir is not None:
            self.write_image_dir()

        # Present IPython prompt
        if self.interactive:
            embed(**self.embed_kw)

    # endregion

    # region Public Properties

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
                    raise ValueError(self._generate_setter_exception(value))
        self._font_names = value
        self._clear_private_property_caches()

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
                    raise ValueError(self._generate_setter_exception(value))
        self._font_sizes = value
        self._clear_private_property_caches()

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
                    raise ValueError(self._generate_setter_exception(value))
        self._font_widths = value
        self._clear_private_property_caches()

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
                    raise ValueError(self._generate_setter_exception(value))
        self._font_x_offsets = value
        self._clear_private_property_caches()

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
                    raise ValueError(self._generate_setter_exception(value))
        self._font_y_offsets = value
        self._clear_private_property_caches()

    @property
    def n_chars(self):
        """int: Number of unique characters to support"""
        if not hasattr(self, "_n_chars"):
            self._n_chars = 10
        return self._n_chars

    @n_chars.setter
    def n_chars(self, value):
        if value is not None:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except Exception as e:
                    raise ValueError(self._generate_setter_exception(value))
            if value < 1:
                raise ValueError(self._generate_setter_exception(value))
        self._n_chars = value

    # endregion

    # region Private Properties

    @property
    def _spec_columns(self):
        """list(str): Character image specification columns"""

        if hasattr(self, "_specs"):
            return self.specs.columns.values
        else:
            return ["path", "char", "font", "size", "width", "x_offset",
                    "y_offset"]

    @property
    def _spec_dtypes(self):
        """list(str): Character image specification dtypes"""
        return {"path": str, "char": str, "font": str, "size": int,
                "width": int, "x_offset": int, "y_offset": int}

    @property
    def _figure(self):
        """matplotlib.figure.Figure: Temporary figure used for images"""
        if not hasattr(self, "_figure_"):
            from matplotlib.pyplot import figure

            self._figure_ = figure(figsize=(1.0, 1.0), dpi=80)
        return self._figure_

    @property
    def _draw_specs_available(self):
        """pandas.DataFrame: Available character image specifications"""
        if not hasattr(self, "_draw_specs_available_"):
            import pandas as pd
            from itertools import product

            fonts, sizes, widths, x_offsets, y_offsets = tuple(zip(*product(
                self.font_names, self.font_sizes, self.font_widths,
                self.font_x_offsets, self.font_y_offsets)))

            self._draw_specs_available_ = pd.DataFrame({
                "font": pd.Series(
                    fonts,
                    dtype=self._spec_dtypes["font"]),
                "size": pd.Series(
                    sizes,
                    dtype=self._spec_dtypes["size"]),
                "width": pd.Series(
                    widths,
                    dtype=self._spec_dtypes["width"]),
                "x_offset": pd.Series(
                    x_offsets,
                    dtype=self._spec_dtypes["x_offset"]),
                "y_offset": pd.Series(
                    y_offsets,
                    dtype=self._spec_dtypes["y_offset"])})

        return self._draw_specs_available_

    @property
    def _draw_specs_available_set(self):
        if not hasattr(self, "_draw_specs_available_set_"):
            self._draw_specs_available_set_ = set(
                map(tuple, self._draw_specs_available.values))
        return self._draw_specs_available_set_

    @property
    def _draw_specs_minimal(self):
        """pandas.DataFrame: Available character image specifications"""
        if not hasattr(self, "_draw_specs_minimal_"):
            import pandas as pd

            self._draw_specs_minimal_ = pd.DataFrame({
                "font": pd.Series(
                    self.font_names,
                    dtype=self._spec_dtypes["font"]),
                "size": pd.Series(
                    [self.font_sizes[0]] * len(self.font_names),
                    dtype=self._spec_dtypes["size"]),
                "width": pd.Series(
                    [self.font_widths[0]] * len(self.font_names),
                    dtype=self._spec_dtypes["width"]),
                "x_offset": pd.Series(
                    [self.font_x_offsets[0]] * len(self.font_names),
                    dtype=self._spec_dtypes["x_offset"]),
                "y_offset": pd.Series(
                    [self.font_y_offsets[0]] * len(self.font_names),
                    dtype=self._spec_dtypes["y_offset"])})

        return self._draw_specs_minimal_

    @property
    def _draw_specs_minimal_set(self):
        if not hasattr(self, "_draw_specs_minimal_set_"):
            self._draw_specs_minimal_set_ = set(
                map(tuple, self._draw_specs_minimal.values))
        return self._draw_specs_minimal_set_

    # endregion

    # region Public Methods

    def generate_additional_images(self, n_images=1, chars=None):
        import numpy as np
        import pandas as pd
        from random import sample
        from zysyzm.ocr import generate_char_image

        if chars is None:
            chars = self.chars[:self.n_chars]
        if not isinstance(chars, list):
            chars = list(chars)

        # Build queue of new specs
        queue = []
        for char in chars:
            specs = self._draw_specs_available_set.difference(
                self._get_specs_of_char_set(char))
            for spec in sample(specs, min(n_images, len(specs))):
                queue.append({
                    "char": char,
                    "font": spec[0],
                    "size": spec[1],
                    "width": spec[2],
                    "x_offset": spec[3],
                    "y_offset": spec[4]})

        if len(queue) >= 1:
            if self.verbosity >= 1:
                print(f"Generating {len(queue)} new images")

            # Prepare specs
            specs = pd.DataFrame(queue)

            # Prepare data
            data = np.zeros((len(queue), self._data_size), self._data_dtype)
            for i, spec in enumerate(queue):
                data[i] = self.image_to_data(generate_char_image(
                    fig=self._figure, image_mode=self.image_mode, **spec))

            self.add_images(specs, data)

    def generate_minimal_images(self):

        import numpy as np
        import pandas as pd
        from zysyzm.ocr import generate_char_image

        if self.verbosity >= 1:
            print(f"Checking for minimal image set")

        # Build queue of missing specs
        queue = []
        for i, char in enumerate(self.chars[:self.n_chars]):
            specs_of_char = self._get_specs_of_char_set(char)
            for _, spec in self._draw_specs_minimal.iterrows():
                if tuple(spec) not in specs_of_char:
                    spec = spec.to_dict()
                    spec["char"] = char
                    queue.append(spec)

        if len(queue) >= 1:
            if self.verbosity >= 1:
                print(f"Generating {len(queue)} new images for minimal set")

            # Prepare specs
            specs = pd.DataFrame(queue)

            # Prepare data
            data = np.zeros((len(queue), self._data_size), self._data_dtype)
            for i, spec in enumerate(queue):
                data[i] = self.image_to_data(generate_char_image(
                    fig=self._figure, image_mode=self.image_mode, **spec))

            self.add_images(specs, data)

    def get_data_for_training(self, val_portion=0.1):
        import numpy as np
        from random import sample

        all_trn_indexes = []
        all_val_indexes = []

        # Prepare trn and val sets with at least one image of each character
        for char in set(self.specs["char"]):
            specs = self._get_specs_of_char(char)
            n_specs = specs.index.size

            # Add at least one image of each character to each set
            trn_index, val_index = sample(specs.index.tolist(), 2)
            all_trn_indexes.append(trn_index)
            all_val_indexes.append(val_index)
            specs = specs.drop([trn_index, val_index])

            # Distribution remaining images across sets
            n_for_trn = int(np.floor(n_specs * (1 - val_portion)) - 1)
            n_for_val = int(np.ceil(n_specs * val_portion) - 1)
            if n_for_trn > 0:
                trn_indexes = sample(specs.index.tolist(), n_for_trn)
                all_trn_indexes.extend(trn_indexes)
                specs = specs.drop(trn_indexes)
            if n_for_val > 0:
                val_indexes = sample(specs.index.tolist(), n_for_val)
                all_val_indexes.extend(val_indexes)
                specs = specs.drop(val_indexes)

        # Organize data
        trn_img = self.data[all_trn_indexes]
        trn_lbl = self.chars_to_labels(
            self.specs["char"].loc[all_trn_indexes].values)
        val_img = self.data[all_val_indexes]
        val_lbl = self.chars_to_labels(
            self.specs["char"].loc[all_val_indexes].values)

        return trn_img, trn_lbl, val_img, val_lbl

    def get_trn_val_indexes(self, val_portion=0.1):
        import numpy as np
        from random import sample

        all_trn_indexes = []
        all_val_indexes = []

        # Prepare trn and val sets with at least one image of each character
        for char in set(self.specs["char"]):
            specs = self._get_specs_of_char(char)
            n_specs = specs.index.size

            # Add at least one image of each character to each set
            trn_index, val_index = sample(specs.index.tolist(), 2)
            all_trn_indexes.append(trn_index)
            all_val_indexes.append(val_index)
            specs = specs.drop([trn_index, val_index])

            # Distribution remaining images across sets
            n_for_trn = int(np.floor(n_specs * (1 - val_portion)) - 1)
            n_for_val = int(np.ceil(n_specs * val_portion) - 1)
            if n_for_trn > 0:
                trn_indexes = sample(specs.index.tolist(), n_for_trn)
                all_trn_indexes.extend(trn_indexes)
                specs = specs.drop(trn_indexes)
            if n_for_val > 0:
                val_indexes = sample(specs.index.tolist(), n_for_val)
                all_val_indexes.extend(val_indexes)
                specs = specs.drop(val_indexes)

        return all_trn_indexes, all_val_indexes

    def write_trn_val_image_dirs(self):
        from os import makedirs
        from os.path import dirname, isdir

        trn_image_dir = f"{self.output_image_dir.rstrip('trn')}trn"
        val_image_dir = f"{self.output_image_dir.rstrip('trn')}val"

        if self.verbosity >= 1:
            print(f"Writing images to '{trn_image_dir}'"
                  f"and {val_image_dir}")

        def trn_outfile_formatter(spec):
            return f"{trn_image_dir}/" \
                   f"{spec[1]['char']}_" \
                   f"{spec[1]['size']:02d}_" \
                   f"{spec[1]['width']:02d}_" \
                   f"{spec[1]['x_offset']:+d}_" \
                   f"{spec[1]['y_offset']:+d}_" \
                   f"{spec[1]['font'].replace(' ', '')}.png"

        def val_outfile_formatter(spec):
            return f"{val_image_dir}/" \
                   f"{spec[1]['char']}_" \
                   f"{spec[1]['size']:02d}_" \
                   f"{spec[1]['width']:02d}_" \
                   f"{spec[1]['x_offset']:+d}_" \
                   f"{spec[1]['y_offset']:+d}_" \
                   f"{spec[1]['font'].replace(' ', '')}.png"

        trn_indexes, val_indexes = self.get_trn_val_indexes()
        trn_outfiles = map(trn_outfile_formatter,
                           self.specs.loc[trn_indexes].iterrows())
        val_outfiles = map(val_outfile_formatter,
                           self.specs.loc[val_indexes].iterrows())
        trn_data = self.data[trn_indexes]
        val_data = self.data[val_indexes]
        for outfile, data in zip(trn_outfiles, trn_data):
            if self.verbosity >= 1:
                print(f"Writing '{outfile}'")
            if not isdir(dirname(outfile)):
                makedirs(dirname(outfile))
            self.image_array_to_object(data).save(outfile)
        for outfile, data in zip(val_outfiles, val_data):
            if self.verbosity >= 1:
                print(f"Writing '{outfile}'")
            if not isdir(dirname(outfile)):
                makedirs(dirname(outfile))
            self.image_array_to_object(data).save(outfile)

    # endregion

    # region Private Methods

    def _clear_private_property_caches(self):
        if hasattr(self, "_draw_specs_available_"):
            delattr(self, "_draw_specs_available_")
        if hasattr(self, "_draw_specs_available_set_"):
            delattr(self, "_draw_specs_available_set_")
        if hasattr(self, "_draw_specs_minimal_"):
            delattr(self, "_draw_specs_minimal_")
        if hasattr(self, "_draw_specs_minimal_set_"):
            delattr(self, "_draw_specs_minimal_set_")

    def _get_hdf5_input_spec_formatter(self, columns):
        """Provides spec formatter compatible with both numpy and h5py"""
        columns = list(columns)
        str_indexes = []
        if "path" in columns:
            str_indexes += [columns.index("path")]
        if "char" in columns:
            str_indexes += [columns.index("char")]
        if "font" in columns:
            str_indexes += [columns.index("font")]

        def func(x):
            x = list(x)
            for str_index in str_indexes:
                x[str_index] = x[str_index].decode("utf8")
            return tuple(x)

        return func

    def _get_hdf5_output_spec_formatter(self, columns):
        """Provides spec formatter compatible with both numpy and h5py"""
        columns = list(columns)
        str_indexes = []
        if "path" in columns:
            str_indexes += [columns.index("path")]
        if "char" in columns:
            str_indexes += [columns.index("char")]
        if "font" in columns:
            str_indexes += [columns.index("font")]

        def func(x):
            x = list(x)
            for str_index in str_indexes:
                if isinstance(x[str_index], float):
                    x[str_index] = ""
                x[str_index] = x[str_index].encode("utf8")
            return tuple(x)

        return func

    def _get_hdf5_spec_dtypes(self, columns):
        """Provides spec dtypes compatible with both numpy and h5py"""
        dtypes = {"path": "S255", "char": "S3", "font": "S10",
                  "size": "i1", "width": "i1", "x_offset": "i1",
                  "y_offset": "i1"}
        return list(zip(columns, [dtypes[k] for k in columns]))

    def _get_image_dir_input_specs(self, infiles):
        """Provides specs of infiles"""
        import pandas as pd
        from os.path import basename

        chars = list(map(lambda x: basename(x).split("_")[0],
                         infiles))
        sizes = list(map(lambda x: int(basename(x).split("_")[1]),
                         infiles))
        widths = list(map(lambda x: int(basename(x).split("_")[2]),
                          infiles))
        x_offsets = list(map(lambda x: int(basename(x).split("_")[3]),
                             infiles))
        y_offsets = list(map(lambda x: int(basename(x).split("_")[4]),
                             infiles))
        fonts = list(map(lambda x: basename(x).split("_")[5].split(".")[0],
                         infiles))

        specs = {
            "path": pd.Series(
                infiles, dtype=self._spec_dtypes["path"]),
            "char": pd.Series(
                chars, dtype=self._spec_dtypes["char"]),
            "font": pd.Series(
                fonts, dtype=self._spec_dtypes["font"]),
            "size": pd.Series(
                sizes, dtype=self._spec_dtypes["size"]),
            "width": pd.Series(
                widths, dtype=self._spec_dtypes["width"]),
            "x_offset": pd.Series(
                x_offsets, dtype=self._spec_dtypes["x_offset"]),
            "y_offset": pd.Series(
                y_offsets, dtype=self._spec_dtypes["y_offset"])}

        return pd.DataFrame(data=specs, index=range(len(infiles)))

    def _get_image_dir_outfile_formatter(self, specs, outdir):
        """Provides formatter for image outfile paths"""

        def func(spec):
            return f"{outdir}/" \
                   f"{spec[1]['char']}_" \
                   f"{spec[1]['size']:02d}_" \
                   f"{spec[1]['width']:02d}_" \
                   f"{spec[1]['x_offset']:+d}_" \
                   f"{spec[1]['y_offset']:+d}_" \
                   f"{spec[1]['font'].replace(' ', '')}.png"

        return func

    def _get_specs_of_char(self, char):
        return self.specs.loc[self.specs["char"] == char][
            ["font", "size", "width", "x_offset", "y_offset"]]

    def _get_specs_of_char_set(self, char):
        return set(map(tuple, self._get_specs_of_char(char).values))

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    GeneratedOCRDataset.main()
