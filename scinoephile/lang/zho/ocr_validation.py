#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Chinese OCR validation helpers."""

from __future__ import annotations

from logging import warning
from pathlib import Path

from scinoephile.image.drawing import get_img_with_bboxes
from scinoephile.image.ocr import BboxManager
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

__all__ = ["validate_zho_ocr"]


def validate_zho_ocr(
    series: ImageSeries,
    output_dir_path: Path | str | None = None,
    stop_at_idx: int | None = None,
    interactive: bool = False,
) -> None:
    """Validate OCR text against image series bboxes.

    Arguments:
        series: ImageSeries to validate
        output_dir_path: directory in which to save validation images
        stop_at_idx: stop processing at this index
        interactive: whether to prompt user for confirmations
    """
    bbox_mgr = BboxManager()
    output_series = ImageSeries() if output_dir_path is not None else None
    if stop_at_idx is None:
        stop_at_idx = len(series) - 1
    for sub_idx, sub in enumerate(series.events):
        if sub_idx > stop_at_idx:
            break
        for message in bbox_mgr.validate_char_bboxes(
            sub, sub_idx=sub_idx, interactive=interactive
        ):
            warning(message)
        if output_dir_path is not None:
            annotated_img = get_img_with_bboxes(sub.img, sub.bboxes)
            output_series.events.append(
                ImageSubtitle(
                    img=annotated_img,
                    start=sub.start,
                    end=sub.end,
                    text=sub.text,
                    series=output_series,
                )
            )
    if output_dir_path is not None:
        output_series.save(output_dir_path)
