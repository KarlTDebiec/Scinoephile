#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.UnlabeledOCRDataset,py
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
class UnlabeledOCRDataset(OCRDataset):
    """
    A collection of unlabeled character images

    .. todo::
      - [x] Read image directory
      - [x] Add images
      - [x] Write hdf5
      - [x] Read hdf5
      - [x] Write image directory
    """

    # region Builtins

    def __call__(self):
        """ Core logic """

        # Input
        if self.infile is not None:
            self.load()

        # Output
        if self.outfile is not None:
            self.save()

        # Present IPython prompt
        if self.interactive:
            embed(**self.embed_kw)

    # endregion

    # region Private Properties

    @property
    def _imagespec_columns(self):
        """list(str): Character image specification columns"""

        return ["path"]

    @property
    def _imagespec_dtypes(self):
        """list(str): Character image specification dtypes"""
        return {"path": str}

    # endregion

    # region Private Methods

    def _get_hdf5_input_spec_formatter(self, columns):
        """Provides spec formatter compatible with both numpy and h5py"""
        columns = list(columns)

        if "path" in columns:
            path_index = columns.index("path")

            def func(x):
                x = list(x)
                x[path_index] = x[path_index].decode("utf8")
                return tuple(x)
        else:
            def func(x):
                return tuple(x)

        return func

    def _list_image_dir_input_files(self, path):
        """Provides infiles within path"""
        from glob import iglob

        return sorted(iglob(f"{path}/**/[0-9][0-9].png", recursive=True))

    def _get_image_dir_input_specs(self, infiles):
        """Provides specs of infiles"""
        import pandas as pd

        return pd.DataFrame(data=infiles,
                            index=range(len(infiles)),
                            columns=self._imagespec_columns)

    def _get_hdf5_spec_dtypes(self, columns):
        """Provides spec dtypes compatible with both numpy and h5py"""
        dtypes = {"path": "S255"}
        return list(zip(columns, [dtypes[k] for k in columns]))

    def _get_hdf5_output_spec_formatter(self, columns):
        """Provides spec formatter compatible with both numpy and h5py"""
        columns = list(columns)

        if "path" in columns:
            path_index = columns.index("path")

            def func(x):
                x = list(x)
                x[path_index] = x[path_index].encode("utf8")
                return tuple(x)
        else:
            def func(x):
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
                       f"{spec[0]:06d}.png"

            return func

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    UnlabeledOCRDataset.main()
