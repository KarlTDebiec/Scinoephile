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
from zysyzm import CLToolBase
from zysyzm.ocr import convert_8bit_grayscale_to_2bit, resize_image, trim_image


################################### CLASSES ###################################
class TrainingDataGenerator(CLToolBase):
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

        self.output_directory = "/Users/kdebiec/Desktop/docs/subtitles/trn"

    def __call__(self):
        """Core logic"""
        from matplotlib.pyplot import figure

        def generate_image(char, font_name, font_size, border_width):
            from matplotlib.font_manager import FontProperties
            from matplotlib.patheffects import Stroke, Normal
            from PIL import Image

            outfile = f"{self.output_directory}/{char}_{font_size:02d}_" \
                      f"{border_width:02d}_{font_name.replace(' ', '')}.png"

            # Use matplotlib to generate initial image of character
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
            char_img = resize_image(char_img, (80, 80))
            char_img = convert_8bit_grayscale_to_2bit(char_img)
            char_img.save(outfile)

            if self.verbosity >= 2:
                print(f"Wrote '{outfile}'")


        fig = figure(figsize=(1, 1))

        chars = ["的", "一", "是", "不", "了", "在"]
        font_names = ["Hei", "LiHei Pro", "STHeiti"]
        font_names += ["Kai", "BiauKai"]
        font_names += ["LiSong Pro", "STFangsong"]
        font_sizes = [58, 59, 60, 61, 62]
        border_widths = [3, 4, 5, 6, 7]

        # Loop over combinations
        for char in chars:
            for font_name in font_names:
                for font_size in font_sizes:
                    for border_width in border_widths:
                        generate_image(char, font_name, font_size,
                                       border_width)

    # endregion

    # region Properties
    @property
    def n_images(self):
        """int: Number of character images to generate"""
        if not hasattr(self, "_n_images"):
            self._n_images = 1000
        return self._n_images

    @n_images.setter
    def n_images(self, value):
        if not isinstance(value, int) and value is not None:
            try:
                value = int(value)
            except Exception as e:
                raise ValueError()
        if value < 1 and value is not None:
            raise ValueError()
        self._n_images = value

    @property
    def output_directory(self):
        """str: Path to directory for output character images"""
        if not hasattr(self, "_output_directory"):
            self._output_directory = None
        return self._output_directory

    @output_directory.setter
    def output_directory(self, value):
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
        self._output_directory = value

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    TrainingDataGenerator.main()
