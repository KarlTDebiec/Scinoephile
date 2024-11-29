#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to upscaling images."""
from __future__ import annotations

from logging import info

import numpy as np
from PIL import Image, ImageOps
from reportlab.graphics.renderPM import drawToFile
from svglib.svglib import svg2rlg

from scinoephile.common.file import get_temp_file_path
from scinoephile.common.general import run_command


def get_upscaled_image(image: Image) -> Image:
    """Upscale image.

    Arguments:
        image: Image to upscale
    Returns:
        Upscaled image
    """
    # Get output size
    if image.size[0] > image.size[1]:
        output_size = (2000, int(2000 * image.size[1] / image.size[0]))
    else:
        output_size = (int(2000 * image.size[0] / image.size[1]), 2000)

    # Split color and alpha
    array = np.array(image)
    color_array = np.squeeze(array[:, :, :-1])
    alpha_array = array[:, :, -1]
    color_image = Image.fromarray(color_array)
    alpha_image = Image.fromarray(alpha_array)

    # Process alpha
    alpha_image = alpha_image.convert("L")
    alpha_image = alpha_image.point(lambda p: p > 128 and 255)
    alpha_image = _get_potrace_upscaled_image(alpha_image)

    # Process color
    color_image = color_image.convert("L")
    color_image = color_image.point(lambda p: p > 128 and 255)
    color_image = _get_potrace_upscaled_image(color_image)

    # Combine color and alpha
    color_array = np.array(color_image.convert("RGB"))
    alpha_array = np.array(alpha_image.convert("L"))
    output_array = np.zeros((*color_array.shape[:-1], 4), np.uint8)
    output_array[:, :, :-1] = color_array
    output_array[:, :, -1] = alpha_array
    output_image = Image.fromarray(output_array)

    # Resize and return
    output_image = output_image.resize(output_size, Image.LANCZOS)
    output_image = output_image.convert("RGBA")
    info(f"Upscaled image from {image.size} to {output_image.size}")
    return output_image


def _get_potrace_upscaled_image(image: Image):
    image = image.convert("L")
    image = ImageOps.invert(image)
    with get_temp_file_path(".bmp") as temp_bmp_path:
        image.save(temp_bmp_path)

        with get_temp_file_path(".svg") as temp_svg_path:
            command = (
                f"potrace {temp_bmp_path} "
                f"-b svg -k 0.5 -a 1.0 -O 0.2 "
                f"-o {temp_svg_path}"
            )
            run_command(command)
            traced_drawing = svg2rlg(temp_svg_path)
            if not traced_drawing:
                raise ValueError("No drawing found in SVG")
            traced_drawing.scale(
                (image.size[0] / traced_drawing.width) * 2,
                (image.size[1] / traced_drawing.height) * 2,
            )
            traced_drawing.width = int(image.size[0] * 2)
            traced_drawing.height = int(image.size[1] * 2)

            with get_temp_file_path(".png") as temp_png_path:
                drawToFile(traced_drawing, temp_png_path, fmt="png")
                output_image = Image.open(temp_png_path).convert("L")

    output_image = ImageOps.invert(output_image)
    return output_image
