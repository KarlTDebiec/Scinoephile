#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manages bboxes."""
from __future__ import annotations

from logging import info

import numpy as np
from PIL import Image, ImageChops

from scinoephile.common import package_root


class BboxManager:
    """Manages bboxes."""

    merge_three_file_path = package_root / "data" / "ocr" / "merge_threes.csv"
    """Path to file containing specs for sets of three bboxes that should be merged."""
    merge_threes: dict[tuple[int, int, int, int, int, int, int, int], str] = {}
    """Dimensions and gaps betwee sets of three bboxes that should be merged."""
    merge_two_file_path = package_root / "data" / "ocr" / "merge_twos.csv"
    """Path to file containing specs for sets of two bboxes that should be merged."""
    merge_twos: dict[tuple[int, int, int, int, int], str] = {}
    """Dimensions and gaps between sets of two bboxes that should be merged."""

    def __init__(self):
        """Initialize."""
        if self.merge_two_file_path.exists():
            merge_twos_arr = np.genfromtxt(
                self.merge_two_file_path, delimiter=",", dtype=str, encoding="utf-8"
            )
            self.merge_twos = {
                tuple(map(int, row[1:])): row[0] for row in merge_twos_arr
            }
            self._save_merge_twos()
        if self.merge_three_file_path.exists():
            merge_threes_arr = np.genfromtxt(
                self.merge_three_file_path, delimiter=",", dtype=str, encoding="utf-8"
            )
            self.merge_threes = {
                tuple(map(int, row[1:])): row[0] for row in merge_threes_arr
            }
            self._save_merge_threes()

    def get_char_bboxes(
        self,
        img: Image.Image,
        text: str,
    ) -> list[tuple[int, int, int, int]]:
        """Get character bboxes within an image.

        Arguments:
            img: Image
            text: Provisional text present in image
        Returns:
            Character bounding boxes [(x1, y1, x2, y2), ...]
        """
        if img.mode != "L":
            raise ValueError("Image must be of mode 'L'")

        arr = np.array(img)

        # Split over x-axis into sections separated by white space
        sections = []
        section = None
        for i, nonwhite_pixels in enumerate(np.sum(arr < 255, axis=0)):
            if nonwhite_pixels > 0:
                if section is None:
                    section = [i, i]
                else:
                    section[1] = i
            elif section is not None:
                sections.append(section)
                section = None
        if section is not None:
            sections.append(section)

        # Determine top and bottom of each section to get final bbox
        bboxes = []
        for x1, x2 in sections:
            section = arr[:, x1:x2]
            nonwhite_pixels = np.sum(section < 255, axis=1)
            y1 = int(np.argmax(nonwhite_pixels > 0))
            y2 = int(len(nonwhite_pixels) - np.argmax(nonwhite_pixels[::-1] > 0) - 1)
            bboxes.append((x1, y1, x2, y2))

        # Clean up bboxes
        bboxes = self._merge_twos(bboxes, text)
        bboxes = self._merge_threes(bboxes, text)

        return bboxes

    def _merge_threes(
        self,
        bboxes: list[tuple[int, int, int, int]],
        text: str,
    ) -> list[tuple[int, int, int, int]]:
        """Merge sets of three adjacent bboxes that match specifications.

        Arguments:
            bboxes: Nascent list of bboxes [(x1, y1, x2, y2), ...]
            text: Provisional text present in image
        Returns:
            bboxes with sets of three adjacent bboxes matching specifications merged
        """

        merged_bboxes = []
        i = 0
        while i < len(bboxes):
            # Check if ellipsis
            if i <= len(bboxes) - 3:
                b1_x1, b1_y1, b1_x2, b1_y2 = bboxes[i]
                b2_x1, b2_y1, b2_x2, b2_y2 = bboxes[i + 1]
                b3_x1, b3_y1, b3_x2, b3_y2 = bboxes[i + 2]

                b1_width = b1_x2 - b1_x1
                b1_height = b1_y2 - b1_y1
                b1_b2_gap = b2_x1 - b1_x2
                b2_width = b2_x2 - b2_x1
                b2_height = b2_y2 - b2_y1
                b2_b3_gap = b3_x1 - b2_x2
                b3_width = b3_x2 - b3_x1
                b3_height = b3_y2 - b3_y1
                key = (
                    b1_width,
                    b1_height,
                    b1_b2_gap,
                    b2_width,
                    b2_height,
                    b2_b3_gap,
                    b3_width,
                    b3_height,
                )

                # Merge if appropriate
                if key in self.merge_threes:
                    merged_bboxes.append(
                        (
                            b1_x1,
                            min(b1_y1, b2_y1, b3_y1),
                            b3_x2,
                            max(b1_y2, b2_y2, b3_y2),
                        )
                    )
                    i += 3
                    continue

            # Otherwise, keep as is
            merged_bboxes.append(bboxes[i])
            i += 1

        return merged_bboxes

    def _merge_twos(
        self,
        bboxes: list[tuple[int, int, int, int]],
        text: str,
    ) -> list[tuple[int, int, int, int]]:
        """Merge sets of two adjacent bboxes that match specifications.

        Arguments:
            bboxes: Nascent list of bboxes [(x1, y1, x2, y2), ...]
            text: Provisional text present in image
        Returns:
            bboxes with sets of two adjacent bboxes matching specifications merged
        """
        merged_bboxes = []
        i = 0
        while i < len(bboxes):
            if i <= len(bboxes) - 2:
                b1_x1, b1_y1, b1_x2, b1_y2 = bboxes[i]
                b2_x1, b2_y1, b2_x2, b2_y2 = bboxes[i + 1]

                b1_width = b1_x2 - b1_x1
                b1_height = b1_y2 - b1_y1
                b1_b2_gap = b2_x1 - b1_x2
                b2_width = b2_x2 - b2_x1
                b2_height = b2_y2 - b2_y1
                key = (b1_width, b1_height, b1_b2_gap, b2_width, b2_height)

                # Merge if appropriate
                if key in self.merge_twos:
                    merged_bboxes.append(
                        (b1_x1, min(b1_y1, b2_y1), b2_x2, max(b1_y2, b2_y2))
                    )
                    i += 2
                    continue

            # Otherwise, keep as is
            merged_bboxes.append(bboxes[i])
            i += 1

        return merged_bboxes

    def _save_merge_twos(self):
        """Save merge_twos to file."""
        merge_two_arr = np.array(
            sorted([[value, *key] for key, value in self.merge_twos.items()])
        )
        np.savetxt(
            self.merge_two_file_path,
            merge_two_arr,
            delimiter=",",
            fmt="%s",
            encoding="utf-8",
        )
        info(f"Saved {self.merge_two_file_path}")

    def _save_merge_threes(self):
        """Save merge_threes to file."""
        merge_three_arr = np.array(
            sorted([[value, *key] for key, value in self.merge_twos.items()])
        )
        np.savetxt(
            self.merge_three_file_path,
            merge_three_arr,
            delimiter=",",
            fmt="%s",
            encoding="utf-8",
        )
        info(f"Saved {self.merge_three_file_path}")

    @staticmethod
    def get_bbox(img: Image.Image) -> tuple[int, int, int, int]:
        """Get bbox of non-white/transparent pixels in an image.

        Arguments:
            img: Image
        Returns:
            bbox of non-white/transparent pixels
        """
        img_l = img if img.mode == "L" else img.convert("L")
        mask = ImageChops.invert(img_l).point(lambda p: p > 0 and 255)
        bbox = mask.getbbox()
        return bbox
