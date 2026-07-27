#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle stream cache."""

from __future__ import annotations

import hashlib
import json
from contextlib import ExitStack
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory

import ffmpeg

from scinoephile.common.validation import val_output_dir_path
from scinoephile.core import ScinoephileError
from scinoephile.core.media import SubtitleStream
from scinoephile.image.subtitles import ImageSeries

__all__ = ["SubtitleCache"]

logger = getLogger(__name__)


class SubtitleCache:
    """Cache of subtitle streams extracted from media."""

    def __init__(self, cache_root_path: Path):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache
        """
        self.cache_dir_path = val_output_dir_path(
            cache_root_path / "media" / "subtitles"
        )
        """Directory in which cached subtitle streams are stored."""

    def cache(
        self,
        infile_path: Path,
        streams: list[SubtitleStream],
        *,
        overwrite: bool = False,
        render_images: bool = True,
    ):
        """Cache extracted subtitle streams.

        Arguments:
            infile_path: media input file
            streams: subtitle streams to cache
            overwrite: whether to replace matching cached subtitle artifacts
            render_images: whether to render SUP streams to image directories
        """
        # Determine which subtitle streams must be extracted
        missing: list[tuple[SubtitleStream, Path]] = []
        for stream in streams:
            stream_path = self.get_path(infile_path, stream)
            if overwrite and stream_path.exists():
                stream_path.unlink()
                logger.info(f"Removed subtitle stream cache: {stream_path}")
            if stream_path.exists():
                logger.info(f"Loaded subtitle stream from cache: {stream_path}")
            else:
                missing.append((stream, stream_path))

        # Extract missing streams in one ffmpeg run
        if missing:
            input_stream = ffmpeg.input(str(infile_path))
            with ExitStack() as stack:
                staged_paths: list[tuple[Path, Path]] = []
                output_streams = []
                for stream, stream_path in missing:
                    if not stream_path.parent.exists():
                        stream_path.parent.mkdir(parents=True)
                        logger.info(f"Created cache directory: {stream_path.parent}")
                    staging_dir_path = Path(
                        stack.enter_context(
                            TemporaryDirectory(
                                dir=stream_path.parent,
                                prefix=f".{stream_path.name}-",
                            )
                        )
                    )
                    staging_path = staging_dir_path / stream_path.name
                    staged_paths.append((staging_path, stream_path))
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

                if any(not path.is_file() for path, _ in staged_paths):
                    raise ScinoephileError(
                        f"Could not cache subtitle streams from {infile_path}"
                    )
                for staging_path, stream_path in staged_paths:
                    staging_path.replace(stream_path)
                    logger.info(f"Saved subtitle stream to cache: {stream_path}")

        # Render cached SUP streams when requested
        if render_images:
            self._cache_image_series(infile_path, streams, overwrite=overwrite)

    def get_path(self, infile_path: Path, stream: SubtitleStream) -> Path:
        """Get the cache path for an extracted subtitle stream.

        Arguments:
            infile_path: media input file
            stream: subtitle stream
        Returns:
            subtitle stream cache path
        """
        stat = infile_path.stat()
        payload = {
            "path": str(infile_path),
            "size": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
            "stream_index": stream.index,
            "codec_name": stream.codec_name,
        }
        encoded_payload = json.dumps(payload, sort_keys=True).encode("utf-8")
        cache_key = hashlib.sha256(encoded_payload).hexdigest()
        return self.cache_dir_path / cache_key / f"{stream.index}.{stream.extension}"

    def _cache_image_series(
        self,
        infile_path: Path,
        streams: list[SubtitleStream],
        *,
        overwrite: bool,
    ):
        """Render cached SUP subtitle streams to image directories.

        Arguments:
            infile_path: media input file
            streams: subtitle streams to cache
            overwrite: whether to replace matching rendered image artifacts
        """
        for stream in streams:
            if stream.extension != "sup":
                continue
            stream_path = self.get_path(infile_path, stream)
            image_dir_path = stream_path.parent / "image-series"
            if (image_dir_path / "index.html").exists() and not overwrite:
                logger.info(
                    f"Loaded image subtitle series from cache: {image_dir_path}"
                )
                continue
            image_series = ImageSeries.load(stream_path)
            image_series.save(image_dir_path)
            logger.info(f"Saved image subtitle series to cache: {image_dir_path}")
