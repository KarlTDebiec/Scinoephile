#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Media stream probing utilities."""

from __future__ import annotations

from pathlib import Path
from typing import cast

import ffmpeg

from scinoephile.core.exceptions import ScinoephileError

__all__ = ["get_media_streams"]


def get_media_streams(infile_path: Path) -> list[dict[str, object]]:
    """Return stream objects in a media file.

    Arguments:
        infile_path: media input file to inspect
    Returns:
        ffprobe stream objects
    Raises:
        ScinoephileError: if ffprobe fails
    """
    try:
        probe = ffmpeg.probe(str(infile_path))
    except ffmpeg.Error as exc:
        raise ScinoephileError(f"Could not probe media file {infile_path}") from exc

    return [
        cast("dict[str, object]", stream)
        for stream in probe.get("streams", [])
        if isinstance(stream, dict)
    ]
