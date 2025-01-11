#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to image drawing."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
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
    figure = plt.figure(figsize=(size[0] / 100, size[0] / 100), dpi=100)

    # Draw image using matplotlib
    font = r"C:\WINDOWS\FONTS\MSYHL.TTC"
    size = 60
    width = 2
    text = figure.text(
        x=0.5,
        y=0.475,
        s=text,
        ha="center",
        va="center",
        fontproperties=FontProperties(fname=font, size=size),
        color=(0.67, 0.67, 0.67),
    )
    text.set_path_effects(
        [Stroke(linewidth=width, foreground=(0.0, 0.0, 0.0)), Normal()]
    )
    figure.canvas.draw()

    # Convert to appropriate mode using pillow
    image_array = np.array(figure.canvas.renderer._renderer)
    image = Image.fromarray(image_array).convert("L")
    return image
