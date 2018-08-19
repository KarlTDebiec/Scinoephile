#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.ocr.OCRDataset,py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from zysyzm.ocr import OCRCLToolBase
from IPython import embed


################################### CLASSES ###################################
class OCRDataset(OCRCLToolBase):
    """
    Represents a collection of character images

    8bit grayscale to 2bit grayscale:
        0 -> 00
        85 -> 01
        170 -> 10
        256 -> 11

    Todo:
      - [ ] Document
      - [ ] Implement other image data types (8 bit and 1 bit)
    """

    # region Instance Variables

    help_message = ("Represents a collection of character images")

    # endregion

    # region Builtins

    def __init__(self, input_hdf5=None, input_image_directory=None,
                 output_hdf5=None, output_image_directory=None,
                 image_mode=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if input_hdf5 is not None:
            self.input_hdf5 = input_hdf5
        if input_image_directory is not None:
            self.input_image_directory = input_image_directory
        if output_hdf5 is not None:
            self.output_hdf5 = output_hdf5
        if output_image_directory is not None:
            self.output_image_directory = output_image_directory
        if image_mode is not None:
            self.image_mode = image_mode

    def __call__(self):
        """ Core logic """
        pass

    # endregion

    # region Properties

    @property
    def char_image_spec_columns(self):
        """list(str): Character image specification columns"""
        raise NotImplementedError()

    @property
    def char_image_specs(self):
        """pandas.DataFrame: Character image specifications"""
        if not hasattr(self, "_char_image_specs"):
            import pandas as pd

            self._char_image_specs = pd.DataFrame(
                columns=self.char_image_spec_columns)
        return self._char_image_specs

    @char_image_specs.setter
    def char_image_specs(self, value):
        # Todo: Validate
        self._char_image_specs = value
        if hasattr(self, "_char_image_specs_set"):
            delattr(self, "_char_image_specs_set")

    @property
    def char_image_specs_set(self):
        if not hasattr(self, "_char_image_specs_set"):
            self._char_image_specs_set = set(
                list(map(tuple, self.char_image_specs.values)))
        return self._char_image_specs_set

    @property
    def char_image_data(self):
        """numpy.ndarray(bool): Character image data"""
        if not hasattr(self, "_char_image_data"):
            import numpy as np

            self._char_image_data = np.zeros((0, self.image_data_size),
                                             self.image_data_dtype)
        return self._char_image_data

    @char_image_data.setter
    def char_image_data(self, value):
        import numpy as np

        if not isinstance(value, np.ndarray):
            raise ValueError()
        if value.shape[1] != self.image_data_size:
            raise ValueError()
        if value.dtype != self.image_data_dtype:
            raise ValueError()
        self._char_image_data = value

    @property
    def image_data_size(self):
        """int: Size of a single image within arrays"""
        if self.image_mode == "8bit":
            return 6400
        elif self.image_mode == "2bit":
            return 12800
        elif self.image_mode == "1bit":
            return 6400

    @property
    def image_data_dtype(self):
        """type: Numpy dtype of image arrays"""
        import numpy as np

        if self.image_mode == "8bit":
            return np.int8
        elif self.image_mode == "2bit":
            return np.bool
        elif self.image_mode == "1bit":
            return np.bool

    @property
    def image_mode(self):
        """str: Image mode"""
        if not hasattr(self, "_image_mode"):
            self._image_mode = "2bit"
        return self._image_mode

    @image_mode.setter
    def image_mode(self, value):
        if value is not None:
            if not isinstance(value, str):
                try:
                    value = str(value)
                except Exception as e:
                    raise ValueError()
            if value == "8bit":
                raise NotImplementedError()
            elif value == "1bit":
                raise NotImplementedError()
            elif value not in ["2bit"]:
                raise ValueError()

        self._image_mode = value

    @property
    def input_hdf5(self):
        """str: Path to input hdf5 file"""
        if not hasattr(self, "_input_hdf5"):
            self._input_hdf5 = None
        return self._input_hdf5

    @input_hdf5.setter
    def input_hdf5(self, value):
        from os.path import expandvars, isfile

        if value is not None:
            if not isinstance(value, str):
                raise ValueError()
            else:
                value = expandvars(value)
                if not isfile(value):
                    raise ValueError()
        self._input_hdf5 = value

    @property
    def input_image_directory(self):
        """str: Path to directory for output training character images"""
        if not hasattr(self, "_input_image_directory"):
            self._input_image_directory = None
        return self._input_image_directory

    @input_image_directory.setter
    def input_image_directory(self, value):
        from os import access, makedirs, R_OK, W_OK
        from os.path import expandvars, isdir

        if not isinstance(value, str) and value is not None:
            raise ValueError()
        elif isinstance(value, str):
            value = expandvars(value)
            if not isdir(value):
                try:
                    makedirs(value)
                except Exception as e:
                    raise ValueError()
            if not access(value, W_OK):
                raise ValueError()
        self._input_image_directory = value

    @property
    def output_hdf5(self):
        """str: Path to output hdf5 file"""
        if not hasattr(self, "_output_hdf5"):
            self._output_hdf5 = None
        return self._output_hdf5

    @output_hdf5.setter
    def output_hdf5(self, value):
        from os import access, R_OK, W_OK
        from os.path import dirname, expandvars, isfile

        if value is not None:
            if not isinstance(value, str):
                raise ValueError()
            else:
                value = expandvars(value)
                if isfile(value) and not access(value, R_OK):
                    raise ValueError()
                elif not access(dirname(value), W_OK):
                    raise ValueError()
        self._output_hdf5 = value

    @property
    def output_image_directory(self):
        """str: Path to directory for output character images"""
        if not hasattr(self, "_output_image_directory"):
            self._output_image_directory = None
        return self._output_image_directory

    @output_image_directory.setter
    def output_image_directory(self, value):
        from os import makedirs
        from os.path import expandvars, isdir

        if not isinstance(value, str) and value is not None:
            raise ValueError()
        elif isinstance(value, str):
            value = expandvars(value)
            if not isdir(value):
                try:
                    makedirs(value)
                except Exception as e:
                    raise ValueError()
        self._output_image_directory = value

    # endregion

    # region Methods

    def add_char_images(self, char_image_specs, char_image_data):
        import numpy as np

        new = char_image_specs.apply(
            lambda x: tuple(x.values) not in self.char_image_specs_set,
            axis=1).values

        self.char_image_specs = self.char_image_specs.append(
            char_image_specs.loc[new], ignore_index=True)
        self.char_image_data = np.append(
            self.char_image_data, char_image_data[new], axis=0)

    def data_to_image(self, data):
        import numpy as np
        from PIL import Image

        if self.image_mode == "8bit":
            raise NotImplementedError()
        elif self.image_mode == "2bit":
            raw = np.zeros((self.image_data_size // 2), np.uint8)
            raw[np.logical_and(data[0::2] == False, data[1::2] == True)] = 85
            raw[np.logical_and(data[0::2] == True, data[1::2] == False)] = 170
            raw[np.logical_and(data[0::2] == True, data[1::2] == True)] = 255
            raw = raw.reshape((int(np.sqrt(raw.size)), int(np.sqrt(raw.size))))
            image = Image.fromarray(raw, mode="L")
        elif self.image_mode == "1bit":
            raise NotImplementedError()

        return image

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

    def read_hdf5(self):
        import pandas as pd
        import h5py
        import numpy as np

        if self.verbosity >= 1:
            print(f"Reading data from '{self.input_hdf5}'")
        with h5py.File(self.input_hdf5) as hdf5_infile:
            if "char_image_specs" not in hdf5_infile:
                raise ValueError()
            if "char_image_data" not in hdf5_infile:
                raise ValueError()

            # Load configuration (Todo: Validate that mode matches current)
            self.image_mode = hdf5_infile.attrs["mode"]

            # Load specs
            formatter = self._read_hdf5_spec_formatter(
                hdf5_infile["char_image_specs"].dtype.names)
            char_image_specs = pd.DataFrame(
                data=list(map(formatter,
                              np.array(hdf5_infile["char_image_specs"]))),
                index=range(hdf5_infile["char_image_specs"].size),
                columns=hdf5_infile["char_image_specs"].dtype.names)

            # Load data
            char_image_data = np.array(hdf5_infile["char_image_data"])

        self.add_char_images(char_image_specs, char_image_data)

    def read_image_directory(self):
        import numpy as np
        from PIL import Image
        from zysyzm.ocr import convert_8bit_grayscale_to_2bit

        if self.verbosity >= 1:
            print(f"Reading images from '{self.input_image_directory}'")
        infiles = self._read_image_directory_infiles(
            self.input_image_directory)
        char_image_specs = self._read_image_directory_specs(infiles)
        char_image_data = np.zeros(
            (len(infiles), self.image_data_size), self.image_data_dtype)
        for i, infile in enumerate(infiles):
            image = Image.open(infile)
            if self.image_mode == "8bit":
                pass
            elif self.image_mode == "2bit":
                image = convert_8bit_grayscale_to_2bit(image)
            elif self.image_mode == "1bit":
                raise NotImplementedError()
            char_image_data[i] = self.image_to_data(image)

        self.add_char_images(char_image_specs, char_image_data)

    def show_char_images(self, indexes, columns=None):
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

    def write_hdf5(self):
        import h5py
        import numpy as np

        if self.verbosity >= 1:
            print(f"Writing data to '{self.output_hdf5}'")
        with h5py.File(self.output_hdf5) as hdf5_outfile:
            # Remove preexisting data
            if "char_image_data" in hdf5_outfile:
                del hdf5_outfile["char_image_data"]
            if "char_image_specs" in hdf5_outfile:
                del hdf5_outfile["char_image_specs"]

            # Save configuration
            hdf5_outfile.attrs["mode"] = self.image_mode

            # Save specs
            formatter = self._write_hdf5_spec_formatter(
                self.char_image_specs.columns.values)
            dtypes = self._write_hdf5_spec_dtypes(
                self.char_image_specs.columns.values)
            hdf5_outfile.create_dataset(
                "char_image_specs",
                data=np.array(list(map(formatter,
                                       self.char_image_specs.values)),
                              dtype=dtypes),
                dtype=dtypes,
                chunks=True,
                compression="gzip")

            # Save data
            hdf5_outfile.create_dataset(
                "char_image_data",
                data=self.char_image_data,
                dtype=self.image_data_dtype,
                chunks=True,
                compression="gzip")

    # endregion

    # Private Methods

    def _read_hdf5_spec_formatter(self, columns):
        """Formats spec for compatibility with both numpy and h5py"""
        raise NotImplementedError()

    def _read_image_directory_infiles(self, path):
        """Provides infiles within path"""
        raise NotImplementedError()

    def _read_image_directory_specs(self, infiles):
        """Provides specs of infiles"""
        raise NotImplementedError()

    def _write_hdf5_spec_dtypes(self, columns):
        """Provides spec dtypes compatible with both numpy and h5py"""
        raise NotImplementedError()

    def _write_hdf5_spec_formatter(self, columns):
        """Provides spec formatter compatible with both numpy and h5py"""
        raise NotImplementedError()

    # endregion
