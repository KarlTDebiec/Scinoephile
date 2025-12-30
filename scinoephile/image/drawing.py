#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to drawing."""

from __future__ import annotations

import colorsys
from functools import cache
from pathlib import Path
from platform import system

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from scinoephile.core import ScinoephileError
from scinoephile.core.text import get_text_type

from .bbox import get_bbox

__all__ = [
    "get_img_with_bboxes",
    "get_img_diff",
    "get_img_of_text",
    "get_img_of_text_with_bboxes",
    "get_img_scaled_to_bbox",
    "get_img_with_white_bg",
    "get_imgs_stacked",
]


def get_img_with_bboxes(img: Image.Image, bboxes: list[tuple[int, ...]]) -> Image.Image:
    """Draw bounding boxes on an image with rainbow colors for debugging.

    Arguments:
        img: reference image
        bboxes: bounding boxes [(x1, y1, x2, y2)].
    Returns:
        image with bounding boxes drawn.
    """
    img_with_bboxes = img.convert("RGB")
    draw = ImageDraw.Draw(img_with_bboxes)

    # Generate palette
    palette = [
        tuple(
            int(c * 255)
            for c in np.array(colorsys.hsv_to_rgb(i / len(bboxes), 1.0, 1.0))
        )
        for i in range(len(bboxes))
    ]

    # Draw boxes
    for i, (x1, y1, x2, y2) in enumerate(bboxes):
        draw.rectangle(
            [x1, y1, x2, y2],
            outline=palette[i],
            width=1,
        )

    return img_with_bboxes


def get_img_diff(ref: Image.Image, tst: Image.Image) -> Image.Image:
    """Get diff between two grayscale images.

    Arguments:
        ref: reference image; must be of mode "L"
        tst: test image; must be of mode "L" and the same size as ref
    Returns:
        color diff image in which pixels that are darker in the test image are red, and
        pixels that are lighter in the test image are blue.
    """
    if ref.size != tst.size:
        raise ValueError(
            f"Images must be the same size; ref: {ref.size}, tst: {tst.size}"
        )
    if ref.mode != "L":
        raise ValueError(f"Reference image must be of mode 'L', is {ref.mode}")
    if tst.mode != "L":
        raise ValueError(f"Test image must be of mode 'L', is {tst.mode}")

    blur_radius = 2
    ref = ref.filter(ImageFilter.GaussianBlur(blur_radius))
    tst = tst.filter(ImageFilter.GaussianBlur(blur_radius))

    diff_arr = np.array(ref).astype(int) - np.array(tst).astype(int)

    diff_sq = np.sign(diff_arr) * (diff_arr**2)
    diff_sq = (diff_sq / 65025) * 255
    darker_arr = np.clip(-diff_sq, 0, 255).astype(np.uint8)
    lighter_arr = np.clip(diff_sq, 0, 255).astype(np.uint8)

    color_diff_arr = np.ones((ref.size[1], ref.size[0], 3), np.uint8) * 255
    color_diff_arr[..., 1] -= darker_arr  # Subtract darker from green and blue
    color_diff_arr[..., 2] -= darker_arr  # to make darker pixels redder
    color_diff_arr[..., 0] -= lighter_arr  # Subtract lighter from red and green
    color_diff_arr[..., 1] -= lighter_arr  # to make lighter pixels bluer
    color_diff = Image.fromarray(color_diff_arr)

    return color_diff


def get_img_of_text(
    text: str,
    size: tuple[int, int],
    *,
    font_path: Path | str | None = None,
    font_size: int = 64,
    fill_color: int = 31,
    outline_color: int = 235,
) -> Image.Image:
    """Get image of text, drawn using pillow.

    Arguments:
        text: text to draw
        size: size of image
        font_path: path to font file
        font_size: font size for rendering
        fill_color: fill color of text
        outline_color: outline color of text
    Returns:
        image of text
    """
    # Create a new image with white background
    image = Image.new("L", size, 255)
    draw = ImageDraw.Draw(image)

    # Determine font.
    if font_path is None:
        font_path = _get_default_font_path()
    font = ImageFont.truetype(font_path, font_size)

    if get_text_type(text) == "full":
        spacing: int = 14

        # Calculate initial position for text drawing
        x = (
            image.size[0] - (len(text) * font_size // 2 + (len(text) - 1) * spacing)
        ) // 2
        y = (image.size[1] - font_size) // 2

        # Draw each character with custom spacing
        for char in text:
            text_bbox = draw.textbbox((0, 0), char, font=font)
            char_width = text_bbox[2] - text_bbox[0]

            # Draw character outline and fill
            outline_width = 3
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text(
                            (x + dx, y + dy),
                            char,
                            font=font,
                            fill=outline_color,
                        )
            draw.text(
                (x, y),
                char,
                font=font,
                fill=fill_color,
            )

            # Move to next character position
            x += char_width + spacing
    else:
        # Calculate text size and position
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = (
            text_bbox[2] - text_bbox[0],
            text_bbox[3] - text_bbox[1],
        )
        text_x = (image.size[0] - text_width) // 2
        text_y = (image.size[1] - text_height) // 2
        text_y -= text_bbox[1]

        # Draw text outline and fill
        outline_width = 2
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text(
                        (text_x + dx, text_y + dy),
                        text,
                        font=font,
                        fill=outline_color,
                    )
        draw.text(
            (text_x, text_y),
            text,
            font=font,
            fill=fill_color,
        )

    return image


def get_img_of_text_with_bboxes(
    text: str,
    size: tuple[int, int],
    bboxes: list[tuple[int, int, int, int]],
    *,
    font_path: Path | str | None = None,
    fill_color: int = 31,
    outline_color: int = 235,
) -> Image.Image:
    """Generate an image of text, aligning each character to the reference image.

    Arguments:
        text: OCRed text believed to be present in image
        size: size of image
        bboxes: bounding boxes of characters in reference image
        font_path: path to font file
        fill_color: fill of text
        outline_color: outline of text
    Returns:
        image of text
    """
    # Check if alignment is possible
    filtered_text = "".join([char for char in text if char not in ("\u3000", " ")])
    if len(bboxes) != len(filtered_text):
        raise ScinoephileError(
            f"Number of characters in text ({len(filtered_text)})"
            f" does not match number of boxes ({len(bboxes)})"
        )

    # Create a blank canvas for the final image
    img = Image.new("L", size, 255)

    # Load font
    if font_path is None:
        font_path = _get_default_font_path()
    font_size = 40 * 2
    font = ImageFont.truetype(font_path, font_size)
    outline_width = 3

    for i, ref_box in enumerate(bboxes):
        char = filtered_text[i]
        if char == "⋯":
            char = "…"

        ref_x1, ref_y1, ref_x2, ref_y2 = ref_box
        ref_size = (ref_x2 - ref_x1, ref_y2 - ref_y1)

        # Create a separate 2X canvas to draw the character
        char_size = (160, 160)
        char_img = Image.new("L", char_size, 255)
        char_draw = ImageDraw.Draw(char_img)

        # Draw character outline and fill
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    char_draw.text(
                        (80 + dx, 80 + dy),
                        char,
                        font=font,
                        fill=outline_color,
                        anchor="mm",
                    )
        char_draw.text(
            (80, 80),
            char,
            font=font,
            fill=fill_color,
            anchor="mm",
        )

        # Downscale character to fit final bounding box
        crop_bbox = get_bbox(char_img)
        if crop_bbox is None:
            raise ScinoephileError(f"Could not determine bbox for character '{char}'.")
        # Extend crop bbox by one pixel
        crop_bbox = (
            max(0, crop_bbox[0] - 1),
            max(0, crop_bbox[1] - 1),
            min(char_size[0], crop_bbox[2] + 1),
            min(char_size[1], crop_bbox[3] + 1),
        )
        char_resized = char_img.crop(crop_bbox).resize(
            ref_size, Image.Resampling.LANCZOS
        )

        # Paste into the final image at the correct position
        img.paste(char_resized, (ref_x1, ref_y1))

    return img


def get_img_scaled_to_bbox(ref: Image.Image, tst: Image.Image) -> Image.Image:
    """Get image with non-white/transparent contents scaled to dimensions of reference.

    Arguments:
        ref: reference image
        tst: test image
    Returns:
        scaled image
    """
    if ref.size != tst.size:
        raise ValueError("Images must be the same size")

    ref_bbox = get_bbox(ref)
    tst_bbox = get_bbox(tst)
    if ref_bbox is None or tst_bbox is None:
        raise ScinoephileError("Could not determine bbox for reference or test image.")
    ref_bbox_size = (ref_bbox[2] - ref_bbox[0], ref_bbox[3] - ref_bbox[1])
    tst_cropped = tst.crop(tst_bbox)
    tst_scaled = tst_cropped.resize(ref_bbox_size, Image.Resampling.LANCZOS)
    tst_final = Image.new("L", ref.size, 255)
    tst_final.paste(tst_scaled, (ref_bbox[0], ref_bbox[1]))

    return tst_final


def get_img_with_white_bg(img: Image.Image) -> Image.Image:
    """Get image with transparency on white background.

    Arguments:
        img: image with transparency
    Returns:
        image on white background
    """
    if img.mode == "LA":
        img_la = Image.new("LA", img.size, (255, 255))
        img_la.paste(img, (0, 0), img)
        img_l = img_la.convert("L")
        return img_l
    elif img.mode == "RGBA":
        img_rgba = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img_rgba.paste(img, (0, 0), img)
        img_rgb = img_rgba.convert("RGB")
        return img_rgb
    else:
        raise ScinoephileError(f"Image must be in mode 'LA' or 'RGBA', is {img.mode}")


def get_imgs_stacked(*imgs: Image.Image) -> Image.Image:
    """Get images stacked vertically.

    Arguments:
        *imgs: images to stack
    Returns:
        stack of images
    """
    size = imgs[0].size

    stack = Image.new("RGB", (size[0], size[1] * len(imgs)))
    for i, img in enumerate(imgs):
        if img.size != size:
            raise ValueError("Images must be the same size")
        stack.paste(img, (0, size[1] * i))

    return stack


@cache
def _get_default_font_path() -> Path:
    """Get path to font file.

    Returns:
        path to font file
    """
    if system() == "Windows":
        return Path(r"C:\WINDOWS\FONTS\MSYH.TTC")
    if system() == "Darwin":
        return Path(r"/System/Library/Fonts/STHeiti Medium.ttc")
    raise ScinoephileError("Font path must be provided for non-Windows systems")
