#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to image drawing."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageChops
from matplotlib.font_manager import FontProperties
from matplotlib.patheffects import Normal, Stroke


def get_grayscale_image_on_white(image: Image.Image) -> Image.Image:
    """Get grayscale image on white background"""
    image_l = Image.new("LA", image.size, (255, 255))
    image_l.paste(image, (0, 0), image)
    image_l = image_l.convert("L")
    return image_l


def get_image_diff(reference: Image.Image, test: Image.Image) -> Image.Image:
    """Get image diff. Darker or lighter pixels are red and blue, respectively.

    Arguments:
        reference: reference image
        test: test image
    Returns:
        color diff image in which pixels that are dark in the test image are red, and
        pixels that are too light in the test image are blue.
    """
    if reference.size != test.size:
        raise ValueError("Images must be the same size")
    if reference.mode != "L":
        reference_l = get_grayscale_image_on_white(reference)
    else:
        reference_l = reference
    if test.mode != "L":
        test_l = get_grayscale_image_on_white(test)
    else:
        test_l = test

    diff_data = np.array(reference_l).astype(int) - np.array(test_l).astype(int)

    darker_data = diff_data.copy()
    darker_data[darker_data > 0] = 0
    darker_data = (darker_data * -1).astype(np.uint8)

    lighter_data = diff_data.copy()
    lighter_data[lighter_data < 0] = 0
    lighter_data = lighter_data.astype(np.uint8)

    color_diff_data = np.ones((reference.size[1], reference.size[0], 3), np.uint8) * 255
    color_diff_data[..., 1] -= darker_data  # Subtract darker from green and blue
    color_diff_data[..., 2] -= darker_data  # to make darker pixels redder
    color_diff_data[..., 0] -= lighter_data  # Subtract lighter from red and green
    color_diff_data[..., 1] -= lighter_data  # to make lighter pixels bluer
    color_diff = Image.fromarray(color_diff_data)

    return color_diff


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
    font = r"C:\WINDOWS\FONTS\MSYH.TTC"
    font_size = 41.5
    width = 4
    text = figure.text(
        x=0.5,
        y=0.5,
        s=text,
        ha="center",
        va="center",
        fontproperties=FontProperties(
            fname=font,
            size=font_size,
        ),
        color=(0.8549, 0.8549, 0.8549),
    )
    text.set_path_effects(
        [Stroke(linewidth=width, foreground=(0.1, 0.1, 0.1)), Normal()]
    )
    figure.canvas.draw()

    # Make a new image of desired size and paste on it, to ensure correct size
    image = Image.new("RGBA", size, color=255)
    image_array = np.array(figure.canvas.renderer._renderer)  # noqa
    image.paste(Image.fromarray(image_array), (0, 0))

    return image


def get_non_white_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    """Get bounding box of non-white/transparent pixels in the image.

    Arguments:
        image: Image
    Returns:
        Bounding box of non-white/transparent pixels in the image
    """
    # Convert image to grayscale if not already
    if image.mode != "L":
        image = get_grayscale_image_on_white(image)

    # Create a mask of non-white pixels
    non_white_mask = ImageChops.invert(image).point(lambda p: p > 0 and 255)

    # Get the bounding box of the non-white pixels
    bbox = non_white_mask.getbbox()

    return bbox


def get_stretched_image(reference: Image.Image, test: Image.Image) -> Image.Image:
    """Get image with non-white/transparent contents streched to size of reference.

    Arguments:
        reference: Reference image
        test: Test image
    Returns:
        Stretched image
    """
    if reference.size != test.size:
        raise ValueError("Images must be the same size")

    reference_l = get_grayscale_image_on_white(reference)
    test_l = get_grayscale_image_on_white(test)
    reference_bbox = get_non_white_bbox(reference_l)
    test_bbox = get_non_white_bbox(test_l)
    reference_bbox_size = (
        reference_bbox[2] - reference_bbox[0],
        reference_bbox[3] - reference_bbox[1],
    )
    test_bbox_size = (test_bbox[2] - test_bbox[0], test_bbox[3] - test_bbox[1])
    test_cropped = test.crop(test_bbox)
    test_scaled = test_cropped.resize(reference_bbox_size, Image.LANCZOS)  # noqa
    test_updated = Image.new("LA", reference.size, (255, 255))
    test_updated.paste(test_scaled, (reference_bbox[0], reference_bbox[1]), test_scaled)
    test_l = test_updated.convert("L")

    return test_l


def get_stacked_image_diff(
    reference: Image.Image, test: Image.Image, diff: Image.Image | None = None
) -> Image.Image:
    """Get image of text.

    Arguments:
        reference: Reference image
        test: Test image
        diff: Difference between reference and teset
    Returns:
        Image of text
    """
    if reference.size != test.size:
        raise ValueError("Images must be the same size")

    reference_l = get_grayscale_image_on_white(reference)
    test_l = get_stretched_image(reference_l, test)

    diff = get_image_diff(reference_l, test_l)

    stack = Image.new("RGB", (reference.width, reference.height * 3))
    stack.paste(reference_l, (0, 0))
    stack.paste(test_l, (0, reference.height))
    stack.paste(diff, (0, reference.height * 2))

    return stack
