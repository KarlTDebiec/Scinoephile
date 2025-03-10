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

from scinoephile.common.validation import (
    validate_input_file,
    validate_output_directory,
    validate_output_file,
)
from scinoephile.core import ScinoephileException, Series
from scinoephile.image.image_subtitle import ImageSubtitle
from scinoephile.image.sup import read_sup_series


class ImageSeries(Series):
    """Series of subtitles with images."""

    event_class = ImageSubtitle
    """Class of individual subtitle events"""

    events: list[ImageSubtitle]
    """Individual subtitle events."""

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
