#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.LabeledOCRDataset,py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile.ocr import OCRDataset
from IPython import embed


################################### CLASSES ###################################
class LabeledOCRDataset(OCRDataset):
    """
    Represents a collection of labeled character images

    Todo:
      - [ ] Document
      - [ ] Don't allow 'path' to be set to NaN
    """

    # region Instance Variables

    help_message = ("Represents a collection of labeled character images")

    # endregion

    # region Builtins

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # self.input_image_dir = \
        #     "/Users/kdebiec/Desktop/docs/subtitles/tst"
        # self.input_hdf5 = \
        #     "/Users/kdebiec/Desktop/docs/subtitles/tst/labeled.h5"
        # self.output_hdf5 = \
        #     "/Users/kdebiec/Desktop/docs/subtitles/tst/labeled.h5"
        # self.output_image_dir = \
        #     "/Users/kdebiec/Desktop/labeled"

    def __call__(self):
        """ Core logic """

        # Input
        if self.input_hdf5 is not None:
            self.read_hdf5()
        if self.input_image_dir is not None:
            self.read_image_dir()

        # Output
        if self.output_hdf5 is not None:
            self.write_hdf5()
        if self.output_image_dir is not None:
            self.write_image_dir()

        # Present IPython prompt
        if self.interactive:
            embed(**self.embed_kw)

    # endregion

    # region Private Properties

    @property
    def _spec_columns(self):
        """list(str): Character image specification columns"""

        return ["path", "char"]

    @property
    def _spec_dtypes(self):
        """list(str): Character image specification dtypes"""
        return {"path": str, "char": str}

    # endregion

    # region Public Methods

    def get_images_and_labels(self, indexes=None):
        if indexes is None:
            img = self.data
            lbl = self.chars_to_labels(self.specs["char"].values)
        else:
            img = self.data[indexes]
            lbl = self.chars_to_labels(self.specs["char"].loc[indexes].values)

        return img, lbl

    # endregion

    # region Private Methods

    def _get_hdf5_input_spec_formatter(self, columns):
        """Provides spec formatter compatible with both numpy and h5py"""
        columns = list(columns)
        str_indexes = []
        if "path" in columns:
            str_indexes += [columns.index("path")]
        if "char" in columns:
            str_indexes += [columns.index("char")]

        def func(x):
            x = list(x)
            for str_index in str_indexes:
                x[str_index] = x[str_index].decode("utf8")
            return tuple(x)

        return func

    def _list_image_dir_input_files(self, path):
        """Provides infiles within path"""
        from glob import iglob

        return sorted(iglob(f"{path}/**/*.png", recursive=True))

    def _get_image_dir_input_specs(self, infiles):
        """Provides specs of infiles"""
        import numpy as np
        import pandas as pd
        from os.path import basename

        chars = list(map(lambda x: basename(x)[0], infiles))

        return pd.DataFrame(data=np.array([infiles, chars]).transpose(),
                            index=range(len(infiles)),
                            columns=self._spec_columns)

    def _get_hdf5_spec_dtypes(self, columns):
        """Provides spec dtypes compatible with both numpy and h5py"""
        dtypes = {"path": "S255", "char": "S3"}
        return list(zip(columns, [dtypes[k] for k in columns]))

    def _get_hdf5_output_spec_formatter(self, columns):
        """Provides spec formatter compatible with both numpy and h5py"""
        columns = list(columns)
        str_indexes = []
        if "path" in columns:
            str_indexes += [columns.index("path")]
        if "char" in columns:
            str_indexes += [columns.index("char")]

        def func(x):
            x = list(x)
            for str_index in str_indexes:
                x[str_index] = x[str_index].encode("utf8")
            return tuple(x)

        return func

    def _get_image_dir_outfile_formatter(self, specs, outdir):
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
                return f"{outdir}/" \
                       f"{base_path_remover(spec[1]['path'])}"

            return func
        else:
            def func(spec):
                return f"{outdir}/" \
                       f"{spec[1]['char']}_{spec[0]:06d}.png"

            return func

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    LabeledOCRDataset.main()
