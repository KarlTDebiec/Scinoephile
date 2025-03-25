#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series of subtitles with images."""
from __future__ import annotations

from logging import info
from pathlib import Path
from typing import Any, BinaryIO

import numpy as np
from PIL import Image
from pysubs2 import SSAFile, make_time
from scipy.signal import find_peaks

from scinoephile.common.validation import (
    validate_input_file,
    validate_output_directory,
    validate_output_file,
)
from scinoephile.core import ScinoephileException, Series
from scinoephile.image.drawing import get_text_colors
from scinoephile.image.image_subtitle import ImageSubtitle
from scinoephile.image.sup import read_sup_series


class ImageSeries(Series):
    """Series of subtitles with images."""

    event_class = ImageSubtitle
    """Class of individual subtitle events"""

    events: list[ImageSubtitle]
    """Individual subtitle events."""

    def __init__(self) -> None:
        """Initialize."""
        super().__init__()

        self._inner_color = None
        self._outer_color = None

    @property
    def inner_color(self):
        if self._inner_color is None:
            arrs = [e.data for e in self.events]
            self._inner_color, self._outer_color = get_text_colors(arrs)
        return self._inner_color

    @property
    def outer_color(self):
        if self._outer_color is None:
            arrs = [e.data for e in self.events]
            self._inner_color, self._outer_color = get_text_colors(arrs)
        return self._outer_color

    def save(self, path: str, format_: str | None = None, **kwargs: Any) -> None:
        """Save series to an output file.

        Arguments:
            path: output file path
            format_: output file format
            **kwargs: additional keyword arguments
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

    def _get_colors(self):
        # Calculate histogram of grayscale shades, excluding pixels with transparency
        hist = np.zeros(256, dtype=np.uint64)
        for event in self.events:
            grayscale = event.data[:, :, 0]
            alpha = event.data[:, :, 1]
            mask = alpha > 0
            values = grayscale[mask]
            np.add.at(hist, values, 1)

        # Determine if image is 4-bit
        yat = {17, 35, 54, 70, 88, 106, 123, 132, 149, 167, 185, 203, 220, 238, 255}
        nonzero_indices = set(map(int, np.nonzero(hist)[0]))
        four_bit = nonzero_indices.issubset(yat)

        # Find two largest peaks in histogram
        if four_bit:
            folded = np.zeros(16, dtype=hist.dtype)
            for i in range(16):
                folded[i] = hist[i * 16]
            peaks, _ = find_peaks(folded, distance=1, height=np.max(folded) * 0.1)
            sorted_peaks = sorted(peaks, key=lambda p: folded[p], reverse=True)
            light, dark = sorted(sorted_peaks[:2])
        else:
            peaks, _ = find_peaks(hist, distance=10, height=np.max(hist) * 0.1)
            sorted_peaks = sorted(peaks, key=lambda p: hist[p], reverse=True)
            light, dark = sorted(sorted_peaks[:2])

        return light, dark

    def _save_png(self, fp: Path, **kwargs: Any) -> None:
        """Save series to directory of png files.

        Arguments:
            fp: path to outpt directory
            **kwargs: dditional keyword arguments
        """
        # Prepare empty directory, deleting existing files if needed
        if fp.exists() and fp.is_dir():
            for file in fp.iterdir():
                file.unlink()
        else:
            fp.mkdir(parents=True)

        # Save images
        for i, event in enumerate(self.events, 1):
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
            path : input file path
            encoding: input file encoding
            format_: input file format
            **kwargs: additional keyword arguments
        Returns:
            loaded series
        """
        path = Path(path)

        # Check if sup
        if format_ == "sup" or path.suffix == ".sup":
            path = validate_input_file(path)
            with open(path, "rb") as fp:
                return cls._load_sup(fp, **kwargs)

        # Check if directory
        if format_ == "png" or path.is_dir():
            return cls._load_png(path, **kwargs)

        raise ValueError(
            f"{cls.__name__} does not support format {format_}, must be sup or png"
        )

    @classmethod
    def _load_sup(cls, fp: BinaryIO, **kwargs: Any) -> ImageSeries:
        """Load series from an input sup file.

        Arguments:
            fp: open binary file
            **kwargs: additional keyword arguments
        Returns:
            loaded series
        """
        # Initialize
        series = cls()
        series.format = "sup"

        # Parse infile
        data = fp.read()
        starts, ends, images = read_sup_series(data)
        for start, end, image in zip(starts, ends, images):

            # Skip completely transparent images
            if np.all(image[:, :, 3] == 0):
                continue

            series.events.append(
                cls.event_class(
                    start=make_time(s=start),
                    end=make_time(s=end),
                    data=image,
                    series=series,
                )
            )

        return series

    @classmethod
    def _load_png(cls, fp: Path, **kwargs: Any) -> ImageSeries:
        """Load series from a directory of png files.

        Arguments:
            fp: path to input directory
            **kwargs: additional keyword arguments
        Returns:
            loaded series
        """
        series = cls()
        series.format = "png"

        # Load text
        srt_path = fp / f"{fp.stem}.srt"
        text_series = Series.load(srt_path)

        # Load images
        infiles = sorted([path for path in fp.iterdir() if path.suffix == ".png"])
        if len(text_series) != len(infiles):
            raise ScinoephileException(
                f"Number of images in {fp} ({len(series)}) "
                f"does not match number of subtitles in {srt_path} "
                f"({len(text_series)})"
            )
        for text_event, infile in zip(text_series, infiles):
            image = Image.open(infile)
            if image.mode == "RGBA":
                arr = np.array(image)
                if np.all(arr[:, :, 0] == arr[:, :, 1]) and np.all(
                    arr[:, :, 1] == arr[:, :, 2]
                ):
                    image = image.convert("LA")
                    image.save(infile)
                    info(f"Converted {infile} to LA and resaved")
            series.events.append(
                cls.event_class(
                    start=text_event.start,
                    end=text_event.end,
                    data=np.array(image),
                    text=text_event.text,
                    series=series,
                )
            )

        return series
