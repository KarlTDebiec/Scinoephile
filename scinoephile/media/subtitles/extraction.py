#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle extraction from media files."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from shutil import copy2

from scinoephile.core.media import SubtitleStream

from .cache import (
    cache_subtitles,
    get_subtitle_cache_path,
)

__all__ = ["extract_subtitle_stream"]

logger = getLogger(__name__)


def extract_subtitle_stream(
    infile_path: Path,
    stream: SubtitleStream,
    outfile_path: Path,
    *,
    cache_dir_path: Path | None = None,
) -> Path:
    """Extract a subtitle stream using a runtime cache.

    Arguments:
        infile_path: media input file
        stream: subtitle stream to extract
        outfile_path: requested output path
        cache_dir_path: cache directory path
    Returns:
        output path
    """
    cache_subtitles(
        infile_path,
        [stream],
        cache_dir_path=cache_dir_path,
        render_images=False,
    )
    stream_path = get_subtitle_cache_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    if stream_path != outfile_path:
        if not outfile_path.parent.exists():
            outfile_path.parent.mkdir(parents=True)
            logger.info(f"Created subtitle output directory: {outfile_path.parent}")
        copy2(stream_path, outfile_path)
        logger.info(f"Extracted subtitle stream to {outfile_path}")
    return outfile_path
