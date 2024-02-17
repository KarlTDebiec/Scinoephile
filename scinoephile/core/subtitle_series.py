#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series of subtitles."""
from __future__ import annotations

from logging import info
from typing import Any

from pysubs2 import SSAFile

from scinoephile.common import validate_input_file_path, validate_output_file_path
from scinoephile.core.subtitle import Subtitle


class SubtitleSeries(SSAFile):
    """Series of subtitles.

    TODO: Add support for loading from and saving to hdf5
    """

    event_class = Subtitle
    """Class of individual subtitle events."""

    def save(self, path: str, format_: str | None = None, **kwargs: Any) -> None:
        """Save subtitles to an output file.

        Arguments:
            path: output file path
            format_: output file format
            **kwargs: additional keyword arguments
        """
        path = validate_output_file_path(path)
        SSAFile.save(self, path, format_=format_, **kwargs)
        info(f"Saved subtitles to {path}")

    @classmethod
    def load(
        cls,
        path: str,
        encoding: str = "utf-8",
        format_: str | None = None,
        **kwargs: Any,
    ) -> SubtitleSeries:
        """Load subtitles from an input file.

        Arguments:
            path : input file path
            encoding: input file encoding
            format_: input file format
            **kwargs: additional keyword arguments
        Returns:
            loaded subtitles
        """
        path = validate_input_file_path(path)

        with open(path, encoding=encoding) as fp:
            subtitles = cls.from_file(fp, format_=format_, **kwargs)
            events = []
            for ssaevent in subtitles.events:
                events.append(cls.event_class(series=subtitles, **ssaevent.as_dict()))
            subtitles.events = events

        info(f"Loaded subtitles from {path}")
        return subtitles
