#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to image drawing."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageChops
from matplotlib.font_manager import FontProperties
from matplotlib.patheffects import Normal, Stroke


def get_image_of_text(text: str, size: tuple[int, int]) -> Image.Image:
    """Get image of text.

    Arguments:
        text: Text to encode
        size: Size of image
    Returns:
        Image of text
    """
    # Generate figure of height and width
    figure = plt.figure(figsize=(size[0] / 100, size[1] / 100), dpi=100)
    figure.patch.set_alpha(0)
    figure.patch.set_facecolor("none")

    # Draw image using matplotlib
    # font = r"C:\WINDOWS\FONTS\MSYHL.TTC"
    font = r"C:\WINDOWS\FONTS\MSYH.TTC"
    # font = r"C:\WINDOWS\FONTS\MSYHBD.TTC"
    font_size = 41.5
    width = 3
    text = figure.text(
        x=0.5,
        y=0.5,
        s=text,
        ha="center",
        va="center",
        fontproperties=FontProperties(fname=font, size=font_size),
        color=(0.8549, 0.8549, 0.8549),
    )
    text.set_path_effects(
        [Stroke(linewidth=width, foreground=(0.1, 0.1, 0.1)), Normal()]
    )
    figure.canvas.draw()

    # Make a new image of desired size and paste on it, to ensure correct size
    image = Image.new("RGBA", size, color=255)
    image_array = np.array(figure.canvas.renderer._renderer)
    fuck = Image.fromarray(image_array)
    image.paste(fuck, (0, 0))
    return image


def get_stacked_image_diff(
    top: Image.Image, bottom: Image.Image, diff: Image.Image | None = None
) -> Image.Image:
    """Get image of text.

    Arguments:
        top: Top image
        bottom: Bottom image
        diff: Difference between top and bottom
    Returns:
        Image of text
    """
    if top.size != bottom.size:
        raise ValueError("Images must be the same size")
    if not diff:
        diff = ImageChops.difference(top, bottom)

    stack = Image.new("RGBA", (top.width, top.height * 3))
    stack.paste(top, (0, 0))
    stack.paste(bottom, (0, top.height))
    stack.paste(diff, (0, top.height * 2))

    return stack
