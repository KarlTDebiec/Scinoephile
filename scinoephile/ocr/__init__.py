#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.__init__.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import numpy as np
import pandas as pd
from scinoephile import package_root

################################## VARIABLES ##################################
hanzi_frequency = pd.read_csv(
    f"{package_root}/data/ocr/characters.txt",
    sep="\t", names=["character", "frequency", "cumulative frequency"])

hanzi_chars = np.array(hanzi_frequency["character"], np.str)
western_chars = np.array(list(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"))
numeric_chars = np.array(list("0123456789"))
'⋯'
eastern_punctuation_chars = np.array(list("。？！，、（）［］《》「」：；"))
'–'
western_punctuation_chars = np.array(list(".?!,-()[]<>:;…"))


################################## FUNCTIONS ##################################
def center_char_img(data, x_offset=0, y_offset=0):
    """
    Centers image data

    Args:
        data (numpy.ndarray): Character image data
        x_offset (int): Offset to apply along x axis
        y_offset (int): Offset to apply along y axis

    Returns:
        numpy.ndarray: Centered character image
    """
    # TODO: Make general-purpose

    white_cols = (data == data.max()).all(axis=0)
    white_rows = (data == data.max()).all(axis=1)
    trimmed = data[
              np.argmin(white_rows):white_rows.size - np.argmin(
                  white_rows[::-1]),
              np.argmin(white_cols):white_cols.size - np.argmin(
                  white_cols[::-1])]
    x = int(np.floor((80 - trimmed.shape[1]) / 2)) + x_offset
    y = int(np.floor((80 - trimmed.shape[0]) / 2)) + y_offset
    centered = np.ones_like(data) * data.max()
    centered[y:y + trimmed.shape[0], x:x + trimmed.shape[1]] = trimmed

    return centered


def draw_char_imgs(data, cols=20, **kwargs):
    """
    Draws character images from provided data

    Args:
        data (ndarray): Character data to draw
        cols (int, optional): Number of columns of characters
        kwargs: Additional keyword arguments

    Returns:
        PIL.Image.Image: Images of characters
    """
    from PIL import Image

    # Process arguments
    if data.dtype == np.uint8:
        pass
    elif data.dtype in [np.float16, np.float32, np.float64]:
        data = np.array(data * 255.0, np.uint8)
    if cols is None:
        cols = data.shape[0]
        rows = 1
    else:
        rows = int(np.ceil(data.shape[0] / cols))
    cols = min(cols, data.shape[0])

    # Draw image
    img = Image.new("L", (cols * 100, rows * 100), 255)
    for i, char in enumerate(data):
        column = (i // cols)
        row = i - (column * cols)
        img.paste(Image.fromarray(char), (100 * row + 10,
                                          100 * column + 10,
                                          100 * (row + 1) - 10,
                                          100 * (column + 1) - 10))

    return img


def draw_text_on_img(image, text, x=0, y=0,
                     font="/System/Library/Fonts/STHeiti Light.ttc", size=30):
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

    # TODO: Handle default font better

    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font, size)
    width, height = draw.textsize(text, font=font)
    draw.text((x - width / 2, y - height / 2), text, font=font)


def generate_char_datum(char, font="/System/Library/Fonts/STHeiti Light.ttc",
                        size=60, width=5, x_offset=0, y_offset=0, fig=None):
    """
    Generates an image of a character

    Args:
        char (str): character of which to draw an image of
        font (str): font with which to draw character
        fig (matplotlib.figure.Figure, optional): figure on which to draw
          character
        size (int, optional): font size with which to draw character
        width (int, optional: border width with which to draw character
        x_offset (int, optional): x offset to apply to character
        y_offset (int, optional: y offset to apply to character

    Returns:
        numpy.ndarray: Character image data
    """
    from matplotlib.font_manager import FontProperties
    from matplotlib.patheffects import Stroke, Normal
    from PIL import Image

    # TODO: Don't hardcode defaults for macOS

    # Process arguments
    if fig is None:
        from matplotlib.pyplot import figure

        fig = figure(figsize=(1.0, 1.0), dpi=80)
    else:
        fig.clear()

    # Draw image using matplotlib
    text = fig.text(x=0.5, y=0.475, s=char, ha="center", va="center",
                    fontproperties=FontProperties(fname=font, size=size),
                    color=(0.67, 0.67, 0.67))
    text.set_path_effects([Stroke(linewidth=width, foreground=(0.0, 0.0, 0.0)),
                           Normal()])
    fig.canvas.draw()

    # Convert to appropriate mode using pillow
    img = Image.fromarray(np.array(fig.canvas.renderer._renderer))
    data = np.array(img.convert("L"), np.uint8)

    # Center
    data = center_char_img(data, x_offset, y_offset)

    return data


def show_img(img, **kwargs):
    """
    Shows an image using context-appropriate function

    If called from within Jupyter notebook, shows inline. If imgcat module
    is available, shows inline in terminal. Otherwise opens a new window.

    Args:
        img (PIL.Image.Image): Image to show
        kwargs: Additional keyword arguments

    """
    from scinoephile import in_ipython

    # Show image
    if in_ipython() == "ZMQInteractiveShell":
        from io import BytesIO
        from IPython.display import display, Image

        bytes_ = BytesIO()
        img.save(bytes_, "png")
        display(Image(data=bytes_.getvalue()))
    elif in_ipython() == "InteractiveShellEmbed":
        img.show()
    else:
        try:
            from imgcat import imgcat

            imgcat(img)
        except ImportError:
            img.show()


################################### CLASSES ###################################
from scinoephile.ocr.ImageSubtitleEvent import ImageSubtitleEvent
from scinoephile.ocr.ImageSubtitleSeries import ImageSubtitleSeries
from scinoephile.ocr.OCRDataset import OCRDataset
from scinoephile.ocr.OCRTestDataset import OCRTestDataset
from scinoephile.ocr.OCRTrainDataset import OCRTrainDataset
