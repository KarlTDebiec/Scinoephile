#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle extraction from media files."""

from __future__ import annotations

from pathlib import Path

import ffmpeg

from scinoephile.core.exceptions import ScinoephileError

from .streams import get_media_streams
from .subtitle_stream import SubtitleStream

__all__ = [
    "extract_subtitle_stream",
    "get_subtitle_streams",
]


def extract_subtitle_stream(
    infile_path: Path,
    stream: SubtitleStream,
    outfile_path: Path,
) -> Path:
    """Extract one subtitle stream from a media file.

    Arguments:
        infile_path: video input file containing subtitle streams
        stream: subtitle stream to extract
        outfile_path: subtitle output path
    Returns:
        output path
    Raises:
        ScinoephileError: if ffmpeg fails
    """
    try:
        (
            ffmpeg.input(str(infile_path))
            .output(
                str(outfile_path),
                map=f"0:{stream.index}",
                **{"c:s": stream.output_codec},
            )
            .run(overwrite_output=True)
        )
    except ffmpeg.Error as exc:
        raise ScinoephileError(
            f"Could not extract subtitle stream {stream.index} from {infile_path}"
        ) from exc
    return outfile_path


def get_subtitle_streams(infile_path: Path) -> list[SubtitleStream]:
    """Return subtitle streams in a media file.

    Arguments:
        infile_path: media input file to inspect
    Returns:
        subtitle stream metadata
    Raises:
        ScinoephileError: if ffprobe fails
    """
    return [
        stream
        for stream in get_media_streams(infile_path)
        if isinstance(stream, SubtitleStream)
    ]
