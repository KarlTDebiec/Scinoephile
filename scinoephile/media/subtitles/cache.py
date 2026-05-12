#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle stream cache."""

from __future__ import annotations

import hashlib
import json
from logging import getLogger
from pathlib import Path
from shutil import rmtree
from typing import NotRequired, TypedDict
from uuid import uuid4

from PIL import Image

from scinoephile.common.subprocess import run_command
from scinoephile.core.media import SubtitleStream
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

__all__ = [
    "ImageSubtitleManifest",
    "cache_subtitle_streams",
    "get_cached_subtitle_stream_path",
    "get_or_create_image_subtitle_dir_path",
    "is_valid_image_subtitle_cache",
    "load_cached_image_subtitles",
    "load_image_subtitle_manifest",
    "save_image_subtitle_manifest",
]

logger = getLogger(__name__)


class ImageSubtitleManifest(TypedDict):
    """Rendered image subtitle cache manifest."""

    event_count: int
    """Number of subtitle events."""
    image_count: int
    """Number of cached image files."""
    first_start_ms: NotRequired[int | None]
    """First subtitle start time in milliseconds."""
    last_end_ms: NotRequired[int | None]
    """Last subtitle end time in milliseconds."""
    source_name: NotRequired[str]
    """Source subtitle stream filename."""
    source_size: NotRequired[int]
    """Source subtitle stream size in bytes."""


def cache_subtitle_streams(
    infile_path: Path,
    streams: list[SubtitleStream],
    *,
    cache_dir_path: Path | None = None,
):
    """Cache extracted subtitle streams using one ffmpeg command.

    Arguments:
        infile_path: media input file
        streams: subtitle streams to cache
        cache_dir_path: cache directory path
    """
    missing: list[tuple[SubtitleStream, Path]] = []
    for stream in streams:
        stream_path = get_cached_subtitle_stream_path(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        )
        try:
            stream_is_cached = stream_path.stat().st_size > 0
        except FileNotFoundError:
            stream_is_cached = False
        if stream_is_cached:
            logger.info(f"Loaded subtitle stream from cache: {stream_path}")
        else:
            missing.append((stream, stream_path))

    if not missing:
        return

    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("media", "subtitles")
    temp_dir_path = cache_dir_path / f"subtitle-streams-tmp-{uuid4().hex}"
    temp_dir_path.mkdir(parents=True, exist_ok=False)
    temp_stream_paths: list[tuple[Path, Path]] = []
    command = ["ffmpeg", "-y", "-i", str(infile_path)]
    for stream, stream_path in missing:
        temp_stream_path = temp_dir_path / stream_path.name
        temp_stream_paths.append((temp_stream_path, stream_path))
        command.extend(
            [
                "-map",
                f"0:{stream.index}",
                "-c:s",
                stream.output_codec,
                str(temp_stream_path),
            ]
        )
    try:
        run_command(command)
        for temp_stream_path, stream_path in temp_stream_paths:
            if temp_stream_path.exists():
                stream_path.parent.mkdir(parents=True, exist_ok=True)
                temp_stream_path.replace(stream_path)
            logger.info(f"Saved subtitle stream to cache: {stream_path}")
    finally:
        rmtree(temp_dir_path, ignore_errors=True)


def get_cached_subtitle_stream_path(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    cache_dir_path: Path | None = None,
) -> Path:
    """Get the cache path for an extracted subtitle stream.

    Arguments:
        infile_path: media input file
        stream: subtitle stream
        cache_dir_path: cache directory path
    Returns:
        subtitle stream cache path
    """
    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("media", "subtitles")
    resolved_path = infile_path.resolve()
    stat = resolved_path.stat()
    payload = {
        "path": str(resolved_path),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "stream_index": stream.index,
        "codec_name": stream.codec_name,
    }
    encoded_payload = json.dumps(payload, sort_keys=True).encode("utf-8")
    cache_key = hashlib.sha256(encoded_payload).hexdigest()
    return cache_dir_path / cache_key / f"{stream.index}.{stream.extension}"


def get_or_create_image_subtitle_dir_path(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    cache_dir_path: Path | None,
) -> Path:
    """Get or create the rendered image subtitle cache directory.

    Arguments:
        infile_path: media input file
        stream: subtitle stream
        cache_dir_path: cache directory path
    Returns:
        rendered image subtitle cache directory path
    """
    image_dir_path = _get_cached_image_subtitle_dir_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    if is_valid_image_subtitle_cache(image_dir_path):
        logger.info(f"Loaded image subtitle series from cache: {image_dir_path}")
        return image_dir_path

    stream_path = get_cached_subtitle_stream_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    cache_subtitle_streams(
        infile_path,
        [stream],
        cache_dir_path=cache_dir_path,
    )

    image_series = ImageSeries.load(stream_path)
    first_start_ms = None
    last_end_ms = None
    if image_series:
        first_start_ms = min(event.start for event in image_series)
        last_end_ms = max(event.end for event in image_series)

    image_dir_path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir_path = image_dir_path.parent / f"{image_dir_path.name}-tmp-{uuid4().hex}"
    image_series.save(temp_dir_path)
    save_image_subtitle_manifest(
        {
            "event_count": len(image_series),
            "image_count": len(list(temp_dir_path.glob("*.png"))),
            "first_start_ms": first_start_ms,
            "last_end_ms": last_end_ms,
            "source_name": stream_path.name,
            "source_size": stream_path.stat().st_size,
        },
        temp_dir_path,
    )
    if image_dir_path.exists():
        rmtree(image_dir_path)
    temp_dir_path.replace(image_dir_path)
    logger.info(f"Saved image subtitle series to cache: {image_dir_path}")
    return image_dir_path


def is_valid_image_subtitle_cache(image_dir_path: Path) -> bool:
    """Check whether a rendered image subtitle cache is valid.

    Arguments:
        image_dir_path: rendered image subtitle cache directory path
    Returns:
        whether the cache is valid
    """
    try:
        manifest = load_image_subtitle_manifest(image_dir_path)
    except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False
    return (
        manifest["event_count"] >= 0
        and manifest["image_count"] == manifest["event_count"]
        and "first_start_ms" in manifest
        and "last_end_ms" in manifest
        and (image_dir_path / "index.html").exists()
    )


def load_cached_image_subtitles(
    image_dir_path: Path,
    indexes: list[int],
) -> list[ImageSubtitle]:
    """Load selected cached image subtitle events.

    Arguments:
        image_dir_path: rendered image subtitle cache directory path
        indexes: zero-based subtitle event indexes
    Returns:
        image subtitle events
    """
    html_path = image_dir_path / "index.html"
    html_text = html_path.read_text(encoding="utf-8")
    html_events = ImageSeries._parse_html_events(html_text, image_dir_path)
    events = []
    for index in indexes:
        html_event = html_events[index]
        with Image.open(html_event["path"]) as opened:
            img = opened.copy()
        events.append(
            ImageSubtitle(
                start=html_event["start"],
                end=html_event["end"],
                img=img,
                text=html_event["text"],
            )
        )
    return events


def load_image_subtitle_manifest(
    image_dir_path: Path,
) -> ImageSubtitleManifest:
    """Load a rendered image subtitle cache manifest.

    Arguments:
        image_dir_path: rendered image subtitle cache directory path
    Returns:
        rendered image subtitle cache manifest
    """
    manifest_path = image_dir_path / "manifest.json"
    with manifest_path.open("r", encoding="utf-8") as file:
        raw = json.load(file)
    manifest: ImageSubtitleManifest = {
        "event_count": int(raw["event_count"]),
        "image_count": int(raw["image_count"]),
    }
    if "first_start_ms" in raw:
        if raw["first_start_ms"] is None:
            manifest["first_start_ms"] = None
        else:
            manifest["first_start_ms"] = int(raw["first_start_ms"])
    if "last_end_ms" in raw:
        if raw["last_end_ms"] is None:
            manifest["last_end_ms"] = None
        else:
            manifest["last_end_ms"] = int(raw["last_end_ms"])
    if "source_name" in raw:
        manifest["source_name"] = str(raw["source_name"])
    if "source_size" in raw:
        manifest["source_size"] = int(raw["source_size"])
    return manifest


def save_image_subtitle_manifest(
    manifest: ImageSubtitleManifest,
    image_dir_path: Path,
):
    """Save a rendered image subtitle cache manifest.

    Arguments:
        manifest: rendered image subtitle cache manifest
        image_dir_path: rendered image subtitle cache directory path
    """
    manifest_path = image_dir_path / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, ensure_ascii=False, sort_keys=True)


def _get_cached_image_subtitle_dir_path(
    infile_path: Path,
    stream: SubtitleStream,
    *,
    cache_dir_path: Path | None = None,
) -> Path:
    """Get the cache directory path for rendered image subtitles.

    Arguments:
        infile_path: media input file
        stream: subtitle stream
        cache_dir_path: cache directory path
    Returns:
        rendered image subtitle cache directory path
    """
    return (
        get_cached_subtitle_stream_path(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        ).parent
        / "image-series"
    )
