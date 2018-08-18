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
