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
eastern_punctuation_chars = np.array(list(
    "．。？！，、﹣（）［］《》「」：；＂⋯"))
western_punctuation_chars = np.array(list(
    ".?!,-()[]<>:;“”\"…"))


################################## FUNCTIONS ##################################
def analyze_character_accuracy(self, img, lbl, model, title="", verbosity=1):
    # TODO: Implement
    raise NotImplementedError()
    # pred = model.predict(img)
    # loss, acc = model.evaluate(img, lbl)
    # if verbosity >= 1:
    #     print(f"{title:10s}  Count:{lbl.size:5d}  Loss:{loss:7.5f} "
    #           f"Accuracy:{acc:7.5f}")
    # if verbosity >= 2:
    #     for i, char in enumerate(get_chars_of_labels(lbl)):
    #         poss_lbls = np.argsort(pred[i])[::-1]
    #         poss_chars = get_chars_of_labels(poss_lbls)
    #         poss_probs = np.round(pred[i][poss_lbls], 2)
    #         if char != poss_chars[0]:
    #             if verbosity >= 2:
    #                 matches = [f"{a}:{b:4.2f}" for a, b in
    #                            zip(poss_chars[:10], poss_probs[:10])]
    #                 print(f"{char} | {' '.join(matches)}")
    #
    # return loss, acc


def analyze_text_accuracy(subtitles, standard, chars, verbosity=1):
    # TODO: Document
    from colorama import Fore, Style

    event_pairs = zip([e.text for e in subtitles.events],
                      [e.text for e in standard.events])
    n_events = len(subtitles.events)
    n_events_correct_length = n_events
    n_chars_total = 0
    n_chars_correct = 0
    n_chars_matchable = 0
    matchable_10k = ""
    unmatchable = ""

    # Loop over subtitles
    for i, (pred_text, true_text) in enumerate(event_pairs):

        # Remove whitespace
        pred_text = pred_text.replace("　", "").replace(" ", "")
        true_text = true_text.replace("　", "").replace(" ", "")
        n_chars_total += len(true_text)
        # Loop over characters

        if len(pred_text) != len(true_text):
            n_events_correct_length -= 1
            # TODO: Align and evaluate each character
            if verbosity >= 2:
                print(f"{i:4d} | {Fore.RED}{pred_text}{Style.RESET_ALL}")
        else:
            if verbosity >= 3 or (verbosity == 2 and pred_text != true_text):
                print(f"{i:4d} | ", end="")
            for pred_char, true_char in zip(pred_text, true_text):
                if pred_char == true_char:
                    n_chars_correct += 1
                    if verbosity >= 3 or (
                            verbosity == 2 and pred_text != true_text):
                        print(f"{Fore.GREEN}{pred_char}{Style.RESET_ALL}",
                              end="")
                else:
                    if verbosity >= 3 or (
                            verbosity == 2 and pred_text != true_text):
                        print(f"{Fore.RED}{pred_char}{Style.RESET_ALL}",
                              end="")
                if true_char in chars:
                    n_chars_matchable += 1
                elif true_char in hanzi_chars:
                    matchable_10k += true_char
                else:
                    unmatchable += true_char
            if verbosity >= 3 or (verbosity == 2 and pred_text != true_text):
                print("")

        if verbosity >= 3 or (verbosity == 2 and pred_text != true_text):
            print(f"     | {true_text}")

    if verbosity >= 1:
        print(f"{n_events_correct_length}/{n_events} "
              f"subtitles segmented correctly (accuracy = "
              f"{n_events_correct_length / n_events:6.4})")
        print(f"{n_chars_correct}/{n_chars_total} "
              f"characters recognized correctly (accuracy = "
              f"{n_chars_correct / n_chars_total:6.4})")
        print(f"{n_chars_correct}/{n_chars_matchable} "
              f"matchable characters recognized correctly (accuracy = "
              f"{n_chars_correct / n_chars_matchable:6.4f})")
        print(f"{len(matchable_10k)}/{n_chars_total} "
              f"chars would be matchable using 10,000 most frequent"
              f"({len(set(matchable_10k))} unique)")
        print(sorted(list(set(matchable_10k))))
        print(f"{len(unmatchable)}/{n_chars_total} "
              f"chars would be still be unmatchable "
              f"({len(set(unmatchable))} unique)")
        print(sorted(list(set(unmatchable))))


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

    # TODO: Don't hardcode default font for macOS

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

    # TODO: Don't hardcode default font for macOS

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


def get_reconstructed_text(chars, widths, separations, punctuation="eastern"):
    text = ""
    items = zip(chars[:-1], chars[1:], widths[:-1], widths[1:], separations)
    for char_i, char_j, width_i, width_j, sep in items:
        text += char_i

        # Very large space: Two speakers
        if sep >= 100:
            text = f"﹣{text}　　﹣"
        # Two Hanzi: separation cutoff of 40 to add double-width space
        elif width_i >= 45 and width_j >= 45 and sep >= 40:
            # print("Adding a double-width space")
            text += "　"
        # Two Roman: separation cutoff of 35 to add single-width space
        elif width_i < 45 and width_j < 45 and sep >= 36:
            # print("Adding a single-width space")
            text += " "
    text += chars[-1]

    # TODO: Improve handling of punctuation, including ellipsis
    text = text.replace(".", "。")
    text = text.replace("．", "。")
    text = text.replace("!", "！")
    text = text.replace(":", "：")
    text = text.replace("。。。", "⋯")

    return text


def get_tesseract_text(image, language="chi_sim"):
    from pytesseract import image_to_string

    return image_to_string(image, config=f"--psm 7 --oem 3", lang=language)


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
