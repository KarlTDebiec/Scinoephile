#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.OCRDataset.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile.ocr import OCRCLToolBase
from IPython import embed


################################### CLASSES ###################################
class OCRDataset(OCRCLToolBase):
    """
    A collection of character images
    """

    # region Builtins

    def __init__(self, infile=None, outfile=None, imgmode=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if infile is not None:
            self.infile = infile
        if outfile is not None:
            self.outfile = outfile
        if imgmode is not None:
            self.imgmode = imgmode

    def __call__(self):
        """ Core logic """
        raise NotImplementedError()

    # endregion

    # region Public Properties

    @property
    def imgspec(self):
        """pandas.DataFrame: Character image specifications"""
        if not hasattr(self, "_imgspec"):
            import pandas as pd

            self._imgspec = pd.DataFrame({
                c: pd.Series([], dtype=self._imgspec_dtypes[c])
                for c in self._imgspec_cols})
        return self._imgspec

    @imgspec.setter
    def imgspec(self, value):
        # Todo: Validate
        self._imgspec = value

    @property
    def imgdata(self):
        """numpy.ndarray(bool): Character image data"""
        if not hasattr(self, "_imgdata"):
            import numpy as np

            self._imgdata = np.zeros(
                (0, self._imgdata_size), self._imgdata_dtype)
        return self._imgdata

    @imgdata.setter
    def imgdata(self, value):
        import numpy as np

        if not isinstance(value, np.ndarray):
            raise ValueError(self._generate_setter_exception(value))
        if value.shape[1] != self._imgdata_size:
            raise ValueError(self._generate_setter_exception(value))
        if value.dtype != self._imgdata_dtype:
            raise ValueError(self._generate_setter_exception(value))
        self._imgdata = value

    @property
    def imgmode(self):
        """str: Image mode"""
        if not hasattr(self, "_imgmode"):
            self._imgmode = "1 bit"
        return self._imgmode

    @imgmode.setter
    def imgmode(self, value):
        if value is not None:
            if not isinstance(value, str):
                try:
                    value = str(value)
                except Exception:
                    raise ValueError(self._generate_setter_exception(value))
            if value == "8 bit":
                pass
            elif value == "1 bit":
                pass
            else:
                raise ValueError(self._generate_setter_exception(value))
        # TODO: Respond to changes appropriately

        self._imgmode = value

    @property
    def infile(self):
        """str: Path to input file"""
        if not hasattr(self, "_infile"):
            self._infile = None
        return self._infile

    @infile.setter
    def infile(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._infile = value

    @property
    def outfile(self):
        """str: Path to output file"""
        if not hasattr(self, "_outfile"):
            self._outfile = None
        return self._outfile

    @outfile.setter
    def outfile(self, value):
        from os import access, getcwd, R_OK, W_OK
        from os.path import dirname, expandvars, isfile

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
            elif isfile(value) and not access(value, R_OK):
                raise ValueError(self._generate_setter_exception(value))
            elif dirname(value) == "" and not access(getcwd(), W_OK):
                raise ValueError(self._generate_setter_exception(value))
            # TODO: Validate if directory exists or can be created
        self._outfile = value

    # endregion

    # region Private Properties

    @property
    def _imgspec_cols(self):
        """list(str): Character image specification columns"""
        raise NotImplementedError()

    @property
    def _imgspec_dtypes(self):
        """list(str): Character image specification dtypes"""
        raise NotImplementedError()

    @property
    def _imgspec_set(self):
        """set: Unique character image specs"""
        if not hasattr(self, "_imgspec_set_"):
            self._imgspec_set_ = set(map(tuple, self.imgspec.values))
        return self._imgspec_set_

    @property
    def _imgdata_size(self):
        """int: Size of a single image within arrays"""
        if self.imgmode == "8 bit":
            return 6400
        elif self.imgmode == "1 bit":
            return 6400
        else:
            raise NotImplementedError()

    @property
    def _imgdata_dtype(self):
        """type: dtype of image arrays"""
        import numpy as np

        if self.imgmode == "8 bit":
            return np.int8
        elif self.imgmode == "1 bit":
            return np.bool
        else:
            raise NotImplementedError()

    # endregion

    # region Public Methods

    def add_img(self, imgspec, imgdata):
        """
        Adds new images

        Args:
            imgspec (pandas.DataFrame): New image specifications
            imgdata (numpy.ndarray): New image data
        """
        import numpy as np

        new = imgspec.apply(
            lambda x: tuple(x.values) not in self._imgspec_set,
            axis=1).values
        if new.sum() >= 1:
            self.imgspec = self.imgspec.append(
                imgspec.loc[new], ignore_index=True, sort=False)
            self.imgdata = np.append(
                self.imgdata, imgdata[new], axis=0)

    def read_hdf5(self):
        """
        import pandas as pd
        import h5py
        import numpy as np

        if self.verbosity >= 1:
            print(f"Reading images from '{self.input_hdf5}'")
        with h5py.File(self.input_hdf5) as hdf5_infile:
            if "imgspec" not in hdf5_infile:
                raise ValueError()
            if "imgdata" not in hdf5_infile:
                raise ValueError()

            # Load configuration (Todo: Validate that mode matches current)
            self.imgmode = hdf5_infile.attrs["mode"]

            # Load specs
            formatter = self._get_hdf5_input_spec_formatter(
                hdf5_infile["imgspec"].dtype.names)
            char_image_specs = pd.DataFrame(
                data=list(map(formatter,
                              np.array(hdf5_infile["imgspec"]))),
                index=range(hdf5_infile["imgspec"].size),
                columns=hdf5_infile["imgspec"].dtype.names)

            # Load data
            char_image_data = np.array(hdf5_infile["imgdata"])

        self.add_img(char_image_specs, char_image_data)
        """
        raise NotImplementedError()

    def read_image_dir(self):
        """
        import numpy as np
        from PIL import Image
        from scinoephile.ocr import convert_8bit_grayscale_to_2bit

        # TODO: Validate that directory can be load

        if self.verbosity >= 1:
            print(f"Reading images from '{self.input_image_dir}'")

        # Prepare list of infiles
        infiles = self._list_image_dir_input_files(self.input_image_dir)

        # Prepare specs
        specs = self._get_image_dir_input_specs(infiles)

        # Prepare data
        data = np.zeros((len(infiles), self._imgdata_size), self._imgdata_dtype)
        for i, infile in enumerate(infiles):
            image = Image.open(infile)
            if self.imgmode == "8bit":
                pass
            elif self.imgmode == "2bit":
                image = convert_8bit_grayscale_to_2bit(image)
            elif self.imgmode == "1bit":
                raise NotImplementedError()
            data[i] = self.image_to_data(image)

        self.add_img(specs, data)
        """
        raise NotImplementedError()

    def show(self, indexes=None, cols=None):
        import numpy as np
        from PIL import Image

        # Process arguments
        if indexes is None:
            indexes = range(self.imgdata.shape[0])
        elif isinstance(indexes, int):
            indexes = [indexes]
        indexes = np.array(indexes, np.int)
        if np.any(indexes >= self.imgdata.shape[0]):
            raise ValueError()
        if cols is None:
            cols = indexes.size
            rows = 1
        else:
            rows = int(np.ceil(indexes.size / cols))

        # Draw image
        if self.imgmode == "8 bit":
            img = Image.new("L", (cols * 100, rows * 100), 255)
        elif self.imgmode == "1 bit":
            img = Image.new("1", (cols * 100, rows * 100), 1)
        else:
            raise NotImplementedError()
        for i, index in enumerate(indexes):
            column = (i // cols)
            row = i - (column * cols)
            if self.imgmode == "8 bit":
                char_img = Image.fromarray(
                    self.imgdata[index].reshape((80, 80)))
            elif self.imgmode == "1 bit":
                char_img = Image.fromarray(
                    self.imgdata[index].reshape(
                        (80, 80)).astype(np.uint8) * 255)
            else:
                raise NotImplementedError()
            img.paste(char_img,
                      (100 * row + 10,
                       100 * column + 10,
                       100 * (row + 1) - 10,
                       100 * (column + 1) - 10))
        img.show()

    def write_hdf5(self, outfile=None):
        """
        import h5py
        import numpy as np
        from os.path import expandvars

        if outfile is None:
            outfile = self.output_hdf5
        else:
            outfile = expandvars(outfile)
        # TODO: Validate that hdf5 file can be written

        if self.verbosity >= 1:
            print(f"Writing imgdata to '{outfile}'")
        with h5py.File(outfile) as hdf5_outfile:
            # Remove preexisting data
            if "imgdata" in hdf5_outfile:
                del hdf5_outfile["imgdata"]
            if "imgspec" in hdf5_outfile:
                del hdf5_outfile["imgspec"]

            # Save configuration
            hdf5_outfile.attrs["mode"] = self.imgmode

            # Save specs
            # TODO: Check if 'columns.values' can just be 'columns'
            formatter = self._get_hdf5_output_spec_formatter(
                self.imgspec.columns.values)
            dtypes = self._get_hdf5_spec_dtypes(
                self.imgspec.columns.values)
            hdf5_outfile.create_dataset(
                "imgspec",
                data=np.array(list(map(formatter, self.imgspec.values)),
                              dtype=dtypes),
                dtype=dtypes,
                chunks=True,
                compression="gzip")

            # Save data
            hdf5_outfile.create_dataset(
                "imgdata",
                data=self.imgdata,
                dtype=self._imgdata_dtype,
                chunks=True,
                compression="gzip")
        """
        raise NotImplementedError()

    def write_image_dir(self, outdir=None):
        """
        from os import makedirs
        from os.path import dirname, expandvars, isdir

        if outdir is None:
            outdir = self.output_image_dir
        else:
            outdir = expandvars(outdir)
        # TODO: Validate that directory can be written

        if self.verbosity >= 1:
            print(f"Writing images to '{outdir}'")
        outfile_path_formatter = self._get_image_dir_outfile_formatter(
            self.imgspec, outdir)
        outfiles = map(outfile_path_formatter, self.imgspec.iterrows())
        for outfile, data in zip(outfiles, self.imgdata):
            if self.verbosity >= 2:
                print(f"Writing '{outfile}'")
            if not isdir(dirname(outfile)):
                makedirs(dirname(outfile))
            self.image_array_to_object(data).save(outfile)
        """
        raise NotImplementedError()

    # endregion

    # region Private Methods

    def _get_hdf5_input_spec_formatter(self, columns):
        """Provides spec formatter compatible with both numpy and h5py"""
        raise NotImplementedError()

    def _list_image_dir_input_files(self, path):
        """Provides infiles within path"""
        raise NotImplementedError()

    def _get_image_dir_input_specs(self, infiles):
        """Provides specs of infiles"""
        raise NotImplementedError()

    def _get_hdf5_spec_dtypes(self, columns):
        """Provides spec dtypes compatible with both numpy and h5py"""
        raise NotImplementedError()

    def _get_hdf5_output_spec_formatter(self, columns):
        """Provides spec formatter compatible with both numpy and h5py"""
        raise NotImplementedError()

    def _get_image_dir_outfile_formatter(self, specs, outdir):
        """Provides formatter for image outfile paths"""
        raise NotImplementedError()

    # endregion
