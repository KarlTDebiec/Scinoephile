#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle stream extraction into the runtime cache."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from tempfile import TemporaryDirectory

import ffmpeg

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.media import SubtitleStream
from scinoephile.image.subtitles import ImageSeries

from .cache import SubtitleCache

__all__ = ["SubtitleExtractor"]


class SubtitleExtractor:
    """Extracts subtitle streams and stores them in a SubtitleCache."""

    def __init__(self, cache: SubtitleCache | None = None):
        """Initialize.

        Arguments:
            cache: subtitle stream cache, or None to create one with default settings
        """
        self._cache = cache if cache is not None else SubtitleCache()
        """Subtitle stream cache."""

    def extract(
        self,
        infile_path: Path,
        streams: Sequence[SubtitleStream],
        *,
        render_images: bool = True,
    ) -> list[Path]:
        """Extract missing subtitle streams into the cache.

        Arguments:
            infile_path: media input file
            streams: subtitle streams to extract
            render_images: whether to render SUP streams to image directories
        Returns:
            cached subtitle stream paths in input order
        """
        # Identify the subtitle streams absent from the cache
        missing = [
            stream
            for stream in streams
            if self._cache.load(infile_path, stream) is None
        ]

        # Extract all missing streams in one ffmpeg run
        if missing:
            input_stream = ffmpeg.input(str(infile_path))
            with TemporaryDirectory(
                dir=self._cache.cache_dir_path,
                prefix=".subtitle-extraction-",
            ) as temp_dir:
                staged_paths: list[tuple[SubtitleStream, Path]] = []
                output_streams = []
                for stream in missing:
                    staging_path = Path(temp_dir) / f"{stream.index}.{stream.extension}"
                    staged_paths.append((stream, staging_path))
                    output_streams.append(
                        input_stream.output(
                            str(staging_path),
                            **{
                                "map": f"0:{stream.index}",
                                "c:s": stream.output_codec,
                            },
                        )
                    )
                try:
                    ffmpeg.merge_outputs(*output_streams).run(
                        quiet=False,
                        overwrite_output=True,
                    )
                except ffmpeg.Error as exc:
                    raise ScinoephileError(
                        f"Could not cache subtitle streams from {infile_path}"
                    ) from exc
                if any(not path.is_file() for _, path in staged_paths):
                    raise ScinoephileError(
                        f"Could not cache subtitle streams from {infile_path}"
                    )
                for stream, staging_path in staged_paths:
                    self._cache.save(infile_path, stream, staging_path)

        stream_paths = [self._cache.get_path(infile_path, stream) for stream in streams]

        # Render cached SUP streams when requested
        if render_images:
            self._render_image_series(infile_path, streams, stream_paths)
        return stream_paths

    def _render_image_series(
        self,
        infile_path: Path,
        streams: Sequence[SubtitleStream],
        stream_paths: Sequence[Path],
    ):
        """Render cached SUP subtitle streams to image directories.

        Arguments:
            infile_path: media input file
            streams: subtitle streams to render
            stream_paths: cached subtitle stream paths
        """
        for stream, stream_path in zip(streams, stream_paths, strict=True):
            if stream.extension != "sup":
                continue
            if self._cache.load_image_series(infile_path, stream) is not None:
                continue
            image_series = ImageSeries.load(stream_path)
            self._cache.save_image_series(infile_path, stream, image_series)
