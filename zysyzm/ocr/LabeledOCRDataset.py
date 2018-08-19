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
    """Represents a collection of labeled character images

    Todo:
      - [x] Read image directory
      - [x] Add images
      - [ ] Write hdf5
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

    def __call__(self):
        """ Core logic """

        # Initialize
        if self.input_hdf5 is not None:
            self.read_hdf5()
        if self.input_image_directory is not None:
            self.read_image_directory()

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

    # region Methods

    # endregion

    # Private Methods

    def _read_image_directory_infiles(self, path):
        from glob import iglob

        return sorted(iglob(f"{path}/**/*.png", recursive=True))

    def _read_image_directory_specs(self, infiles):
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
