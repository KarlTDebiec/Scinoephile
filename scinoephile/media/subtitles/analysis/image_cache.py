#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Rendered image subtitle cache."""

from __future__ import annotations

import json
from logging import getLogger
from pathlib import Path
from shutil import rmtree
from uuid import uuid4

from PIL import Image

from scinoephile.core.media import SubtitleStream
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle
from scinoephile.media.subtitles.cache import (
    cache_subtitle_stream_artifacts,
    get_cached_subtitle_artifact_path,
    is_valid_subtitle_artifact_cache,
)

from .types import ImageSubtitleManifest

__all__ = [
    "IMAGE_SERIES_CACHE_VERSION",
    "get_or_create_image_subtitle_dir_path",
    "load_cached_image_subtitles",
    "load_image_subtitle_manifest",
    "save_image_subtitle_manifest",
]

logger = getLogger(__name__)

IMAGE_SERIES_CACHE_VERSION = 1
"""Rendered image subtitle cache schema version."""


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
    if _is_valid_image_subtitle_cache(image_dir_path):
        logger.info(f"Loaded image subtitle series from cache: {image_dir_path}")
        return image_dir_path

    artifact_path = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    if not is_valid_subtitle_artifact_cache(artifact_path):
        cache_subtitle_stream_artifacts(
            infile_path,
            [stream],
            cache_dir_path=cache_dir_path,
        )

    image_series = ImageSeries.load(artifact_path)
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
            "version": IMAGE_SERIES_CACHE_VERSION,
            "event_count": len(image_series),
            "image_count": len(list(temp_dir_path.glob("*.png"))),
            "first_start_ms": first_start_ms,
            "last_end_ms": last_end_ms,
            "artifact_name": artifact_path.name,
            "artifact_size": artifact_path.stat().st_size,
        },
        temp_dir_path,
    )
    if image_dir_path.exists():
        rmtree(image_dir_path)
    temp_dir_path.replace(image_dir_path)
    logger.info(f"Saved image subtitle series to cache: {image_dir_path}")
    return image_dir_path


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
        "version": int(raw["version"]),
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
    if "artifact_name" in raw:
        manifest["artifact_name"] = str(raw["artifact_name"])
    if "artifact_size" in raw:
        manifest["artifact_size"] = int(raw["artifact_size"])
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
        get_cached_subtitle_artifact_path(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        ).parent
        / "image-series"
    )


def _is_valid_image_subtitle_cache(image_dir_path: Path) -> bool:
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
        manifest["version"] == IMAGE_SERIES_CACHE_VERSION
        and manifest["event_count"] >= 0
        and manifest["image_count"] == manifest["event_count"]
        and "first_start_ms" in manifest
        and "last_end_ms" in manifest
        and (image_dir_path / "index.html").exists()
    )
