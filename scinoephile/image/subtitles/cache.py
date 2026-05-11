#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Rendered image subtitle cache helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import NotRequired, TypedDict

from PIL import Image

from .series import ImageSeries
from .subtitle import ImageSubtitle

__all__ = [
    "IMAGE_SERIES_CACHE_VERSION",
    "ImageSubtitleManifest",
    "is_valid_image_subtitle_cache",
    "load_cached_image_subtitles",
    "load_image_subtitle_manifest",
    "save_image_subtitle_manifest",
]

IMAGE_SERIES_CACHE_VERSION = 1
"""Rendered image subtitle cache schema version."""


class ImageSubtitleManifest(TypedDict):
    """Rendered image subtitle cache manifest."""

    version: int
    """Manifest schema version."""
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
        manifest["version"] == IMAGE_SERIES_CACHE_VERSION
        and manifest["event_count"] >= 0
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
