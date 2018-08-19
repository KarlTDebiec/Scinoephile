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
      - [x] Read image directory
      - [x] Add images
      - [ ] Write hdf5
      - [ ] Read hdf5
      - [ ] Write image directory
      - [ ] Document
    """

    # region Instance Variables

    help_message = ("Represents a collection of unlabeled character images")

    # endregion

    # region Builtins

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.input_image_directory = \
            "/Users/kdebiec/Desktop/docs/subtitles/magnificent_mcdull"

    def __call__(self):
        """ Core logic """

        # Initialize
        if self.input_hdf5 is not None:
            self.read_hdf5()
        if self.input_image_directory is not None:
            self.read_image_directory()

        # Present IPython prompt
        if self.interactive:
            self.embed()

    # endregion

    # region Properties

    @property
    def char_image_spec_columns(self):
        """list(str): Character image specification columns"""

        if hasattr(self, "_char_image_specs"):
            return self.char_image_specs.columns.values
        else:
            return ["path"]

    # endregion

    # region Public Methods

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

    def write_hdf5(self):
        import h5py
        import numpy as np

        def clean_spec_for_hdf5(row):
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

    # endregion

    # Private Methods

    def _read_image_directory_infiles(self, path):
        from glob import iglob

        return sorted(iglob(f"{path}/**/[0-9][0-9].png", recursive=True))

    def _read_image_directory_specs(self, infiles):
        import pandas as pd

        return pd.DataFrame(data=infiles,
                            index=range(len(infiles)),
                            columns=self.char_image_spec_columns)

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    UnlabeledOCRDataset.main()
