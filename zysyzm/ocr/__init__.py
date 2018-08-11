#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.ocr.__init__.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""
Todo:
  - Decide whether or not to move load_labeled_data and load_unlabeled_data
    to separate functions
  - Move caching from .npy format to hdf5, with information about generation
    stored alongside the data
  - Try relocating temporary image file from /tmp/ to io.Bytes
  - Choose and implement inheritance pattern
  - Implement central executable that reaches out to other classes
  - Once data is moved into hdf5, consider CLTool for browse images
  - Implement support for treating images as float, 8-bit grayscale,
    2-bit grayscale, or 1-bit black and white
"""
################################### MODULES ###################################
from zysyzm import CLToolBase


################################## FUNCTIONS ##################################
def adjust_2bit_grayscale_palette(image):
    """
    Sets palette of a four-color grayscale image to [0, 85, 170, 255]

    Args:
        image(PIL.Image.Image): 4-color grayscale source image

    Returns (PIL.Image.Image): image with [0, 85, 170, 255] palette

    """
    import numpy as np
    from PIL import Image

    raw = np.array(image)
    input_shades = np.where(np.bincount(raw.flatten()) != 0)[0]
    output_shades = [0, 85, 170, 255]

    for input_shade, output_shade in zip(input_shades, output_shades):
        raw[raw == input_shade] = output_shade

    image = Image.fromarray(raw, mode=image.mode)
    return image


def convert_8bit_grayscale_to_2bit(image):
    """
    Sets palette of a four-color grayscale image to [0, 85, 170, 255]

    Args:
        image(PIL.Image.Image): 4-color grayscale source image

    Returns (PIL.Image.Image): image with [0, 85, 170, 255] palette

    """
    import numpy as np
    from PIL import Image

    raw = np.array(image)
    raw[raw < 42] = 0
    raw[np.logical_and(raw >= 42, raw < 127)] = 85
    raw[np.logical_and(raw >= 127, raw <= 212)] = 170
    raw[raw > 212] = 255

    image = Image.fromarray(raw, mode=image.mode)
    return image


def draw_text_on_image(image, text, x=0, y=0, font="Arial.ttf", size=30):
    """
    Draws text on an image

    Args:
        image (PIL.Image.Image): image on which to draw text
        text (str): text to draw
        x (int, optional): x position at which to center text
        y (int, optional): x position at which to center text
        font (str, optional): font with which to draw text
        size (int, optional): font size with which to draw text

    """
    from PIL import ImageDraw, ImageFont

    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font, size)
    width, height = draw.textsize(text, font=font)
    draw.text((x - width / 2, y - height / 2), text, font=font)


def generate_char_image(char, fig=None, font_name="Hei", font_size=60,
                        border_width=5, x_offset=0, y_offset=0,
                        tmpfile="/tmp/zysyzm.png"):
    """
    Generates an image of a character

    Note that the image is written a file here, rather than being rendered
    into an array or similar. This two-step method yields anti-aliasing
    between the inner gray of the character and its black outline, but not
    between the black outline and the outer white. I haven't found an
    in-memory workflow that achieves this style.

    Args:
        char (str): character to generate an image of
        fig (matplotlib.figure.Figure, optional): figure on  which to draw
          character
        font_name (str, optional): font with which to draw character
        font_size (int, optional): font size with which to draw character
        border_width (int, optional: border width with which to draw character
        x_offset (int, optional): x offset to apply to character
        y_offset (int, optional: y offset to apply to character
        tmpfile (str, option): path at which to write temporary image from
          matplotlib

    Returns (PIL.Image.Image): Image of character

    """
    from os import remove
    from matplotlib.font_manager import FontProperties
    from matplotlib.patheffects import Stroke, Normal
    from PIL import Image

    # Use matplotlib to generate initial image of character
    if fig is None:
        from matplotlib.pyplot import figure

        fig = figure(figsize=(1.0, 1.0), dpi=80)
    else:
        fig.clear()

    # Draw image with matplotlib
    font = FontProperties(family=font_name, size=font_size)
    text = fig.text(x=0.5, y=0.475, s=char, ha="center", va="center",
                    fontproperties=font, color=(0.67, 0.67, 0.67))
    text.set_path_effects([Stroke(linewidth=border_width,
                                  foreground=(0.00, 0.00, 0.00)),
                           Normal()])
    fig.savefig(tmpfile, dpi=80, transparent=True)

    # Reload with pillow to trim, resize, and adjust color
    img = trim_image(Image.open(tmpfile).convert("L"), 0)
    img = resize_image(img, (80, 80), x_offset, y_offset)
    img = convert_8bit_grayscale_to_2bit(img)
    remove(tmpfile)

    return img


def trim_image(image, background_color=None):
    """
    Trims whitespace around an image

    Args:
        image (PIL.Image.Image): source image

    Returns (PIL.Image.Image): trimmed image

    """
    from PIL import Image, ImageChops

    if background_color is None:
        background_color = image.getpixel((0, 0))

    background = Image.new(image.mode, image.size, background_color)
    diff = ImageChops.difference(image, background)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()

    if bbox:
        return image.crop(bbox)


def resize_image(image, new_size, x_offset=0, y_offset=0):
    """
    Resizes an image, keeping current contents centered

    Args:
        image (PIL.Image.Image): source image
        new_size (tuple(int, int)): New width and height

    Returns (PIL.Image.Image): resized image

    """
    import numpy as np
    from PIL import Image

    x = int(np.floor((new_size[0] - image.size[0]) / 2))
    y = int(np.floor((new_size[1] - image.size[1]) / 2))
    new_image = Image.new(image.mode, new_size, image.getpixel((0, 0)))
    new_image.paste(image, (x + x_offset,
                            y + y_offset,
                            x + image.size[0] + x_offset,
                            y + image.size[1] + y_offset))

    return new_image


################################### CLASSES ###################################
class OCRCLToolBase(CLToolBase):
    """Base for optical character recognition command line tools"""

    # region Properties
    @property
    def chars(self):
        """pandas.core.frame.DataFrame: Characters"""
        if not hasattr(self, "_chars"):
            import numpy as np

            self._chars = np.array(self.char_frequency_table["character"],
                                   np.str)
        return self._chars

    @property
    def char_frequency_table(self):
        """pandas.core.frame.DataFrame: Character frequency table"""
        if not hasattr(self, "_char_frequency_table"):
            import pandas as pd

            self._char_frequency_table = pd.read_csv(
                f"{self.directory}/data/ocr/characters.txt", sep="\t",
                names=["character", "frequency", "cumulative frequency"])
        return self._char_frequency_table

    # endregion

    # region Methods
    def chars_to_labels(self, chars):
        """
        Converts collection of characters to character labels

        Args:
            chars (np.ndarray(U64), str): characters

        Returns (np.ndarray(int64): labels of provided characters
        """
        import numpy as np

        if isinstance(chars, np.ndarray):
            sorter = np.argsort(self.chars)
            return np.array(
                sorter[np.searchsorted(self.chars, chars, sorter=sorter)])
        elif isinstance(chars, str):
            return np.argwhere(self.chars == chars[0])[0, 0]
        else:
            raise ValueError()

    def labels_to_chars(self, labels):
        """
        Converts collection of character labels to characters themselves

        Args:
            labels (np.ndarray(int64): labels

        Returns (np.ndarray(U64): characters of provided labels
        """
        import numpy as np

        if isinstance(labels, np.ndarray):
            return np.array([self.chars[i] for i in labels], np.str)
        elif isinstance(labels, int):
            return self.chars[labels]
        else:
            raise ValueError()

    # endregion
