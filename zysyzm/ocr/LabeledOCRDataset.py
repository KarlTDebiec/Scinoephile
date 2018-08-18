#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.ocr.LabeledOCRDataset,py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from zysyzm.ocr import OCRDataset


################################### CLASSES ###################################
class LabeledOCRDataset(OCRDataset):
    """Represents a collection of labeled character images

    Todo:
      - [ ] Refactor
      - [ ] Document
    """

    # region Instance Variables

    help_message = ("Represents a collection of labeled character images")

    # endregion

    # region Builtins

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Store property values

        # Initialize
        if self.input_hdf5 is not None:
            self.read_hdf5()
        else:
            self.initialize_from_scratch()

    # endregion

    # region Properties
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
    def char_image_data(self):
        """numpy.ndarray(bool): Character image data"""
        return self._char_image_data

    @char_image_data.setter
    def char_image_data(self, value):
        # Todo: Validate
        self._char_image_data = value

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
        import pandas as pd
        import numpy as np

        base_spec = self.char_image_specs_available.loc[0]

        # Prepare empty arrays
        self.char_image_specs = pd.DataFrame(
            index=range(self.n_chars),
            columns=self.char_image_specs.columns.values)
        self.char_image_data = np.zeros(
            (self.n_chars, self.image_data_size), dtype=self.image_data_dtype)

        # Fill in arrays with specs and data
        for i, char in enumerate(self.chars[:self.n_chars]):
            row = base_spec.to_dict()
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

    # endregion
