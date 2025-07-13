#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series of subtitles with images."""

from __future__ import annotations

from logging import info
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from pysubs2 import SSAFile

from scinoephile.common import DirectoryNotFoundError
from scinoephile.common.validation import (
    validate_input_directory,
    validate_output_directory,
    validate_output_file,
)
from scinoephile.core import ScinoephileError, Series
from scinoephile.image.image_subtitle import ImageSubtitle


class ImageSeries(Series):
    """Series of subtitles with images."""

    event_class = ImageSubtitle
    """Class of individual subtitle events."""
    events: list[ImageSubtitle]
    """Individual subtitle events."""

    def __init__(self) -> None:
        """Initialize."""
        super().__init__()

        self._fill_color = None
        self._outline_color = None

    @property
    def fill_color(self) -> int:
        """Fill color of text images."""
        if self._fill_color is None:
            self._init_fill_and_outline_colors()
        return self._fill_color

    @property
    def outline_color(self) -> int:
        """Outline color of text images."""
        if self._outline_color is None:
            self._init_fill_and_outline_colors()
        return self._outline_color

    def save(self, path: str, format_: str | None = None, **kwargs: Any) -> None:
        """Save series to an output file.

        Arguments:
            path: Output file path
            format_: Output file format
            **kwargs: Additional keyword arguments
        """
        path = Path(path)

        # Check if directory
        if format_ == "png" or (not format_ and path.suffix == ""):
            path = validate_output_directory(path)
            self._save_png(path, **kwargs)
            info(f"Saved series to {path}")
            return

        # Otherwise, continue as superclass SSAFile
        path = validate_output_file(path)
        SSAFile.save(self, path, format_=format_, **kwargs)
        info(f"Saved series to {path}")

    def _save_png(self, fp: Path, **kwargs: Any) -> None:
        """Save series to directory of png files.

        Arguments:
            fp: Path to outpt directory
            **kwargs: Additional keyword arguments
        """
        # Prepare empty directory, deleting existing files if needed
        if fp.exists() and fp.is_dir():
            for file in fp.iterdir():
                file.unlink()
                info(f"Deleted {file}")
        else:
            fp.mkdir(parents=True)
            info(f"Created directory {fp}")

        # Save images
        for i, event in enumerate(self, 1):
            outfile_path = fp / f"{i:04d}_{event.start:08d}_{event.end:08d}.png"
            event.img.save(outfile_path)
            info(f"Saved image to {outfile_path}")

        # Save text
        outfile_path = fp / f"{fp.stem}.srt"
        super().save(outfile_path, format_="srt")

    @classmethod
    def load(
        cls,
        path: str,
        encoding: str = "utf-8",
        format_: str | None = None,
        **kwargs: Any,
    ) -> ImageSeries:
        """Load series from an input file.

        Arguments:
            path: Input file path
            encoding: Input file encoding
            format_: Input file format
            **kwargs: Additional keyword arguments
        Returns:
            Loaded series
        """
        try:
            validated_path = validate_input_directory(path)
            return cls._load_png(validated_path, **kwargs)
        except (DirectoryNotFoundError, NotADirectoryError) as exc:
            raise ValueError(
                f"{cls.__name__}'s path must be path to a directory containing one srt "
                "file containing N subtitles and N png files."
            ) from exc

    @classmethod
    def _load_png(cls, fp: Path, **kwargs: Any) -> ImageSeries:
        """Load series from a directory of png files.

        Arguments:
            fp: Path to input directory
            **kwargs: Additional keyword arguments
        Returns:
            Loaded series
        """
        series = cls()
        series.format = "png"

        # Load text
        srt_path = fp / f"{fp.stem}.srt"
        text_series = Series.load(srt_path)

        # Load images
        infiles = sorted([path for path in fp.iterdir() if path.suffix == ".png"])
        if len(text_series) != len(infiles):
            raise ScinoephileError(
                f"Number of images in {fp} ({len(series)}) "
                f"does not match number of subtitles in {srt_path} "
                f"({len(text_series)})"
            )
        for text_event, infile in zip(text_series, infiles):
            img = Image.open(infile)
            if img.mode == "RGBA":
                arr = np.array(img)
                if np.all(arr[:, :, 0] == arr[:, :, 1]) and np.all(
                    arr[:, :, 1] == arr[:, :, 2]
                ):
                    img = img.convert("LA")
                    img.save(infile)
                    info(f"Converted {infile} to LA and resaved")
            series.events.append(
                cls.event_class(
                    start=text_event.start,
                    end=text_event.end,
                    img=img,
                    text=text_event.text,
                    series=series,
                )
            )

        return series

    def _init_fill_and_outline_colors(self) -> None:
        """Initialzie the fill and outline colors used in this series.

        * Uses the most common two colors, which works correctly for tested images.
        * Tested images used a 16-color palette.
        """
        hist = np.zeros(256, dtype=np.uint64)
        for subtitle in self:
            grayscale = subtitle.arr[:, :, 0]
            alpha = subtitle.arr[:, :, 1]
            mask = alpha != 0
            values = grayscale[mask]
            np.add.at(hist, values, 1)

        fill, outline = map(int, np.argsort(hist)[-2:])
        if outline > fill:
            fill, outline = outline, fill
        self._fill_color = fill
        self._outline_color = outline
