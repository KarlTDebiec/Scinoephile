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
    Represents a collection of character images

    TODO:
      - [ ] Implement 8-bit and 1-bit support; remove 2-bit support
      - [ ] Clean up and refactor
      - [ ] Document
    """

    # region Instance Variables

    help_message = ("Represents a collection of character images")

    # endregion

    # region Builtins

    def __init__(self, infile=None, outfile=None, image_mode=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if infile is not None:
            self.infile = infile
        if outfile is not None:
            self.outfile = outfile
        if image_mode is not None:
            self.image_mode = image_mode

    def __call__(self):
        """ Core logic """
        raise NotImplementedError()

    # endregion

    # region Public Properties

    @property
    def imagespecs(self):
        """pandas.DataFrame: Character image specifications"""
        if not hasattr(self, "_imagespecs"):
            import pandas as pd

            self._imagespecs = pd.DataFrame({
                c: pd.Series([], dtype=self._imagespec_dtypes[c])
                for c in self._imagespec_columns})
        return self._imagespecs

    @imagespecs.setter
    def imagespecs(self, value):
        # Todo: Validate
        self._imagespecs = value
        if hasattr(self, "_specs_set_"):
            delattr(self, "_specs_set_")

    @property
    def imagedata(self):
        """numpy.ndarray(bool): Character image data"""
        if not hasattr(self, "_imagedata"):
            import numpy as np

            self._imagedata = np.zeros((0, self._imagedata_size), self._imagedata_dtype)
        return self._imagedata

    @imagedata.setter
    def imagedata(self, value):
        import numpy as np

        if not isinstance(value, np.ndarray):
            raise ValueError(self._generate_setter_exception(value))
        if value.shape[1] != self._imagedata_size:
            raise ValueError(self._generate_setter_exception(value))
        if value.dtype != self._imagedata_dtype:
            raise ValueError(self._generate_setter_exception(value))
        self._imagedata = value

    @property
    def image_mode(self):
        """str: Image mode"""
        if not hasattr(self, "_image_mode"):
            self._image_mode = "1 bit"
        return self._image_mode

    @image_mode.setter
    def image_mode(self, value):
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

        self._image_mode = value

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
    def _imagespec_columns(self):
        """list(str): Character image specification columns"""
        raise NotImplementedError()

    @property
    def _imagespec_dtypes(self):
        """list(str): Character image specification dtypes"""
        raise NotImplementedError()

    @property
    def _imagespecs_set(self):
        """set: Unique character image specs"""
        if not hasattr(self, "_imagespecs_set_"):
            self._imagespecs_set_ = set(map(tuple, self.imagespecs.values))
        return self._imagespecs_set_

    @property
    def _imagedata_size(self):
        """int: Size of a single image within arrays"""
        if self.image_mode == "8bit":
            return 6400
        elif self.image_mode == "1bit":
            return 6400

    @property
    def _imagedata_dtype(self):
        """type: dtype of image arrays"""
        import numpy as np

        if self.image_mode == "8bit":
            return np.int8
        elif self.image_mode == "1bit":
            return np.bool

    # endregion

    # region Public Methods

    def add_images(self, imagespecs, imagedata):
        """
        Adds image imagedata and specifications

        TODO: Improve efficiency; is it necessary to check that specs are new?

        Args:
            imagespecs (pandas.DataFrame): New specifications
            imagedata (numpy.ndarray): New imagedata
        """
        import numpy as np

        new = imagespecs.apply(
            lambda x: tuple(x.values) not in self._imagespecs_set,
            axis=1).values
        if new.sum() >= 1:
            self.imagespecs = self.imagespecs.append(imagespecs.loc[new],
                                                     ignore_index=True, sort=False)
            self.imagedata = np.append(self.imagedata, imagedata[new], axis=0)

    def read_hdf5(self):
        import pandas as pd
        import h5py
        import numpy as np

        if self.verbosity >= 1:
            print(f"Reading imagedata from '{self.input_hdf5}'")
        with h5py.File(self.input_hdf5) as hdf5_infile:
            if "imagespecs" not in hdf5_infile:
                raise ValueError()
            if "imagedata" not in hdf5_infile:
                raise ValueError()

            # Load configuration (Todo: Validate that mode matches current)
            self.image_mode = hdf5_infile.attrs["mode"]

            # Load specs
            formatter = self._get_hdf5_input_spec_formatter(
                hdf5_infile["imagespecs"].dtype.names)
            char_image_specs = pd.DataFrame(
                data=list(map(formatter,
                              np.array(hdf5_infile["imagespecs"]))),
                index=range(hdf5_infile["imagespecs"].size),
                columns=hdf5_infile["imagespecs"].dtype.names)

            # Load data
            char_image_data = np.array(hdf5_infile["imagedata"])

        self.add_images(char_image_specs, char_image_data)

    def read_image_dir(self):
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
        data = np.zeros((len(infiles), self._imagedata_size), self._imagedata_dtype)
        for i, infile in enumerate(infiles):
            image = Image.open(infile)
            if self.image_mode == "8bit":
                pass
            elif self.image_mode == "2bit":
                image = convert_8bit_grayscale_to_2bit(image)
            elif self.image_mode == "1bit":
                raise NotImplementedError()
            data[i] = self.image_to_data(image)

        self.add_images(specs, data)

    def show_chars(self, indexes, columns=None):
        import numpy as np
        from PIL import Image

        # Process arguments
        if isinstance(indexes, int):
            indexes = [indexes]
        indexes = np.array(indexes, np.int)
        if np.any(indexes >= self.imagedata.shape[0]):
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
            char_image = self.image_array_to_object(self.imagedata[index])
            image.paste(char_image,
                        (100 * row + 10,
                         100 * column + 10,
                         100 * (row + 1) - 10,
                         100 * (column + 1) - 10))
        image.show()

    def write_hdf5(self, outfile=None):
        """
        Writes dataset to an hdf5 file

        Args:
            outfile (str, optional): Path to hdf5 file; defaults to
              self.output_hdf5
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
            print(f"Writing imagedata to '{outfile}'")
        with h5py.File(outfile) as hdf5_outfile:
            # Remove preexisting data
            if "imagedata" in hdf5_outfile:
                del hdf5_outfile["imagedata"]
            if "imagespecs" in hdf5_outfile:
                del hdf5_outfile["imagespecs"]

            # Save configuration
            hdf5_outfile.attrs["mode"] = self.image_mode

            # Save specs
            # TODO: Check if 'columns.values' can just be 'columns'
            formatter = self._get_hdf5_output_spec_formatter(
                self.imagespecs.columns.values)
            dtypes = self._get_hdf5_spec_dtypes(
                self.imagespecs.columns.values)
            hdf5_outfile.create_dataset(
                "imagespecs",
                data=np.array(list(map(formatter, self.imagespecs.values)),
                              dtype=dtypes),
                dtype=dtypes,
                chunks=True,
                compression="gzip")

            # Save data
            hdf5_outfile.create_dataset(
                "imagedata",
                data=self.imagedata,
                dtype=self._imagedata_dtype,
                chunks=True,
                compression="gzip")

    def write_image_dir(self, outdir=None):
        """

        Args:
            outdir (str): Path to output directory; defaults to
              self.output_image_dir
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
            self.imagespecs, outdir)
        outfiles = map(outfile_path_formatter, self.imagespecs.iterrows())
        for outfile, data in zip(outfiles, self.imagedata):
            if self.verbosity >= 2:
                print(f"Writing '{outfile}'")
            if not isdir(dirname(outfile)):
                makedirs(dirname(outfile))
            self.image_array_to_object(data).save(outfile)

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
