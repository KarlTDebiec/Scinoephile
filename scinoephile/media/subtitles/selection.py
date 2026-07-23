#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle stream selection from media files."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core import ScinoephileError
from scinoephile.core.media import SubtitleStream
from scinoephile.media.probe import get_subtitle_streams

__all__ = ["get_media_subtitle_stream"]


def get_media_subtitle_stream(
    infile_path: Path,
    stream_index: int | None,
) -> SubtitleStream:
    """Get selected image-based subtitle stream from a media input.

    Arguments:
        infile_path: media input file
        stream_index: selected subtitle stream index
    Returns:
        selected subtitle stream
    Raises:
        ScinoephileError: if stream selection fails
    """
    if stream_index is None:
        raise ScinoephileError("stream index is required for media OCR input")

    try:
        streams = get_subtitle_streams(infile_path)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ScinoephileError(
            f"Unable to inspect subtitle streams in {infile_path}: {exc}"
        ) from exc

    for stream in streams:
        if stream.index == stream_index:
            if stream.extension != "sup":
                raise ScinoephileError(
                    f"Subtitle stream {stream_index} is not an image-based SUP stream"
                )
            return stream
    raise ScinoephileError(f"No subtitle stream {stream_index} found in {infile_path}")
