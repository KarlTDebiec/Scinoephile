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


################################### CLASSES ###################################
class GeneratedOCRDataset(LabeledOCRDataset):
    """Represents a collection of generated character images

    Todo:
      - Refactor
      - Support for creation of training and validaiton datasets, with at
        least on image of each character in each
      - Document
    """

    # region Builtins

    def __init__(self, font_names=None, font_sizes=None, font_widths=None,
                 font_x_offsets=None, font_y_offsets=None, hdf5_infile=None,
                 hdf5_outfile=None, image_mode=None, n_chars=None, **kwargs):
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
        if hdf5_infile is not None:
            self.input_hdf5 = hdf5_infile
        if image_mode is not None:
            self.image_mode = image_mode
        if n_chars is not None:
            self.n_chars = n_chars
        if hdf5_infile is not None:
            self.input_hdf5 = hdf5_infile
        if hdf5_outfile is not None:
            self.output_hdf5 = hdf5_outfile

        # Initialize
        if self.input_hdf5 is not None:
            self.read_hdf5()
        else:
            self.initialize_from_scratch()

    # endregion

    # region Properties

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
    def char_image_specs(self):
        """pandas.DataFrame: Character image specifications"""
        if not hasattr(self, "_char_image_specs"):
            import pandas as pd

            self._char_image_specs = pd.DataFrame(
                columns=["character", "font", "size", "width", "x_offset",
                         "y_offset"])
        return self._char_image_specs

    @char_image_specs.setter
    def char_image_specs(self, value):
        # Todo: Validate
        self._char_image_specs = value

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

    # region Methods

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

    def image_to_data(self, image):
        import numpy as np

        if self.image_mode == "8bit":
            data = np.array(image).flatten()
        elif self.image_mode == "2bit":
            raw = np.array(image).flatten()
            data = np.zeros((2 * raw.size), np.bool)
            data[0::2][np.logical_or(raw == 170, raw == 255)] = True
            data[1::2][np.logical_or(raw == 85, raw == 255)] = True
        elif self.image_mode == "1bit":
            raise NotImplementedError()

        return data

    def data_to_image(self, data):
        import numpy as np
        from IPython import embed
        from PIL import Image

        if self.image_mode == "8bit":
            raise NotImplementedError()
        elif self.image_mode == "2bit":
            raw = np.zeros((data.size // 2), np.uint8)
            raw[np.logical_and(data[0::2] == False, data[1::2] == True)] = 85
            raw[np.logical_and(data[0::2] == True, data[1::2] == False)] = 170
            raw[np.logical_and(data[0::2] == True, data[1::2] == True)] = 255
            raw = raw.reshape((int(np.sqrt(raw.size)), int(np.sqrt(raw.size))))
            image = Image.fromarray(raw, mode="L")
        elif self.image_mode == "1bit":
            raise NotImplementedError()

        return image

    def read_hdf5(self):
        import pandas as pd
        import h5py
        import numpy as np

        def clean_spec_for_pandas(row):
            """
            Processes spec for pandas

            - Converted into a tuple for pandas to build DataFrame
            - Characters converted from integers back to unicode. hdf5 and
              numpy's unicode support do not cooperate well, and this is the
              least painful solution.
            """
            return tuple([chr(row[0])] + list(row)[1:])

        if self.verbosity >= 1:
            print(f"Reading data from '{self.input_hdf5}'")
        with h5py.File(self.input_hdf5) as hdf5_infile:
            if "char_image_specs" not in hdf5_infile:
                raise ValueError()
            if "char_image_data" not in hdf5_infile:
                raise ValueError()

            # Load configuration
            self.image_mode = hdf5_infile.attrs["mode"]

            # Load character image data
            self.char_image_data = np.array(hdf5_infile["char_image_data"])

            # Load character image specification
            self.char_image_specs = pd.DataFrame(
                index=range(self.char_image_data.shape[0]),
                columns=self.char_image_specs.columns.values)
            self.char_image_specs[:] = list(map(
                clean_spec_for_pandas,
                np.array(hdf5_infile["char_image_specs"])))

    def initialize_from_scratch(self):
        import numpy as np
        import pandas as pd

        # Prepare empty arrays
        self.char_image_specs = pd.DataFrame(
            index=range(self.n_chars),
            columns=self.char_image_specs.columns.values)
        self.char_image_data = np.zeros(
            (self.n_chars, self.image_data_size), dtype=self.image_data_dtype)

        # Fill in arrays with specs and data
        for i, char in enumerate(self.chars[:self.n_chars]):
            row = self.char_image_specs_available.loc[0].to_dict()
            row["character"] = char
            self.char_image_specs.loc[i] = row
            self.char_image_data[i] = self.image_to_data(
                self.generate_char_image(**row))

    def write_hdf5(self):
        import h5py
        import numpy as np

        def clean_spec_for_hdf5(row):
            """
            Processes specification for numpy and h5py

            - Converted into a tuple for numpy to build a record array
            - Characters converted from unicode strings to integers. hdf5 and
              numpy's unicode support do not cooperate well, and this is the
              least painful solution.
            """
            return tuple([ord(row[0])] + list(row[1:]))

        if self.verbosity >= 1:
            print(f"Saving data to '{self.output_hdf5}'")
        with h5py.File(self.output_hdf5) as hdf5_outfile:
            # Remove prior data
            if "char_image_data" in hdf5_outfile:
                del hdf5_outfile["char_image_data"]
            if "char_image_specs" in hdf5_outfile:
                del hdf5_outfile["char_image_specs"]

            # Save configuration
            hdf5_outfile.attrs["mode"] = self.image_mode

            # Save character image specifications
            char_image_specs = list(map(clean_spec_for_hdf5,
                                        self.char_image_specs.values))
            dtypes = list(zip(self.char_image_specs.columns.values,
                              ["i4", "S10", "i1", "i1", "i1", "i1"]))
            char_image_specs = np.array(char_image_specs, dtype=dtypes)
            hdf5_outfile.create_dataset("char_image_specs",
                                        data=char_image_specs, dtype=dtypes,
                                        chunks=True, compression="gzip")

            # Save character image data
            hdf5_outfile.create_dataset("char_image_data",
                                        data=self.char_image_data,
                                        dtype=self.image_data_dtype,
                                        chunks=True, compression="gzip")

    def view_char_image(self, indexes, columns=None):
        import numpy as np
        from PIL import Image

        # Process arguments
        if isinstance(indexes, int):
            indexes = [indexes]
        indexes = np.array(indexes, np.int)
        if np.any(indexes >= self.char_image_data.shape[0]):
            raise ValueError()
        if columns is None:
            columns = indexes.size
            rows = 1
        else:
            rows = int(np.ceil(indexes.size / columns))

        # Draw image
        image = Image.new("L", (columns * 100, rows * 100), 255)
        for i, index in enumerate(indexes):
            column = (i // columns)
            row = i - (column * columns)
            char_image = self.data_to_image(self.char_image_data[index])
            image.paste(char_image,
                        (100 * row + 10,
                         100 * column + 10,
                         100 * (row + 1) - 10,
                         100 * (column + 1) - 10))
        image.show()

    def output_char_image(self, char, font_name="Hei", font_size=60,
                          border_width=5, x_offset=0, y_offset=0, **kwargs):
        """
        Outputs an image of a character, if output image does not exist

        Args:
            char (str): character to generate an image of
            font_name (str, optional): font with which to draw character
            font_size (int, optional): font size with which to draw character
            border_width (int, optional: border width with which to draw
              character
            x_offset (int, optional): x offset to apply to character
            y_offset (int, optional: y offset to apply to character
            **kwargs (dict):

        """
        import numpy as np
        from os.path import isfile
        from zysyzm.ocr import generate_char_image

        # Check if outfile exists, and if not choose output location
        outfile = f"{char}_{font_size:02d}_{border_width:02d}_" \
                  f"{x_offset:+d}_{y_offset:+d}_" \
                  f"{font_name.replace(' ', '')}.png"
        outfile = f"{self.trn_output_directory}/{outfile}"
        if isfile(f"{self.trn_output_directory}/{outfile}"):
            return

        # Generate image
        img = generate_char_image(char, font_name=font_name,
                                  font_size=font_size,
                                  border_width=border_width, x_offset=x_offset,
                                  y_offset=y_offset, **kwargs)
        img.save(outfile)
        if self.verbosity >= 2:
            print(f"Wrote '{outfile}'")

    # endregion
