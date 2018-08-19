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
from IPython import embed


################################### CLASSES ###################################
class LabeledOCRDataset(OCRDataset):
    """
    Represents a collection of labeled character images

    Todo:
      - [x] Read image directory
      - [x] Add images
      - [x] Write hdf5
      - [ ] Read hdf5
      - [ ] Write image directory
      - [ ] Document
    """

    # region Instance Variables

    help_message = ("Represents a collection of labeled character images")

    # endregion

    # region Builtins

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.input_image_directory = \
            "/Users/kdebiec/Desktop/docs/subtitles/tst"
        self.output_hdf5 = \
            "/Users/kdebiec/Desktop/docs/subtitles/tst/labeled.h5"

    def __call__(self):
        """ Core logic """

        # Input
        if self.input_hdf5 is not None:
            self.read_hdf5()
        if self.input_image_directory is not None:
            self.read_image_directory()

        # Output
        if self.output_hdf5 is not None:
            self.write_hdf5()

        # Present IPython prompt
        if self.interactive:
            embed(**self.embed_kw)

    # endregion

    # region Properties

    @property
    def char_image_spec_columns(self):
        """list(str): Character image specification columns"""

        if hasattr(self, "_char_image_specs"):
            return self.char_image_specs.columns.values
        else:
            return ["path", "character"]

    # endregion

    # Private Methods

    def _output_hdf5_spec_format(self, row):
        """
        Formats spec for compatibility with both numpy and h5py

        - Converted into a tuple for numpy to build a record array
        - Characters converted from unicode strings to integers. hdf5 and
          numpy's unicode support do not cooperate well, and this is the
          least painful solution.
        """
        row = list(row)
        if "path" in self.char_image_specs.columns.values:
            path_index = list(
                self.char_image_specs.columns.values).index("path")
            row[path_index] = row[path_index].encode("utf8")
        if "character" in self.char_image_specs.columns.values:
            char_index = list(
                self.char_image_specs.columns.values).index("character")
            row[char_index] = row[char_index].encode("utf8")
        return tuple(row)

    def _output_hdf5_spec_dtypes(self):
        """Provides spec dtypes for compatibility with both numpy and h5py"""
        dtypes = {"path": "S255", "character": "S3"}
        return list(zip(self.char_image_specs.columns.values,
                        [dtypes[k] for k in
                         list(self.char_image_specs.columns.values)]))

    def _read_image_directory_infiles(self, path):
        """Provides infiles within path"""
        from glob import iglob

        return sorted(iglob(f"{path}/**/*.png", recursive=True))

    def _read_image_directory_specs(self, infiles):
        """Provides specs of infiles"""
        import numpy as np
        import pandas as pd
        from os.path import basename

        chars = list(map(lambda x: basename(x)[0], infiles))

        return pd.DataFrame(data=np.array([infiles, chars]).transpose(),
                            index=range(len(infiles)),
                            columns=self.char_image_spec_columns)

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    LabeledOCRDataset.main()
