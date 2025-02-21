#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to OCR validation."""
from __future__ import annotations

from logging import warning
from pathlib import Path
from pprint import pprint

from scinoephile.common.validation import validate_output_directory
from scinoephile.core import ScinoephileException
from scinoephile.image.bbox import get_char_bboxes
from scinoephile.image.drawing import (
    get_image_with_white_bg,
)
from scinoephile.image.image_series import ImageSeries


def validate_ocr_hanzi(series: ImageSeries, output_path: Path) -> None:
    """Validate OCR of a hanzi image series.

    Arguments:
        series: Series to validate
        output_path: Directory in which to save validation results
    """
    output_path = validate_output_directory(output_path)
    NEW_LIMITS = {}

    for i, event in enumerate(series.events, 1):
        # Prepare source image
        img_with_white_bg = get_image_with_white_bg(event.img)
        bboxes = get_char_bboxes(img_with_white_bg)
        # img_with_bboxes = get_image_annotated_with_char_bboxes(
        #     img_with_white_bg, bboxes
        # )

        # Draw image of OCRed text, aligned to source image
        try:
            # img_of_text = get_image_of_text_with_char_alignment(
            #     event.text, event.img.size, bboxes
            # )
            NEW_NEW_LIMITS = validate_spaces_hanzi(event.text, bboxes)
            NEW_LIMITS.update(NEW_NEW_LIMITS)
        except ScinoephileException as e:
            warning(f"Subtitle {i} encountered the following exception: {e}")
            # img_of_text = get_image_of_text(event.text, event.img.size)
        # img_of_text_scaled = get_image_scaled(img_with_white_bg, img_of_text)

        # Draw difference between source and OCRed text images
        # img_diff = get_image_diff(img_with_white_bg, img_of_text_scaled)

        # Stack images and rescale for convenience
        # img_stack = get_images_stacked(img_with_bboxes, img_of_text_scaled, img_diff)
        # img_resized = img_stack.resize(
        #     (img_stack.width * 10, img_stack.height * 10), Image.NEAREST  # noqa
        # )

        # Save image
        # img_resized.save(output_path / f"{i:04d}.png")
        # info(f"Saved {output_path / f'{i:04d}.png'}")

    # Merged max_gaps with NEW_LIMITS
    UPDATED_LIMITS = {**max_gaps, **NEW_LIMITS}
    pprint(UPDATED_LIMITS)


max_gaps = {
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
    (15, 66): 46,
    (15, 67): 45,
    (15, 68): 45,
    (16, 62): 54,
    (16, 63): 54,
    (16, 64): 54,
    (16, 65): 53,
    (16, 66): 53,
    (16, 67): 52,
    (16, 68): 51,
    (21, 64): 49,
    (21, 62): 49,
    (28, 64): 40,
    (28, 65): 40,
    (28, 66): 40,
    (29, 15): 51,
    (29, 62): 41,
    (29, 65): 39,
    (29, 67): 38,
    (31, 65): 37,
    (31, 64): 37,
    (31, 68): 35,
    (32, 63): 17,
    (32, 66): 13,
    (32, 68): 12,
    (45, 62): 18,
    (45, 63): 18,
    (45, 65): 17,
    (45, 67): 16,
    (48, 67): 16,
    (49, 57): 23,
    (50, 58): 22,
    (52, 63): 16,
    (52, 64): 18,
    (52, 65): 14,
    (53, 63): 18,
    (54, 45): 25,
    (54, 63): 15,
    (55, 55): 18,
    (55, 60): 16,
    (55, 64): 15,
    (55, 65): 15,
    (55, 66): 14,
    (55, 67): 12,
    (55, 68): 11,
    (56, 62): 14,
    (57, 55): 17,
    (57, 57): 17,
    (57, 63): 14,
    (57, 64): 14,
    (57, 65): 15,
    (57, 66): 14,
    (57, 67): 11,
    (57, 68): 13,
    (58, 16): 13,
    (58, 64): 12,
    (58, 65): 12,
    (58, 67): 12,
    (58, 68): 10,
    (59, 60): 13,
    (59, 62): 11,
    (59, 65): 12,
    (59, 66): 12,
    (59, 67): 11,
    (60, 16): 18,
    (60, 55): 17,
    (60, 60): 13,
    (60, 63): 11,
    (60, 64): 12,
    (60, 65): 13,
    (60, 66): 9,
    (60, 67): 10,
    (61, 15): 22,
    (61, 16): 15,
    (61, 57): 13,
    (61, 62): 13,
    (61, 64): 11,
    (61, 65): 11,
    (61, 66): 10,
    (61, 67): 12,
    (62, 14): 22,
    (62, 15): 21,
    (62, 16): 14,
    (62, 28): 14,
    (62, 45): 20,
    (62, 49): 19,
    (62, 60): 14,
    (62, 61): 11,
    (62, 62): 12,
    (62, 63): 13,
    (62, 64): 12,
    (62, 65): 11,
    (62, 66): 11,
    (62, 67): 10,
    (62, 68): 10,
    (62, 69): 7,
    (63, 14): 21,
    (63, 15): 21,
    (63, 16): 15,
    (63, 28): 14,
    (63, 29): 13,
    (63, 31): 15,
    (63, 32): 36,
    (63, 55): 14,
    (63, 56): 15,
    (63, 58): 13,
    (63, 60): 12,
    (63, 61): 12,
    (63, 62): 12,
    (63, 63): 11,
    (63, 64): 11,
    (63, 65): 11,
    (63, 66): 10,
    (63, 67): 10,
    (63, 68): 8,
    (64, 14): 21,
    (64, 15): 20,
    (64, 16): 13,
    (64, 21): 12,
    (64, 28): 14,
    (64, 29): 14,
    (64, 32): 38,
    (64, 45): 20,
    (64, 54): 14,
    (64, 57): 12,
    (64, 58): 10,
    (64, 60): 13,
    (64, 61): 12,
    (64, 62): 11,
    (64, 63): 12,
    (64, 64): 11,
    (64, 65): 11,
    (64, 66): 10,
    (64, 67): 10,
    (64, 68): 8,
    (64, 69): 7,
    (65, 14): 20,
    (65, 15): 20,
    (65, 16): 14,
    (65, 28): 14,
    (65, 29): 13,
    (65, 45): 19,
    (65, 50): 16,
    (65, 54): 13,
    (65, 55): 14,
    (65, 57): 11,
    (65, 59): 12,
    (65, 60): 12,
    (65, 61): 10,
    (65, 62): 11,
    (65, 63): 11,
    (65, 64): 11,
    (65, 65): 11,
    (65, 66): 10,
    (65, 67): 8,
    (65, 68): 7,
    (65, 69): 6,
    (66, 14): 19,
    (66, 15): 20,
    (66, 16): 12,
    (66, 28): 14,
    (66, 31): 13,
    (66, 32): 35,
    (66, 45): 19,
    (66, 48): 16,
    (66, 53): 10,
    (66, 55): 11,
    (66, 57): 11,
    (66, 59): 10,
    (66, 61): 10,
    (66, 62): 11,
    (66, 63): 9,
    (66, 64): 10,
    (66, 65): 10,
    (66, 66): 9,
    (66, 67): 8,
    (66, 68): 8,
    (67, 14): 20,
    (67, 15): 18,
    (67, 16): 12,
    (67, 28): 12,
    (67, 29): 12,
    (67, 45): 18,
    (67, 52): 14,
    (67, 55): 12,
    (67, 57): 11,
    (67, 58): 10,
    (67, 59): 9,
    (67, 60): 10,
    (67, 61): 9,
    (67, 62): 10,
    (67, 63): 9,
    (67, 64): 9,
    (67, 65): 9,
    (67, 66): 8,
    (67, 67): 7,
    (67, 68): 7,
    (68, 14): 19,
    (68, 16): 11,
    (68, 28): 12,
    (68, 31): 12,
    (68, 32): 34,
    (68, 52): 13,
    (68, 57): 10,
    (68, 58): 9,
    (68, 62): 9,
    (68, 63): 8,
    (68, 64): 9,
    (68, 65): 8,
    (68, 66): 7,
    (68, 67): 6,
    (68, 68): 5,
    (69, 15): 18,
    (69, 62): 6,
    (69, 63): 8,
    (69, 64): 7,
    (69, 65): 6,
    (69, 67): 5,
    (69, 68): 5,
}

gap_strings = {
    260: "　　",
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
    print(f"{text} {widths} {gaps}")

    NEW_LIMITS = {}

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
                if gap < 25:
                    NEW_LIMITS[(char_1_width, char_2_width)] = gap
        char_1_i = char_2_i
        char_1_width_i = char_2_width_i
        gap_i += 1
    return NEW_LIMITS
