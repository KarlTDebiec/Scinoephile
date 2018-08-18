#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.ocr.UnlabeledOCRDataset,py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from zysyzm.ocr import OCRDataset


################################### CLASSES ###################################
class UnlabeledOCRDataset(OCRDataset):
    """Represents a collection of unlabeled character images

    Todo:
      - Refactor
      - Read in unlabeled data
      - Document
    """

    # region Builtins

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from IPython import embed

        # Initialize
        if self.input_hdf5 is not None:
            self.read_hdf5()
        if self.input_image_directory is not None:
            self.read_image_directory()

        embed()

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

    # endregion

    # region Methods
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

#################################### MAIN #####################################
if __name__ == "__main__":
    UnlabeledOCRDataset.main()
