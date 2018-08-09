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
from zysyzm.ocr import (convert_8bit_grayscale_to_2bit, resize_image,
                        trim_image, OCRCLToolBase)


################################### CLASSES ###################################
class TrainingDataGenerator(OCRCLToolBase):
    """Generates data for OCR model training and validation"""

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

        self.n_chars = 400
        self.trn_output_directory = \
            "/Users/kdebiec/Desktop/docs/subtitles/trn"
        self.val_output_directory = \
            "/Users/kdebiec/Desktop/docs/subtitles/val"
        self.val_portion = 0.1

    def __call__(self):
        """Core logic"""
        from matplotlib.pyplot import figure

        def generate_image(char, font_name, font_size, border_width,
                           x_offset, y_offset):
            import numpy as np
            from matplotlib.font_manager import FontProperties
            from matplotlib.patheffects import Stroke, Normal
            from PIL import Image
            from os.path import isfile

            outfile = f"{char}_{font_size:02d}_{border_width:02d}_" \
                      f"{x_offset:+d}_{y_offset:+d}_" \
                      f"{font_name.replace(' ', '')}.png"
            if (isfile(f"{self.val_output_directory}/{outfile}")
                    or isfile(f"{self.trn_output_directory}/{outfile}")):
                return
            if np.random.rand() < self.val_portion:
                outfile = f"{self.val_output_directory}/{outfile}"
            else:
                outfile = f"{self.trn_output_directory}/{outfile}"

            # Use matplotlib to generate initial image of character
            #   Note that the image is written a file here, rather than
            #   being rendered into an array or similar. This two-step
            #   method yields anti-aliasing between the inner gray of the
            #   character and its black outline, but not between the
            #   black outline and the outer white. I haven't found an
            #   in-memory workflow that achieves this style.
            fig.clear()
            font = FontProperties(family=font_name, size=font_size)
            text = fig.text(x=0.5, y=0.475, s=char, ha="center", va="center",
                            fontproperties=font, color=(0.67, 0.67, 0.67))
            text.set_path_effects([Stroke(linewidth=border_width,
                                          foreground=(0.00, 0.00, 0.00)),
                                   Normal()])
            fig.savefig(outfile, dpi=80, transparent=True)

            # Reload with pillow to trim, resize, and adjust color
            char_img = trim_image(Image.open(outfile).convert("L"), 0)
            char_img = resize_image(char_img, (80, 80), x_offset, y_offset)
            char_img = convert_8bit_grayscale_to_2bit(char_img)
            char_img.save(outfile)

            if self.verbosity >= 2:
                print(f"Wrote '{outfile}'")

        fig = figure(figsize=(1.0, 1.0), dpi=80)

        font_names = ["Hei", "STHeiti"]
        # font_names += ["LiHei Pro"]
        # font_names += ["Kai", "BiauKai"]
        # font_names += ["LiSong Pro", "STFangsong"]
        font_sizes = range(58, 63)
        border_widths = range(3, 8)
        offsets = range(-2, 3)

        # Loop over combinations
        for char in self.chars[145:self.n_chars]:
            if self.verbosity >= 1:
                print(f"Generating data for {char}")
            for font_name in font_names:
                for font_size in font_sizes:
                    for border_width in border_widths:
                        for x_offset in offsets:
                            for y_offset in offsets:
                                generate_image(char, font_name, font_size,
                                               border_width, x_offset,
                                               y_offset)

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


#################################### MAIN #####################################
if __name__ == "__main__":
    TrainingDataGenerator.main()
