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
  - Log useful error messages
"""
################################### MODULES ###################################
from zysyzm import Base, CLToolBase


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
class OCRBase(Base):
    """"""

    # region Builtins
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # endregion

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
                f"{self.package_root}/data/ocr/characters.txt", sep="\t",
                names=["char", "frequency", "cumulative frequency"])
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


class OCRDataset(OCRBase):
    """"""

    # region Builtins
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.initialize_from_scratch()

    # endregion

    # region Properties
    @property
    def char_image_specs_available(self):
        """pandas.DataFrame: Available character image specifications"""
        if not hasattr(self, "_char_image_specs_available"):
            from itertools import product
            import pandas as pd

            self._char_image_specs_available = pd.DataFrame(
                list(product(self.font_names, self.font_sizes,
                             self.font_widths, self.font_x_offsets,
                             self.font_y_offsets)),
                columns=["font", "size", "width", "x_offset", "y_offset"])

        return self._char_image_specs_available

    @char_image_specs_available.setter
    def char_image_specs_available(self, value):
        # Todo: Validate
        self._char_image_specs_available = value

    @property
    def char_image_specs(self):
        """pandas.DataFrame: Character image specifications"""
        if not hasattr(self, "_char_image_specs"):
            import pandas as pd

            self._char_image_specs = pd.DataFrame(
                columns=["char", "font", "size", "width", "x_offset",
                         "y_offset"])
        return self._char_image_specs

    @char_image_specs.setter
    def char_image_specs(self, value):
        # Todo: Validate
        self._char_image_specs = value

    @property
    def char_image_data(self):
        """numpy.ndarray(bool): Character image data"""
        return self._char_image_data

    @char_image_data.setter
    def char_image_data(self, value):
        # Todo: Validate
        self._char_image_data = value

    @property
    def figure(self):
        """matplotlib.figure.Figure: Temporary figure used for images"""
        if not hasattr(self, "_figure"):
            from matplotlib.pyplot import figure

            self._figure = figure(figsize=(1.0, 1.0), dpi=80)
        return self._figure

    @property
    def font_names(self):
        """list(str): List of font names"""
        if not hasattr(self, "_font_names"):
            self._font_names = ["Hei"]
        return self._font_names

    @font_names.setter
    def font_names(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [str(v) for v in list(value)]
                except Exception as e:
                    raise ValueError()
        self._font_names = value

    @property
    def font_sizes(self):
        """list(int): List of font sizes"""
        if not hasattr(self, "_font_sizes"):
            self._font_sizes = [60]
        return self._font_sizes

    @font_sizes.setter
    def font_sizes(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [int(v) for v in list(value)]
                except Exception as e:
                    raise ValueError()
        self._font_sizes = value

    @property
    def font_widths(self):
        """list(int): List of font border widths"""
        if not hasattr(self, "_font_widths"):
            self._font_widths = [6]
        return self._font_widths

    @font_widths.setter
    def font_widths(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [int(v) for v in list(value)]
                except Exception as e:
                    raise ValueError()
        self._font_widths = value

    @property
    def font_x_offsets(self):
        """list(int): List of font x offsets"""
        if not hasattr(self, "_font_x_offsets"):
            self._font_x_offsets = [0]
        return self._font_x_offsets

    @font_x_offsets.setter
    def font_x_offsets(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [int(v) for v in list(value)]
                except Exception as e:
                    raise ValueError()
        self._font_x_offsets = value

    @property
    def font_y_offsets(self):
        """list(int): List of font y offsets"""
        if not hasattr(self, "_font_y_offsets"):
            self._font_y_offsets = [0]
        return self._font_y_offsets

    @font_y_offsets.setter
    def font_y_offsets(self, value):
        if value is not None:
            if not isinstance(value, list):
                try:
                    value = [int(v) for v in list(value)]
                except Exception as e:
                    raise ValueError()
        self._font_y_offsets = value

    @property
    def hdf5_infile(self):
        """str: Path to input hdf5 file"""
        if not hasattr(self, "_hdf5_infile"):
            self._hdf5_infile = None
        return self._hdf5_infile

    @hdf5_infile.setter
    def hdf5_infile(self, value):
        from os.path import expandvars, isfile

        if value is not None:
            if not isinstance(value, str):
                raise ValueError()
            else:
                value = expandvars(value)
                if not isfile(value):
                    raise ValueError()
        self._hdf5_infile = value

    @property
    def hdf5_outfile(self):
        """str: Path to output hdf5 file"""
        if not hasattr(self, "_hdf5_outfile"):
            self._hdf5_outfile = None
        return self._hdf5_outfile

    @hdf5_outfile.setter
    def hdf5_outfile(self, value):
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
        self._hdf5_outfile = value

    @property
    def image_data_size(self):
        """int: Size of a single image within arrays"""
        if self.image_mode == "8bit":
            return 6400
        elif self.image_mode == "2bit":
            return 12800

    @property
    def image_data_dtype(self):
        """type: Numpy dtype of image arrays"""
        import numpy as np

        if self.image_mode == "8bit":
            return np.int8
        elif self.image_mode == "2bit":
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
            if value not in ["2bit"]:
                raise ValueError()
        self._font_names = value

    @property
    def n_chars(self):
        """int: Number of characters to generate images of"""
        if not hasattr(self, "_n_chars"):
            self._n_chars = 100
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

    # endregion

    # region Methods
    def generate_char_image(self, char, font="Hei", size=60, width=5,
                            x_offset=0, y_offset=0, format="2bit",
                            tmpfile="/tmp/zysyzm.png"):
        from os import remove
        from matplotlib.font_manager import FontProperties
        from matplotlib.patheffects import Stroke, Normal
        from PIL import Image

        # Draw initial image with matplotlib
        self.figure.clear()
        fp = FontProperties(family=font, size=size)
        text = self.figure.text(x=0.5, y=0.475, s=char,
                                ha="center", va="center",
                                fontproperties=fp,
                                color=(0.67, 0.67, 0.67))
        text.set_path_effects([Stroke(linewidth=width,
                                      foreground=(0.00, 0.00, 0.00)),
                               Normal()])
        self.figure.savefig(tmpfile, dpi=80, transparent=True)

        # Reload with pillow to trim, resize, and adjust color
        img = trim_image(Image.open(tmpfile).convert("L"), 0)
        img = resize_image(img, (80, 80), x_offset, y_offset)
        remove(tmpfile)

        # Convert to configured format
        if self.image_mode == "8bit":
            pass
        elif self.image_mode == "2bit":
            img = convert_8bit_grayscale_to_2bit(img)

        return img

    def generate_char_image_data(self, **kwargs):
        import numpy as np

        img = self.generate_char_image(**kwargs)

        if self.image_mode == "8bit":
            data = np.array(img)
        elif self.image_mode == "2bit":
            raw = np.array(img)
            data = np.append(np.logical_or(raw == 85, raw == 256).flatten(),
                             np.logical_or(raw == 170, raw == 256).flatten())
        else:
            data = None

        return data

    def initialize_from_scratch(self):
        import pandas as pd
        import numpy as np
        from IPython import embed

        # Prepare empty arrays
        self.char_image_specs = pd.DataFrame(
            index=range(self.n_chars),
            columns=self.char_image_specs.columns.values)
        self.char_image_data = np.zeros((self.n_chars, self.image_data_size),
                                        dtype=self.image_data_dtype)

        # Fill in arrays with specs and data
        for i, char in enumerate(self.chars[:self.n_chars]):
            row = self.char_image_specs_available.loc[0].to_dict()
            row["char"] = char
            self.char_image_specs.loc[i] = row
            self.char_image_data[i] = self.generate_char_image_data(**row)

        embed()

    def initialize_from_hdf5(self):
        pass

    def save_to_hdf5(self):
        pass

    # endregion


class OCRCLToolBase(CLToolBase, OCRBase):
    """Base for optical character recognition command line tools"""
    pass
