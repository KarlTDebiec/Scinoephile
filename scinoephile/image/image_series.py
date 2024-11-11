#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series of subtitles with images."""
from __future__ import annotations

from logging import info
from pathlib import Path
from typing import Any, BinaryIO

import h5py
from h5py import File
from pysubs2 import SSAFile, make_time

from scinoephile.common.validation import validate_input_file, validate_output_file
from scinoephile.core import Series
from scinoephile.image.image_subtitle import ImageSubtitle
from scinoephile.image.sup import read_sup_series


class ImageSeries(Series):
    """Series of subtitles with images."""

    event_class = ImageSubtitle
    """Class of individual subtitle events"""

    def save(self, path: str, format_: str | None = None, **kwargs: Any) -> None:
        """Save series to an output file.

        Arguments:
            path: output file path
            format_: output file format
            **kwargs: additional keyword arguments
        """
        path = validate_output_file(path)

        # Check if hdf5
        if format_ == "hdf5" or path.suffix in (".hdf5", ".h5"):
            with h5py.File(path) as fp:
                self._save_hdf5(fp, **kwargs)
            info(f"Saved series to {path}")
            return

        # Check if directory
        if format_ == "png" or path.is_dir():
            self._save_png(path, **kwargs)
            info(f"Saved series to {path}")
            return

        # Otherwise, continue as superclass SSAFile
        SSAFile.save(self, path, format_=format_, **kwargs)
        info(f"Saved series to {path}")

    def _save_hdf5(self, fp: File, **kwargs: Any) -> None:
        """Save series to an output hdf5 file.

        Arguments
            fp: open hdf5 output file
            **kwargs: Additional keyword arguments
        """
        raise NotImplementedError()

    def _save_png(self, fp: Path, **kwargs: Any) -> None:
        """Save series to directory of png files.

        Arguments:
            fp: path to outpt directory
            **kwargs: dditional keyword arguments
        """
        raise NotImplementedError()

    @classmethod
    def load(
        cls,
        path: str,
        encoding: str = "utf-8",
        format_: str | None = None,
        **kwargs: Any,
    ) -> Series:
        """Load series from an input file.

        Arguments:
            path : input file path
            encoding: input file encoding
            format_: input file format
            **kwargs: additional keyword arguments
        Returns:
            loaded series
        """
        path = validate_input_file(path)

        # Check if hdf5
        if format_ == "hdf5" or path.suffix in (".hdf5", ".h5"):
            with h5py.File(path) as fp:
                return cls._load_hdf5(fp, **kwargs)

        # Check if sup
        if format_ == "sup" or path.suffix == ".sup":
            with open(path, "rb") as fp:
                return cls._load_sup(fp, **kwargs)

        raise ValueError(
            f"{cls.__name__} does not support format {format_}, must be hdf5 or sup"
        )

    @classmethod
    def _load_hdf5(cls, fp: File, **kwargs: Any) -> ImageSeries:
        """Load series from an input hdf5 file.

        Arguments:
            fp: open hdf5 input file
            **kwargs: additional keyword arguments
        Returns:
            Loaded series
        """
        raise NotImplementedError()

    @classmethod
    def _load_sup(cls, fp: BinaryIO, **kwargs: Any) -> ImageSeries:
        """Load series from an input sup file.

        Args:
            fp: open binary file
            **kwargs: additional keyword arguments
        Returns:
            loaded series
        """
        # Initialize
        series = cls()
        series.format = "sup"

        # Parse infile
        bytes = fp.read()
        starts, ends, images = read_sup_series(bytes)
        for start, end, image in zip(starts, ends, images):
            series.events.append(
                cls.event_class(
                    start=make_time(s=start),
                    end=make_time(s=end),
                    data=image,
                    series=series,
                )
            )

        return series
