#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to OCR validation."""
from __future__ import annotations

from logging import info, warning
from pathlib import Path

from PIL import Image

from scinoephile.common.validation import validate_output_directory
from scinoephile.core import ScinoephileException
from scinoephile.image.bbox import get_char_bboxes
from scinoephile.image.drawing import (
    get_image_annotated_with_char_bboxes,
    get_image_diff,
    get_image_of_text,
    get_image_of_text_with_char_alignment,
    get_image_scaled,
    get_image_with_white_bg,
    get_images_stacked,
)
from scinoephile.image.image_series import ImageSeries


def validate_ocr_hanzi(series: ImageSeries, output_path: Path) -> None:
    """Validate OCR of a hanzi image series.

    Arguments:
        series: Series to validate
        output_path: Directory in which to save validation results
    """
    output_path = validate_output_directory(output_path)

    for i, event in enumerate(series.events, 1):
        # Prepare source image
        img_with_white_bg = get_image_with_white_bg(event.img)
        bboxes = get_char_bboxes(img_with_white_bg)
        img_with_bboxes = get_image_annotated_with_char_bboxes(
            img_with_white_bg, bboxes
        )

        # Draw image of OCRed text, aligned to source image
        try:
            img_of_text = get_image_of_text_with_char_alignment(
                event.text, event.img.size, bboxes
            )
            validate_spaces_hanzi(event.text, bboxes)
        except ScinoephileException as e:
            warning(f"Subtitle {i} encountered the following exception: {e}")
            img_of_text = get_image_of_text(event.text, event.img.size)
        img_of_text_scaled = get_image_scaled(img_with_white_bg, img_of_text)

        # Draw difference between source and OCRed text images
        img_diff = get_image_diff(img_with_white_bg, img_of_text_scaled)

        # Stack images and rescale for convenience
        img_stack = get_images_stacked(img_with_bboxes, img_of_text_scaled, img_diff)
        img_resized = img_stack.resize(
            (img_stack.width * 10, img_stack.height * 10), Image.NEAREST  # noqa
        )

        # Save image
        img_resized.save(output_path / f"{i:04d}.png")
        info(f"Saved {output_path / f'{i:04d}.png'}")


max_gaps = {
    (11, 34): 16,
    (12, 14): 26,
    (12, 31): 23,
    (12, 33): 16,
    (12, 34): 63,
    (12, 63): 66,
    (12, 65): 64,
    (13, 66): 17,
    (14, 28): 52,
    (14, 49): 55,
    (14, 55): 51,
    (14, 57): 49,
    (14, 60): 49,
    (14, 62): 50,
    (14, 63): 48,
    (14, 64): 48,
    (14, 65): 48,
    (14, 66): 47,
    (14, 67): 46,
    (14, 68): 45,
    (15, 29): 51,
    (15, 55): 51,
    (15, 57): 51,
    (15, 60): 49,
    (15, 62): 48,
    (15, 63): 47,
    (15, 64): 48,
    (15, 65): 47,
    (15, 66): 47,
    (15, 67): 45,
    (15, 68): 45,
    (16, 12): 62,
    (16, 52): 56,
    (16, 54): 58,
    (16, 55): 57,
    (16, 56): 57,
    (16, 57): 56,
    (16, 58): 56,
    (16, 59): 56,
    (16, 60): 55,
    (16, 61): 55,
    (16, 62): 55,
    (16, 63): 55,
    (16, 64): 55,
    (16, 65): 54,
    (16, 66): 53,
    (16, 67): 52,
    (16, 68): 52,
    (16, 69): 50,
    (21, 61): 52,
    (21, 62): 49,
    (21, 64): 49,
    (21, 66): 47,
    (21, 67): 47,
    (22, 64): 48,
    (25, 31): 11,
    (28, 14): 52,
    (28, 60): 43,
    (28, 62): 41,
    (28, 63): 41,
    (28, 64): 41,
    (28, 65): 40,
    (28, 66): 40,
    (28, 67): 39,
    (28, 68): 38,
    (29, 15): 51,
    (29, 58): 41,
    (29, 60): 42,
    (29, 62): 41,
    (29, 63): 40,
    (29, 64): 41,
    (29, 65): 39,
    (29, 66): 39,
    (29, 67): 39,
    (29, 68): 38,
    (31, 16): 41,
    (31, 33): 6,
    (31, 34): 34,
    (31, 55): 42,
    (31, 57): 39,
    (31, 62): 38,
    (31, 63): 37,
    (31, 64): 38,
    (31, 65): 37,
    (31, 66): 37,
    (31, 67): 36,
    (31, 68): 35,
    (32, 11): 18,
    (32, 12): 17,
    (32, 32): 7,
    (32, 33): 5,
    (32, 60): 10,
    (32, 61): 16,
    (32, 63): 17,
    (32, 64): 13,
    (32, 65): 14,
    (32, 66): 14,
    (32, 67): 13,
    (32, 68): 13,
    (33, 25): 10,
    (33, 32): 7,
    (33, 33): 8,
    (33, 35): 6,
    (34, 12): 17,
    (34, 32): 6,
    (34, 33): 6,
    (34, 34): 5,
    (35, 16): 11,
    (35, 32): 6,
    (35, 33): 5,
    (35, 66): 6,
    (36, 32): 5,
    (37, 33): 3,
    (40, 64): 10,
    (45, 28): 22,
    (45, 32): 45,
    (45, 53): 20,
    (45, 54): 22,
    (45, 55): 22,
    (45, 62): 18,
    (45, 63): 19,
    (45, 64): 19,
    (45, 65): 18,
    (45, 66): 17,
    (45, 67): 16,
    (45, 68): 16,
    (47, 62): 16,
    (48, 55): 21,
    (48, 66): 16,
    (48, 67): 16,
    (49, 57): 23,
    (49, 64): 16,
    (49, 65): 16,
    (49, 66): 15,
    (49, 67): 15,
    (50, 58): 22,
    (50, 64): 16,
    (50, 65): 15,
    (50, 66): 15,
    (52, 16): 19,
    (52, 55): 19,
    (52, 61): 20,
    (52, 63): 16,
    (52, 64): 18,
    (52, 65): 15,
    (52, 66): 14,
    (53, 57): 21,
    (53, 62): 19,
    (53, 63): 18,
    (53, 64): 18,
    (53, 65): 18,
    (53, 67): 13,
    (53, 68): 14,
    (54, 45): 25,
    (54, 56): 19,
    (54, 60): 16,
    (54, 62): 14,
    (54, 63): 16,
    (54, 64): 16,
    (54, 65): 14,
    (54, 66): 14,
    (54, 67): 13,
    (54, 68): 12,
    (55, 16): 18,
    (55, 32): 41,
    (55, 55): 18,
    (55, 57): 17,
    (55, 58): 16,
    (55, 59): 17,
    (55, 60): 19,
    (55, 61): 15,
    (55, 62): 16,
    (55, 63): 14,
    (55, 64): 15,
    (55, 65): 15,
    (55, 66): 14,
    (55, 67): 14,
    (55, 68): 12,
    (56, 14): 26,
    (56, 54): 18,
    (56, 56): 17,
    (56, 57): 16,
    (56, 58): 16,
    (56, 60): 15,
    (56, 62): 14,
    (56, 63): 14,
    (56, 64): 15,
    (56, 65): 13,
    (56, 66): 13,
    (56, 67): 13,
    (56, 68): 11,
    (57, 14): 26,
    (57, 16): 19,
    (57, 29): 17,
    (57, 55): 18,
    (57, 56): 16,
    (57, 57): 17,
    (57, 58): 12,
    (57, 59): 16,
    (57, 60): 15,
    (57, 61): 13,
    (57, 62): 16,
    (57, 63): 15,
    (57, 64): 16,
    (57, 65): 15,
    (57, 66): 14,
    (57, 67): 13,
    (57, 68): 13,
    (58, 15): 24,
    (58, 16): 13,
    (58, 54): 17,
    (58, 55): 17,
    (58, 56): 17,
    (58, 57): 15,
    (58, 58): 15,
    (58, 60): 15,
    (58, 61): 11,
    (58, 62): 13,
    (58, 63): 13,
    (58, 64): 13,
    (58, 65): 14,
    (58, 66): 13,
    (58, 67): 12,
    (58, 68): 10,
    (58, 69): 6,
    (59, 14): 25,
    (59, 15): 22,
    (59, 16): 16,
    (59, 54): 15,
    (59, 59): 14,
    (59, 60): 13,
    (59, 61): 13,
    (59, 62): 13,
    (59, 63): 12,
    (59, 64): 13,
    (59, 65): 13,
    (59, 66): 12,
    (59, 67): 11,
    (59, 68): 9,
    (60, 14): 23,
    (60, 15): 25,
    (60, 16): 18,
    (60, 28): 16,
    (60, 50): 21,
    (60, 52): 16,
    (60, 53): 15,
    (60, 55): 17,
    (60, 57): 16,
    (60, 59): 15,
    (60, 60): 16,
    (60, 62): 15,
    (60, 63): 15,
    (60, 64): 14,
    (60, 65): 14,
    (60, 66): 14,
    (60, 67): 13,
    (60, 68): 11,
    (60, 69): 8,
    (61, 14): 22,
    (61, 15): 22,
    (61, 16): 15,
    (61, 29): 15,
    (61, 31): 16,
    (61, 55): 15,
    (61, 56): 17,
    (61, 57): 14,
    (61, 59): 13,
    (61, 60): 14,
    (61, 61): 12,
    (61, 62): 14,
    (61, 63): 14,
    (61, 64): 13,
    (61, 65): 12,
    (61, 66): 13,
    (61, 67): 12,
    (61, 68): 10,
    (62, 14): 22,
    (62, 15): 23,
    (62, 16): 16,
    (62, 28): 15,
    (62, 29): 14,
    (62, 32): 38,
    (62, 45): 21,
    (62, 49): 19,
    (62, 50): 17,
    (62, 52): 14,
    (62, 53): 14,
    (62, 54): 14,
    (62, 55): 15,
    (62, 56): 12,
    (62, 57): 15,
    (62, 58): 13,
    (62, 59): 15,
    (62, 60): 14,
    (62, 61): 14,
    (62, 62): 13,
    (62, 63): 13,
    (62, 64): 14,
    (62, 65): 12,
    (62, 66): 12,
    (62, 67): 11,
    (62, 68): 10,
    (62, 69): 9,
    (63, 14): 23,
    (63, 15): 22,
    (63, 16): 16,
    (63, 21): 12,
    (63, 28): 16,
    (63, 29): 15,
    (63, 31): 27,
    (63, 32): 36,
    (63, 45): 19,
    (63, 48): 19,
    (63, 54): 15,
    (63, 55): 15,
    (63, 56): 15,
    (63, 57): 13,
    (63, 58): 14,
    (63, 59): 13,
    (63, 60): 14,
    (63, 61): 12,
    (63, 62): 12,
    (63, 63): 14,
    (63, 64): 13,
    (63, 65): 12,
    (63, 66): 12,
    (63, 67): 10,
    (63, 68): 9,
    (63, 69): 7,
    (64, 14): 22,
    (64, 15): 22,
    (64, 16): 15,
    (64, 21): 12,
    (64, 22): 12,
    (64, 28): 16,
    (64, 29): 15,
    (64, 32): 38,
    (64, 35): 6,
    (64, 40): 32,
    (64, 45): 20,
    (64, 49): 18,
    (64, 50): 15,
    (64, 52): 16,
    (64, 53): 15,
    (64, 54): 14,
    (64, 55): 15,
    (64, 56): 15,
    (64, 57): 14,
    (64, 58): 12,
    (64, 59): 14,
    (64, 60): 13,
    (64, 61): 13,
    (64, 62): 12,
    (64, 63): 12,
    (64, 64): 12,
    (64, 65): 11,
    (64, 66): 11,
    (64, 67): 10,
    (64, 68): 9,
    (64, 69): 8,
    (64, 70): 8,
    (65, 14): 21,
    (65, 15): 21,
    (65, 16): 14,
    (65, 28): 14,
    (65, 29): 14,
    (65, 31): 15,
    (65, 32): 36,
    (65, 45): 19,
    (65, 47): 16,
    (65, 49): 16,
    (65, 50): 17,
    (65, 52): 14,
    (65, 53): 14,
    (65, 54): 13,
    (65, 55): 14,
    (65, 56): 13,
    (65, 57): 14,
    (65, 58): 14,
    (65, 59): 12,
    (65, 60): 14,
    (65, 61): 12,
    (65, 62): 11,
    (65, 63): 11,
    (65, 64): 11,
    (65, 65): 11,
    (65, 66): 10,
    (65, 67): 9,
    (65, 68): 8,
    (65, 69): 6,
    (66, 14): 21,
    (66, 15): 20,
    (66, 16): 13,
    (66, 21): 12,
    (66, 28): 14,
    (66, 29): 13,
    (66, 31): 14,
    (66, 32): 35,
    (66, 33): 5,
    (66, 45): 19,
    (66, 48): 16,
    (66, 49): 16,
    (66, 50): 14,
    (66, 52): 11,
    (66, 53): 13,
    (66, 54): 12,
    (66, 55): 16,
    (66, 56): 13,
    (66, 57): 12,
    (66, 58): 14,
    (66, 59): 12,
    (66, 60): 14,
    (66, 61): 11,
    (66, 62): 11,
    (66, 63): 11,
    (66, 64): 11,
    (66, 65): 10,
    (66, 66): 9,
    (66, 67): 8,
    (66, 68): 8,
    (66, 69): 6,
    (67, 14): 20,
    (67, 15): 19,
    (67, 16): 13,
    (67, 21): 11,
    (67, 28): 13,
    (67, 29): 12,
    (67, 31): 25,
    (67, 32): 35,
    (67, 45): 18,
    (67, 49): 15,
    (67, 50): 15,
    (67, 52): 14,
    (67, 53): 13,
    (67, 54): 13,
    (67, 55): 15,
    (67, 56): 11,
    (67, 57): 12,
    (67, 58): 11,
    (67, 59): 11,
    (67, 60): 12,
    (67, 61): 10,
    (67, 62): 10,
    (67, 63): 9,
    (67, 64): 10,
    (67, 65): 9,
    (67, 66): 8,
    (67, 67): 8,
    (67, 68): 7,
    (67, 69): 5,
    (68, 13): 15,
    (68, 14): 19,
    (68, 15): 18,
    (68, 16): 12,
    (68, 28): 12,
    (68, 29): 12,
    (68, 31): 12,
    (68, 32): 34,
    (68, 45): 18,
    (68, 50): 14,
    (68, 52): 13,
    (68, 53): 13,
    (68, 54): 12,
    (68, 55): 13,
    (68, 56): 11,
    (68, 57): 11,
    (68, 58): 12,
    (68, 59): 14,
    (68, 60): 13,
    (68, 61): 9,
    (68, 62): 9,
    (68, 63): 10,
    (68, 64): 9,
    (68, 65): 8,
    (68, 66): 8,
    (68, 67): 7,
    (68, 68): 6,
    (68, 69): 5,
    (69, 14): 18,
    (69, 15): 18,
    (69, 16): 11,
    (69, 29): 11,
    (69, 56): 11,
    (69, 57): 9,
    (69, 60): 8,
    (69, 61): 8,
    (69, 62): 8,
    (69, 63): 8,
    (69, 64): 8,
    (69, 65): 6,
    (69, 66): 5,
    (69, 67): 5,
    (69, 68): 5,
    (70, 67): 3,
}


def validate_spaces_hanzi(text: str, bboxes: list[tuple[int, int, int, int]]) -> None:
    """Validate spacing in text by comparing with bbox gaps.

    Arguments:
        text: Text to validate
        bboxes: Bounding boxes [(x1, y1, x2, y2), ...]
    """
    # Check if validation is possible
    filtered_text = "".join([char for char in text if char not in ("\u3000", " ")])
    if len(filtered_text) != len(bboxes):
        raise ScinoephileException(
            f"Number of characters in text ({len(filtered_text)})"
            f" does not match number of boxes ({len(bboxes)})"
        )

    # Calculate widths and gaps
    widths = [bboxes[i][2] - bboxes[i][0] for i in range(len(bboxes))]
    gaps = [bboxes[i + 1][0] - bboxes[i][2] for i in range(len(bboxes) - 1)]

    # Iterate through text and assess gaps
    char_1_i = 0
    char_1_width_i = 0
    gap_i = 0
    while True:
        if char_1_i > len(text) - 2:
            break
        # Get char 1 and its width
        char_1 = text[char_1_i]
        char_1_width = widths[char_1_width_i]

        # Get provisional char 2 and its width
        char_2_i = char_1_i + 1
        char_2 = text[char_2_i]
        char_2_width_i = char_1_width_i + 1
        char_2_width = widths[char_2_width_i]

        # If char 2 is whitespace, iterate to next real char and track whitespace
        whitespace = ""
        while char_2_i < len(text) - 1:
            char_2 = text[char_2_i]
            if char_2 in (" ", "\u3000"):
                whitespace += char_2
                char_2_i += 1
                continue
            else:
                break

        # Get gap between char 1 and char 2, and maximum expected gap
        gap = gaps[gap_i]
        max_gap = max_gaps.get((char_1_width, char_2_width), 0)

        if gap > max_gap:
            if whitespace:
                warning(
                    f"{char_1} and {char_2} are separated by "
                    f"{gap} pixels, exceeding max of {max_gap}. "
                    f"Separated by whitespace '{whitespace}'."
                )
            else:
                warning(
                    f"{char_1} and {char_2} are separated by "
                    f"{gap} pixels, exceeding max of {max_gap}. "
                    f"(May add  ({char_1_width},{char_2_width}):{gap},  to max_gaps)"
                )
        char_1_i = char_2_i
        char_1_width_i = char_2_width_i
        gap_i += 1
