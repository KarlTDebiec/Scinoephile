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
from IPython import embed

################################## CONSTANTS ##################################
char_index_df = pd.read_csv(
    f"{package_root}/data/ocr/characters.txt",
    sep="\t", names=["character", "frequency", "cumulative frequency"])

char_index = np.array(char_index_df["character"], np.str)
punctuation = np.array("\n　 ,,？?，,、,..！!。.…﹣-─“”\"《<》>「[」]：:")


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
    x = int(np.floor((80 - trimmed.shape[1]) / 2))
    y = int(np.floor((80 - trimmed.shape[0]) / 2))
    centered = np.ones_like(data) * data.max()
    centered[y + y_offset:y + trimmed.shape[0] + y_offset,
    x + x_offset:x + trimmed.shape[1] + x_offset] = trimmed

    return centered


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


def generate_char_data(char, font="/System/Library/Fonts/STHeiti Light.ttc",
                       fig=None, size=60, width=5, x_offset=0, y_offset=0,
                       mode="1 bit"):
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

    # TODO: Handle default font better; perhaps get matplotlib's default

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
    try:
        fig.canvas.draw()
    except ValueError as e:
        print(f"{char} {font} {size} {width} {x_offset} {y_offset}")
        raise e

    # Convert to appropriate mode using pillow
    img = Image.fromarray(np.array(fig.canvas.renderer._renderer))
    if mode == "8 bit":
        data = np.array(img.convert("L"), np.uint8)
    elif mode == "1 bit":
        data = np.array(img.convert("1", dither=0), np.bool)
    else:
        raise NotImplementedError()

    try:
        data = center_char_img(data, x_offset, y_offset)
    except ValueError as e:
        print(f"{char} {font} {size} {width} {x_offset} {y_offset}")
        raise e

    return data


def get_labels_of_chars(chars):
    """
    Gets unique integer indexes of provided char strings

    Args:
        chars (ndarray(int64)): Chars

    Returns:
         ndarray(int64): Labels
    """

    # Process arguments
    if isinstance(chars, str):
        if len(chars) == 1:
            return np.argwhere(chars == chars)[0, 0]
        elif len(chars) > 1:
            chars = np.array(list(chars))
    elif isinstance(chars, list):
        chars = np.array(chars)

    # Return labels
    if isinstance(chars, np.ndarray):
        sorter = np.argsort(chars)
        return np.array(
            sorter[np.searchsorted(chars, chars, sorter=sorter)])
    else:
        raise ValueError()


def get_chars_of_labels(labels):
    """
    Gets char strings of unique integer indexes

    Args:
        labels (ndarray(int64)): Labels

    Returns
        ndarray(U64): Chars
    """

    # Process arguments
    if isinstance(labels, int):
        return char_index[labels]
    elif isinstance(labels, list):
        labels = np.array(labels)

    # return char_index
    if isinstance(labels, np.ndarray):
        return np.array([char_index[i] for i in labels], np.str)
    else:
        raise ValueError()


################################### MODULES ###################################
from scinoephile.ocr.ImageSubtitleEvent import ImageSubtitleEvent
from scinoephile.ocr.ImageSubtitleSeries import ImageSubtitleSeries
# from scinoephile.ocr.Model import Model
from scinoephile.ocr.OCRDataset import OCRDataset
# from scinoephile.ocr.TestOCRDataset import TestOCRDataset
from scinoephile.ocr.TrainOCRDataset import TrainOCRDataset
# from scinoephile.ocr.AutoTrainer import AutoTrainer
