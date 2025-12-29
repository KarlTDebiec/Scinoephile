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
) -> None:
    """Validate OCR text against image series bboxes.

    Arguments:
        series: ImageSeries to validate
        output_dir_path: Directory in which to save validation images
    """
    bbox_mgr = BboxManager()
    output_series = ImageSeries() if output_dir_path is not None else None
    for sub_idx, sub in enumerate(series, 1):
        if sub.bboxes is None:
            sub.bboxes = bbox_mgr.get_bboxes(sub, interactive=False)
        if sub.bboxes is None:
            warning(f"Subtitle {sub_idx:04d}: {sub.text} - no bboxes found.")
            if output_series is not None:
                output_series.events.append(
                    ImageSubtitle(
                        img=sub.img_with_white_bg,
                        start=sub.start,
                        end=sub.end,
                        text=sub.text,
                        series=output_series,
                    )
                )
            continue
        if len(sub.text_without_whitspace) != len(sub.bboxes):
            warning(
                f"Subtitle {sub_idx:04d}: {sub.text} - text has "
                f"{len(sub.text_without_whitspace)} non-whitespace characters, "
                f"but image has {len(sub.bboxes)} bboxes."
            )
        for message in bbox_mgr.validate_char_bboxes(sub, subtitle_index=sub_idx):
            warning(message)
        if output_dir_path is not None:
            annotated_img = get_img_with_bboxes(sub.img_with_white_bg, sub.bboxes)
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
