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
from zysyzm.ocr import resize_image, trim_image


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

        self.output_directory = "/Users/kdebiec/Desktop/docs/subtitles/training"

    def __call__(self):
        """Core logic"""
        import numpy as np
        from IPython import embed
        from os import mkdir
        from os.path import expandvars, isdir
        from matplotlib.pyplot import figure
        from matplotlib.font_manager import FontProperties
        from matplotlib.patheffects import Stroke, Normal
        from PIL import Image

        font_names = ["Hei", "LiHei Pro", "STHeiti"]
        # font_names += ["Kai", "BiauKai"]
        # font_names += ["LiSong Pro", "STFangsong"]
        chars = ["的", "一", "是", "不", "了", "在"]
        fig = figure(figsize=(1, 1))

        # Loop over fonts
        for font_name in font_names:
            font_dir = f"{self.output_directory}/{font_name}"
            if not isdir(font_dir):
                mkdir(font_dir)
            font = FontProperties(family=font_name, size=60)

            # Loop over characters
            for char in chars:
                char_outfile = f"{font_dir}/{char}.png"

                # Use matplotlib to fenerate initial image of character
                fig.clear()
                text = fig.text(x=0.5, y=0.475, s=char,
                                ha="center", va="center",
                                fontproperties=font, color=(0.94, 0.94, 0.94))
                text.set_path_effects([Stroke(linewidth=6, foreground="k"),
                                       Normal()])
                fig.savefig(char_outfile, dpi=80, transparent=True)

                # Reload with pillow to trim and adjust color and transparency
                char_img = trim_image(Image.open(char_outfile).convert("L"))
                char_img = resize_image(char_img, (80, 80))
                raw = np.array(char_img)
                raw2 = raw[:, :]
                raw2[raw2 < 80] = 0
                raw2[np.logical_and(raw2 >= 80, raw2 < 160)] = 120
                raw2[np.logical_and(raw2 >= 160, raw2 <= 240)] = 240
                raw2[raw2 > 240] = 255
                char_img = Image.fromarray(raw, mode=char_img.mode)
                char_img.save(char_outfile)

    # endregion

    # region Properties
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
        else:
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
