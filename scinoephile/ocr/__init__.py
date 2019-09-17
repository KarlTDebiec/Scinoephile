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
from IPython import embed
from scinoephile import package_root

################################## VARIABLES ##################################
data_root = f"{package_root}/data/ocr/"
unicode_blocks = pd.read_csv(f"{data_root}/Blocks-12.1.0.txt",
                             sep=";", comment="#", skip_blank_lines=True,
                             names=["range", "name"],
                             converters={"name": lambda n: n.strip()})
unicode_blocks["start"] = unicode_blocks["range"].apply(
    lambda x: int(x.split(".")[0], 16))
unicode_blocks["end"] = unicode_blocks["range"].apply(
    lambda x: int(x.split(".")[-1], 16))
unicode_blocks = unicode_blocks.drop(columns="range")
hanzi_frequency = pd.read_csv(
    f"{data_root}/characters.txt",
    sep="\t", names=["character", "frequency", "cumulative frequency"])
hanzi_chars = np.array(hanzi_frequency["character"], np.str)
western_chars = np.array(list(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"))
numeric_chars = np.array(list("0123456789"))
eastern_punctuation_chars = np.array(list(
    "．。？！，、﹣（）［］《》「」：；＂⋯"))
# ＜＞
western_punctuation_chars = np.array(list(
    ".?!,-()[]<>:;“”\"…"))


################################## FUNCTIONS ##################################
def analyze_character_accuracy(img, lbl, model, title="", verbosity=1):
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
    from difflib import SequenceMatcher
    from colorama import Fore, Style

    event_pairs = zip(
        [e.text.replace("　", "").replace(" ", "") for e in subtitles.events],
        [e.text.replace("　", "").replace(" ", "") for e in standard.events])
    counts = pd.DataFrame(np.zeros((6, 3), np.int),
                          columns=["correct", "incorrect", "unmatchable"],
                          index=["char segmentation", "hanzi chars",
                                 "western chars", "numeric chars",
                                 "punctuation chars", "all chars"])
    misassigned_chars = dict()
    unmatchable_chars = dict()

    # Loop over subtitles
    for i, (pred_text, true_text) in enumerate(event_pairs):
        # Segmentation accuracy
        if len(pred_text) == len(true_text):
            counts.at["char segmentation", "correct"] += 1
            line = f"{i:4d} | "
        else:
            counts.at["char segmentation", "incorrect"] += 1
            line = f"{Fore.RED}{i:4d}{Style.RESET_ALL} | "

        # Recognition accuracy
        opcodes = SequenceMatcher(a=pred_text, b=true_text).get_opcodes()
        for kind, pred_start, pred_end, true_start, true_end in opcodes:
            if kind == "equal":
                line += f"{Fore.GREEN}" \
                        f"{pred_text[pred_start:pred_end]}" \
                        f"{Style.RESET_ALL}"
                for char in pred_text[pred_start:pred_end]:
                    if char in hanzi_chars:
                        counts.at["hanzi chars", "correct"] += 1
                    elif char in western_chars:
                        counts.at["western chars", "correct"] += 1
                    elif char in numeric_chars:
                        counts.at["numeric chars", "correct"] += 1
                    elif (char in eastern_punctuation_chars
                          or char in western_punctuation_chars):
                        counts.at["punctuation chars", "correct"] += 1
            elif kind == "replace":
                line += f"{Fore.RED}" \
                        f"{pred_text[pred_start:pred_end]}" \
                        f"{Style.RESET_ALL}"
                for char in pred_text[pred_start:pred_end]:
                    block = get_unicode_block(char)
                    if block not in misassigned_chars:
                        misassigned_chars[block] = set()
                    misassigned_chars[block].add(char)
                for char in true_text[true_start:true_end]:
                    block = get_unicode_block(char)
                    if char in hanzi_chars:
                        counts.at["hanzi chars", "incorrect"] += 1
                        if block not in misassigned_chars:
                            misassigned_chars[block] = set()
                        misassigned_chars[block].add(char)
                    elif char in western_chars:
                        counts.at["western chars", "incorrect"] += 1
                        if block not in misassigned_chars:
                            misassigned_chars[block] = set()
                        misassigned_chars[block].add(char)
                    elif char in numeric_chars:
                        counts.at["numeric chars", "incorrect"] += 1
                        if block not in misassigned_chars:
                            misassigned_chars[block] = set()
                        misassigned_chars[block].add(char)
                    elif (char in eastern_punctuation_chars
                          or char in western_punctuation_chars):
                        counts.at["punctuation chars", "incorrect"] += 1
                        if block not in misassigned_chars:
                            misassigned_chars[block] = set()
                        misassigned_chars[block].add(char)
                    else:
                        counts.at["hanzi chars", "unmatchable"] += 1
                        if block not in unmatchable_chars:
                            unmatchable_chars[block] = set()
                        unmatchable_chars[block].add(char)
            elif kind == "delete":
                line += f"{Fore.RED}" \
                        f"{pred_text[pred_start:pred_end]}" \
                        f"{Style.RESET_ALL}"
                for char in pred_text[pred_start:pred_end]:
                    block = get_unicode_block(char)
                    misassigned_chars.get(block, set()).add(char)
            else:
                embed()
        if verbosity >= 3 or (verbosity == 2 and pred_text != true_text):
            print(line)
            print(f"     | {true_text}")

    for column in ["correct", "incorrect", "unmatchable"]:
        counts.at["all chars", column] = (
                counts.at["hanzi chars", column] +
                counts.at["western chars", column] +
                counts.at["numeric chars", column] +
                counts.at["punctuation chars", column])
    counts["matchable"] = counts["correct"] + counts["incorrect"]
    counts["total"] = counts["matchable"] + counts["unmatchable"]
    counts["accuracy"] = counts["correct"] / counts["total"]
    counts["matchable accuracy"] = counts["correct"] / counts["matchable"]
    counts.at["char segmentation", "matchable"] = 0
    counts.at["char segmentation", "matchable accuracy"] = 0

    if verbosity >= 1:
        print(counts)
        length = max([len(b) for b in misassigned_chars.keys()]
                     + [len(b) for b in unmatchable_chars.keys()])
        if len(misassigned_chars) > 0:
            print("Characters misassigned by model:")
            for block in sorted(misassigned_chars.keys()):
                char = "".join(sorted(list(misassigned_chars[block])))
                print(f"    {block:{length}} | {char}")
        if len(unmatchable_chars) > 0:
            print("Characters not matchable by model:")
            for block in sorted(unmatchable_chars.keys()):
                char = "".join(sorted(list(unmatchable_chars[block])))
                print(f"    {block:{length}} | {char}")

    return counts, unmatchable_chars


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


def get_reconstructed_text(chars, widths, separations,
                           punctuation="fullwidth"):
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


def get_unicode_block(char):
    # TODO: Document
    code = ord(char)
    for name, start, end in unicode_blocks.values:
        if start <= code <= end:
            return name
    return None


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
