#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.GeneratedOCRDataset,py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile.ocr import LabeledOCRDataset
from IPython import embed


################################### CLASSES ###################################
class GeneratedOCRDataset(LabeledOCRDataset):
    """
    A collection of generated character images
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

    def __call__(self):
        """ Core logic """

        # Input
        if self.infile is not None:
            self.load()

        # Action
        self.generate_minimal_img()
        self.generate_additional_img(2)

        # Output
        if self.outfile is not None:
            self.save()

        # Present IPython prompt
        if self.interactive:
            embed(**self.embed_kw)

    # endregion

    # region Public Properties

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
            self._font_names = [
                "/System/Library/Fonts/STHeiti Light.ttc",
                "/System/Library/Fonts/STHeiti Medium.ttc",
                "/System/Library/Fonts/PingFang.ttc",
                "/Library/Fonts/Songti.ttc"]
        return self._font_names

    @font_names.setter
    def font_names(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [str(v) for v in list(value)]
                except Exception:
                    raise ValueError(self._generate_setter_exception(value))
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
                except Exception:
                    raise ValueError(self._generate_setter_exception(value))
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
                    raise ValueError(self._generate_setter_exception(value))
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
                    raise ValueError(self._generate_setter_exception(value))
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
                    raise ValueError(self._generate_setter_exception(value))
        self._font_y_offsets = value

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

    @property
    def spec_all(self):
        """pandas.DataFrame: All available character image specs"""
        if not hasattr(self, "_spec_all"):
            import pandas as pd
            from itertools import product

            fonts, sizes, widths, x_offsets, y_offsets = tuple(zip(*product(
                self.font_names, self.font_sizes, self.font_widths,
                self.font_x_offsets, self.font_y_offsets)))

            self._spec_all = pd.DataFrame({
                "font": pd.Series(fonts,
                                  dtype=self.spec_dtypes["font"]),
                "size": pd.Series(sizes,
                                  dtype=self.spec_dtypes["size"]),
                "width": pd.Series(widths,
                                   dtype=self.spec_dtypes["width"]),
                "x_offset": pd.Series(x_offsets,
                                      dtype=self.spec_dtypes["x_offset"]),
                "y_offset": pd.Series(y_offsets,
                                      dtype=self.spec_dtypes["y_offset"])})
        return self._spec_all

    @property
    def spec_all_set(self):
        """set(tuple): Set of minimal character image specs"""
        if not hasattr(self, "_spec_all_set"):
            self._spec_all_set = set(map(tuple, self.spec_all.values))
        return self._spec_all_set

    @property
    def spec_cols(self):
        """list(str): Character image specification columns"""

        if hasattr(self, "_spec"):
            return self.spec.columns.values
        else:
            return ["char", "font", "size", "width", "x_offset", "y_offset"]

    @property
    def spec_dtypes(self):
        """list(str): Character image specification dtypes"""
        return {"path": str, "char": str, "font": str, "size": int,
                "width": int, "x_offset": int, "y_offset": int}

    @property
    def spec_min(self):
        """pandas.DataFrame: Minimal character image specs"""
        if not hasattr(self, "_spec_min"):
            import pandas as pd

            self._spec_min = pd.DataFrame({
                "font": pd.Series(self.font_names,
                                  dtype=self.spec_dtypes["font"]),
                "size": pd.Series([self.font_sizes[0]] * len(self.font_names),
                                  dtype=self.spec_dtypes["size"]),
                "width": pd.Series([self.font_widths[0]] * len(self.font_names),
                                   dtype=self.spec_dtypes["width"]),
                "x_offset": pd.Series([self.font_x_offsets[0]] * len(self.font_names),
                                      dtype=self.spec_dtypes["x_offset"]),
                "y_offset": pd.Series([self.font_y_offsets[0]] * len(self.font_names),
                                      dtype=self.spec_dtypes["y_offset"])})
        return self._spec_min

    @property
    def spec_min_set(self):
        """set(tuple): Set of minimal character image specs"""
        if not hasattr(self, "_spec_min_set"):
            self._spec_min_set = set(map(tuple, self.spec_min.values))
        return self._spec_min_set

    # endregion

    # region Public Methods

    def existing_specs_of_char(self, char):
        return set(map(tuple, self.spec.loc[self.spec["char"] == char].drop(
            "char", axis=1).values))

    def generate_minimal_img(self):
        import numpy as np
        import pandas as pd
        from scinoephile.ocr import generate_char_img

        # Process arguments
        if self.verbosity >= 1:
            print(f"Checking for minimal image set")

        # Build queue of needed specs
        queue = []
        to_dict = lambda x: {k: v for k, v in zip(self.spec_cols, (char, *x))}
        for char in self.chars[:self.n_chars]:
            existing = self.existing_specs_of_char(char)
            needed = self.spec_min_set.difference(existing)
            queue.extend(map(to_dict, needed))

        # Generate and add images
        if len(queue) >= 1:
            if self.verbosity >= 1:
                print(f"Generating {len(queue)} new images for minimal set")

            spec = pd.DataFrame(queue)
            data = np.zeros((len(queue), self.data_size), self.data_dtype)
            for i, kwargs in enumerate(queue):
                data[i] = generate_char_img(fig=self.figure, mode=self.mode, **kwargs)

            self.add_img(spec, data)

    def generate_additional_img(self, n_images=1, chars=None):
        import numpy as np
        import pandas as pd
        from random import sample
        from scinoephile.ocr import generate_char_img

        # Process arguments
        if chars is None:
            chars = self.chars[:self.n_chars]
        if not isinstance(chars, list):
            chars = list(chars)
        if self.verbosity >= 1:
            print(f"Generating {n_images} new images for each of {len(chars)} "
                  f"characters")

        # Build queue of new specs
        queue = []
        to_dict = lambda x: {k: v for k, v in zip(self.spec_cols, (char, *x))}
        for char in chars:
            existing = self.existing_specs_of_char(char)
            available = self.spec_all_set.difference(existing)
            selected = sample(available, min(n_images, len(available)))
            queue.extend(map(to_dict, selected))

        # Generate and add images
        if len(queue) >= 1:
            if self.verbosity >= 1:
                print(f"Generating {len(queue)} new images")

            specs = pd.DataFrame(queue)
            data = np.zeros((len(queue), self.data_size), self.data_dtype)
            for i, kwargs in enumerate(queue):
                data[i] = generate_char_img(fig=self.figure, mode=self.mode, **kwargs)

            self.add_img(specs, data)

    def get_trn_val_indexes(self, val_portion=0.1):
        """
        import numpy as np
        from random import sample

        all_trn_indexes = []
        all_val_indexes = []

        # Prepare trn and val sets with at least one image of each character
        for char in set(self.spec["char"]):
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
        """
        raise NotImplementedError()

    # endregion

    # region Private Methods

    def _load_hdf5(self, fp, **kwargs):
        import pandas as pd
        import numpy as np

        decode = lambda x: x.decode("utf8")

        # Load image mode
        self.mode = fp.attrs["mode"]

        # Load image specs
        if "spec" not in fp:
            return  # Do not need to raise if hdf5 is empty
        spec = np.array(fp["spec"])
        spec = pd.DataFrame(data=spec, index=range(spec.size), columns=spec.dtype.names)
        spec["char"] = spec["char"].apply(decode)
        spec["font"] = spec["font"].apply(decode)

        # Load image data
        if "data" not in fp:
            raise ValueError()  # Need to raise if hdf5 has specs but no data
        data = np.array(fp["data"])

        self.add_img(spec, data)

    def _save_hdf5(self, fp, **kwargs):
        import numpy as np

        dtypes = [
            ("char", "S3"),
            ("font", "S255"),
            ("size", "i1"),
            ("width", "i1"),
            ("x_offset", "i1"),
            ("y_offset", "i1")]
        encode = lambda x: x.encode("utf8")

        # Save image mode
        fp.attrs["mode"] = self.mode

        # Save image specs
        if "spec" in fp:
            del fp["spec"]
        encoded = self.spec.copy()
        encoded["char"] = encoded["char"].apply(encode)
        encoded["font"] = encoded["font"].apply(encode)
        encoded = np.array(list(map(tuple, list(encoded.values))), dtype=dtypes)
        fp.create_dataset("spec",
                          data=encoded, dtype=dtypes,
                          chunks=True, compression="gzip")

        # Save iamge data
        if "data" in fp:
            del fp["data"]
        fp.create_dataset("data",
                          data=self.data, dtype=self.data_dtype,
                          chunks=True, compression="gzip")

    # endregion
