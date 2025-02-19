#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to image drawing."""
from __future__ import annotations

import colorsys
from logging import warning

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

from scinoephile.core.text import is_chinese


def get_aligned_image_of_text(text: str, reference: Image.Image) -> Image.Image:
    """Generate an image of text, aligning each character to the reference image.

    Arguments:
        text: The OCR-generated text
        reference: The reference image of the original text
    Returns:
        Aligned image of text
    """
    ref_boxes = get_character_bounding_boxes(reference)

    filtered_text = "".join([char for char in text if char not in ("\u3000",)])
    if len(ref_boxes) != len(filtered_text):
        get_image_with_bounding_boxes(reference, ref_boxes).show()
        warning(
            f"Number of characters in text ({len(filtered_text)})"
            f" does not match number of boxes ({len(ref_boxes)})"
        )
        return Image.new("L", reference.size, 0)

    # Create a blank canvas for the final image
    img = Image.new("L", reference.size, 255)
    draw = ImageDraw.Draw(img)

    # Load a font
    font_path = r"C:\WINDOWS\FONTS\MSYH.TTC"
    font_size = 40 * 2
    font = ImageFont.truetype(font_path, font_size)
    outline_width = 3
    outline_fill = 31
    fill = 235

    for ref_box, char in zip(ref_boxes, filtered_text):
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
                        fill=outline_fill,
                        anchor="mm",
                    )
        char_draw.text((80, 80), char, font=font, fill=fill, anchor="mm")
        # char_img.show()

        # Downscale character to fit final bounding box
        crop_bbox = get_non_white_bbox(char_img)
        # Extend crop bbox by one pixel
        try:
            crop_bbox = (
                max(0, crop_bbox[0] - 1),
                max(0, crop_bbox[1] - 1),
                min(char_size[0], crop_bbox[2] + 1),
                min(char_size[1], crop_bbox[3] + 1),
            )
            char_resized = char_img.crop(crop_bbox).resize(ref_size, Image.LANCZOS)
        except TypeError:
            get_image_with_bounding_boxes(reference, ref_boxes).show()
            warning("Crop bbox is None")
            return Image.new("L", reference.size, 0)

        # Paste into the final image at the correct position
        img.paste(char_resized, (ref_x1, ref_y1))

    return img


def get_character_bounding_boxes(img: Image.Image):
    """Detect character bounding boxes by splitting at vertical white gaps."""
    if img.mode != "L":
        raise ValueError("Image must be in grayscale mode")
    arr = np.array(img)

    # Cound number of non-white pixels in each column
    non_white_counts = np.sum(arr < 255, axis=0)

    # Get list of sections separated by white gaps
    sections = []
    section = None
    for i, count in enumerate(non_white_counts):
        if count > 0:
            if section is None:
                section = [i, i]
            else:
                section[1] = i
        elif section is not None:
            sections.append(section)
            section = None
    if section is not None:
        sections.append(section)

    # Get bounding boxes for each section
    boxes = []
    for x1, x2 in sections:
        section = arr[:, x1:x2]
        # trim white off top and bottom
        non_white_counts = np.sum(section < 255, axis=1)
        y1 = int(np.argmax(non_white_counts > 0))
        y2 = int(len(non_white_counts) - np.argmax(non_white_counts[::-1] > 0))
        boxes.append((x1, y1, x2, y2))

    # Merge narrow adjacent boxes to fix split characters like 八
    boxes = merge_narrow_adjacent_boxes(boxes)
    boxes = merge_ellipses(boxes)

    return boxes


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

    blur_radius = 2
    reference_l = reference_l.filter(ImageFilter.GaussianBlur(blur_radius))
    test_l = test_l.filter(ImageFilter.GaussianBlur(blur_radius))

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
    # Create a new image with white background
    image = Image.new("L", (size[0] * 2, size[1] * 2), 255)
    draw = ImageDraw.Draw(image)

    # Load a font
    font_path = r"C:\WINDOWS\FONTS\MSYH.TTC"
    font_size = 40 * 2
    font = ImageFont.truetype(font_path, font_size)

    if is_chinese(text):
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

            # Draw character outline
            outline_width = 3
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), char, font=font, fill=31)

            # Draw character fill
            draw.text((x, y), char, font=font, fill=235)

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

        # Draw text with outline
        outline_width = 2 * 2
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((text_x + dx, text_y + dy), text, font=font, fill=31)
        draw.text((text_x, text_y), text, font=font, fill=235)

    image = image.resize(size, Image.LANCZOS)  # noqa
    return image


def get_image_with_bounding_boxes(
    img: Image.Image, boxes: list[tuple[int, int, int, int]]
) -> Image.Image:
    """Draw bounding boxes on an image with rainbow colors for debugging.

    Arguments:
        img: The reference image.
        boxes: List of bounding boxes [(x1, y1, x2, y2)].

    Returns:
        Image with bounding boxes drawn.
    """
    # copy image and make RGB
    img_with_boxes = img.copy().convert("RGB")
    draw = ImageDraw.Draw(img_with_boxes)

    # Generate colors from the rainbow spectrum using correct HSV to RGB conversion
    num_boxes = len(boxes)
    colors = [
        tuple(
            int(c * 255) for c in np.array(colorsys.hsv_to_rgb(i / num_boxes, 1.0, 1.0))
        )
        for i in range(num_boxes)
    ]

    # Draw each bounding box with a different color
    for i, (x1, y1, x2, y2) in enumerate(boxes):
        draw.rectangle([x1, y1, x2 - 1, y2 - 1], outline=colors[i], width=1)

    return img_with_boxes


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

    reference_bbox = get_non_white_bbox(reference)
    test_bbox = get_non_white_bbox(test)
    reference_bbox_size = (
        reference_bbox[2] - reference_bbox[0],
        reference_bbox[3] - reference_bbox[1],
    )
    test_bbox_size = (test_bbox[2] - test_bbox[0], test_bbox[3] - test_bbox[1])
    test_cropped = test.crop(test_bbox)
    test_scaled = test_cropped.resize(reference_bbox_size, Image.LANCZOS)  # noqa
    # test_updated = Image.new("LA", reference.size, (255, 255))
    # test_updated.paste(test_scaled, (reference_bbox[0], reference_bbox[1]), test_scaled)
    # test_l = test_updated.convert("L")

    return test_scaled


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


def merge_ellipses(boxes, max_size=30, max_spacing=10):
    """Merge three small adjacent bounding boxes into a single ellipse bounding box.

    Arguments:
        boxes: List of bounding boxes [(x1, y1, x2, y2)].
        max_size: Maximum width and height for a box to be considered part of an ellipse.
        max_spacing: Maximum allowed gap between dots in an ellipse.

    Returns:
        List of cleaned bounding boxes.
    """
    if not boxes:
        return []
    if len(boxes) == 5:
        print("DING")

    merged_boxes = []
    i = 0

    while i < len(boxes):
        if i <= len(boxes) - 3:  # Check if we have at least 3 remaining boxes
            x1, y1, x2, y2 = boxes[i]
            x3, y3, x4, y4 = boxes[i + 1]
            x5, y5, x6, y6 = boxes[i + 2]

            w1, h1 = x2 - x1, y2 - y1
            w2, h2 = x4 - x3, y4 - y3
            w3, h3 = x6 - x5, y6 - y5

            # Check if all three are small squares and close together
            if (
                max(w1, h1) <= max_size
                and max(w2, h2) <= max_size
                and max(w3, h3) <= max_size
                and abs(x3 - x2) <= max_spacing
                and abs(x5 - x4) <= max_spacing
            ):
                # Merge into a single bounding box
                merged_x1 = x1
                merged_y1 = min(y1, y3, y5)
                merged_x2 = x6
                merged_y2 = max(y2, y4, y6)

                merged_boxes.append((merged_x1, merged_y1, merged_x2, merged_y2))
                i += 3  # Skip the next two since they were merged
                continue

        # If not part of an ellipse, keep as is
        merged_boxes.append(boxes[i])
        i += 1

    return merged_boxes


def merge_narrow_adjacent_boxes(boxes, aspect_ratio_cutoff=1.45, distance_cutoff=6):
    if not boxes:
        return []

    merged_boxes = []
    i = 0

    while i < len(boxes) - 1:
        x1, y1, x2, y2 = boxes[i]
        next_x1, next_y1, next_x2, next_y2 = boxes[i + 1]

        width = x2 - x1
        height = y2 - y1
        aspect_ratio = height / max(width, 1)  # Avoid division by zero

        next_width = next_x2 - next_x1
        next_height = next_y2 - next_y1
        next_aspect_ratio = next_height / max(next_width, 1)

        # Check if both boxes are too narrow and close together horizontally
        if (
            aspect_ratio >= aspect_ratio_cutoff
            and next_aspect_ratio >= aspect_ratio_cutoff
            and abs(next_x1 - x2) <= distance_cutoff
        ):

            # Merge the two bounding boxes
            merged_x1 = x1
            merged_y1 = min(y1, next_y1)
            merged_x2 = next_x2
            merged_y2 = max(y2, next_y2)

            merged_boxes.append((merged_x1, merged_y1, merged_x2, merged_y2))
            i += 2  # Skip the next box since it was merged
        else:
            merged_boxes.append((x1, y1, x2, y2))
            i += 1

    # Add the last box if it wasn't merged
    if i == len(boxes) - 1:
        merged_boxes.append(boxes[i])

    return merged_boxes
