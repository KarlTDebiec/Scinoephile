#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to image drawing."""
from __future__ import annotations

from logging import info
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageChops
from matplotlib.font_manager import FontProperties
from matplotlib.patheffects import Normal, Stroke

from scinoephile.common.validation import validate_output_directory
from scinoephile.image import ImageSeries


def validate_ocr(series: ImageSeries, output_path: Path) -> None:
    """Validates the OCR of an image series.

    Arguments:
        series: Series to validate
        output_path: Directory in which to save validation results
    """
    output_path = validate_output_directory(output_path)

    for i, event in enumerate(series.events, 1):
        event.image_diff_stack.save(output_path / f"{i:04d}.png")
        info(f"Saved {output_path / f'{i:04d}.png'}")


def get_grayscale_image_on_white(image: Image.Image) -> Image.Image:
    """Get grayscale image on white background.

    Arguments:
        image: Image
    Returns:
        Grayscale image on white background
    """
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
    """Get image of text, drawn using matplotlib.

    Arguments:
        text: Text to draw
        size: Size of image
    Returns:
        Image of text
    """
    # Prepare Figure of appropriate height and width
    figure = plt.figure(figsize=(size[0] / 100, size[1] / 100), dpi=100)
    figure.patch.set_alpha(0)
    figure.patch.set_facecolor("none")

    # Draw text on Figure
    # TODO: Make styling configurable.
    # TODO: Support OSes other than Windows.
    # TODO: Determine optimized settings for Chinese.
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

    # Convert Figure to Image
    image = Image.new("RGBA", size, color=255)
    image_array = np.array(figure.canvas.renderer._renderer)  # noqa
    image.paste(Image.fromarray(image_array), (0, 0))

    return image


def get_non_white_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    """Get bounding box of non-white/transparent pixels in an image.

    Arguments:
        image: Image
    Returns:
        Bounding box of non-white/transparent pixels
    """
    image_l = image
    if image.mode != "L":
        image_l = get_grayscale_image_on_white(image)
    mask = ImageChops.invert(image_l).point(lambda p: p > 0 and 255)
    bbox = mask.getbbox()

    return bbox


def get_stacked_image(*images: Image.Image) -> Image.Image:
    """Get images stacked vertically.

    Arguments:
        *images: Images
    Returns:
        Image of text
    """
    if not images:
        raise ValueError("No images provided")
    size = images[0].size

    stack = Image.new("RGB", (size[0], size[1] * len(images)))
    for i, image in enumerate(images):
        if image.size != size:
            raise ValueError("Images must be the same size")
        stack.paste(image, (0, size[1] * i))

    return stack


def get_scaled_image(reference: Image.Image, test: Image.Image) -> Image.Image:
    """Get image with non-white/transparent contents scaled to dimensions of reference.

    Arguments:
        reference: Reference image
        test: Test image
    Returns:
        Scaled image
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
