#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.ocr.TrainingDataGenerator.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from zysyzm.ocr import OCRCLToolBase


################################### CLASSES ###################################
class TrainingDataGenerator(OCRCLToolBase):
    """
    Generates data for OCR model training and validation
    Todo:
      - CL arguments
      - Output directly to hdf5
    """

    # region Instance Variables
    help_message = ("Tool for generating training data")

    # endregion

    # region Builtins
    def __init__(self, **kwargs):
        """
        Initializes tool
        Args:
            kwargs (dict): Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.n_chars = 10
        self.trn_output_directory = \
            "/Users/kdebiec/Desktop/docs/subtitles/trn"
        self.val_output_directory = \
            "/Users/kdebiec/Desktop/docs/subtitles/val"
        self.val_portion = 0.1

    def __call__(self):
        """Core logic"""
        from matplotlib.pyplot import figure

        fig = figure(figsize=(1.0, 1.0), dpi=80)

        font_names = ["Hei", "STHeiti"]
        # font_names += ["LiHei Pro"]
        # font_names += ["Kai", "BiauKai"]
        # font_names += ["LiSong Pro", "STFangsong"]
        font_sizes = [58, 59, 60, 61, 62]
        border_widths = [3, 4, 5, 6, 7]
        offsets = [-2, -1, 0, 1, 2]

        # Loop over combinations
        for i, char in enumerate(self.chars[:self.n_chars]):
            if self.verbosity >= 1:
                print(f"{i / self.n_chars * 100:4.2f}% complete, "
                      f"generating data for {char}")
            for font_name in font_names:
                for font_size in font_sizes:
                    for border_width in border_widths:
                        for x_offset in offsets:
                            for y_offset in offsets:
                                self.output_char_image(char, font_name,
                                                       font_size, border_width,
                                                       x_offset, y_offset,
                                                       fig=fig)

    # endregion

    # region Properties
    @property
    def n_chars(self):
        """int: Number of characters to generate images of"""
        if not hasattr(self, "_n_chars"):
            self._n_chars = 21
        return self._n_chars

    @n_chars.setter
    def n_chars(self, value):
        if not isinstance(value, int) and value is not None:
            try:
                value = int(value)
            except Exception as e:
                raise ValueError()
        if value < 1 and value is not None:
            raise ValueError()
        self._n_chars = value

    @property
    def trn_output_directory(self):
        """str: Path to directory for output training character images"""
        if not hasattr(self, "_trn_output_directory"):
            self._trn_output_directory = None
        return self._trn_output_directory

    @trn_output_directory.setter
    def trn_output_directory(self, value):
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
        self._trn_output_directory = value

    @property
    def val_output_directory(self):
        """str: Path to directory for output validation character images"""
        if not hasattr(self, "_val_output_directory"):
            self._val_output_directory = None
        return self._val_output_directory

    @val_output_directory.setter
    def val_output_directory(self, value):
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
        self._val_output_directory = value

    @property
    def val_portion(self):
        """float: Portion of images to set aside for validation"""
        if not hasattr(self, "_val_portion"):
            self._val_portion = 0
        return self._val_portion

    @val_portion.setter
    def val_portion(self, value):
        if value is None:
            value = 0
        elif not isinstance(value, float):
            try:
                value = float(value)
            except Exception as e:
                raise ValueError()
        if not 0 <= value <= 1:
            raise ValueError()
        self._val_portion = value

    # endregion

    # region Methods
    def output_char_image(self, char, font_name="Hei", font_size=60,
                          border_width=5, x_offset=0, y_offset=0, **kwargs):
        """
        Outputs an image of a character, if output image does not exist
        Args:
            char (str): character to generate an image of
            font_name (str, optional): font with which to draw character
            font_size (int, optional): font size with which to draw character
            border_width (int, optional: border width with which to draw
              character
            x_offset (int, optional): x offset to apply to character
            y_offset (int, optional: y offset to apply to character
            **kwargs (dict):
        """
        import numpy as np
        from os.path import isfile
        from zysyzm.ocr import generate_char_image

        # Check if outfile exists, and if not choose output location
        outfile = f"{char}_{font_size:02d}_{border_width:02d}_" \
                  f"{x_offset:+d}_{y_offset:+d}_" \
                  f"{font_name.replace(' ', '')}.png"
        if isfile(f"{self.val_output_directory}/{outfile}"):
            return
        elif isfile(f"{self.trn_output_directory}/{outfile}"):
            return
        elif np.random.rand() < self.val_portion:
            outfile = f"{self.val_output_directory}/{outfile}"
        else:
            outfile = f"{self.trn_output_directory}/{outfile}"

        # Generate image
        img = generate_char_image(char, font=font_name, size=font_size,
                                  width=border_width, x_offset=x_offset,
                                  y_offset=y_offset, **kwargs)
        img.save(outfile)
        if self.verbosity >= 2:
            print(f"Wrote '{outfile}'")
    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    TrainingDataGenerator.main()
