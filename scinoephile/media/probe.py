#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Media stream probing utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import ffmpeg

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.media import AudioStream, Stream, SubtitleStream, VideoStream

__all__ = [
    "get_streams",
    "get_subtitle_streams",
]


def get_streams(infile_path: Path) -> list[Stream]:
    """Return stream objects in a media file.

    Arguments:
        infile_path: media input file to inspect
    Returns:
        media stream metadata
    Raises:
        ScinoephileError: if ffprobe fails
    """
    try:
        probe = ffmpeg.probe(str(infile_path))
    except ffmpeg.Error as exc:
        raise ScinoephileError(f"Could not probe media file {infile_path}") from exc

    streams = []
    for stream in probe.get("streams", []):
        if not isinstance(stream, dict):
            continue
        stream_index = _get_stream_index(stream)
        if stream_index is None:
            continue
        streams.append(_from_ffprobe_stream(stream, stream_index))
    return streams


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
        for stream in get_streams(infile_path)
        if isinstance(stream, SubtitleStream)
    ]


def _from_ffprobe_stream(stream: dict[str, Any], stream_index: int) -> Stream:
    """Parse a probed ffmpeg stream into typed stream metadata.

    Arguments:
        stream: ffprobe stream object
        stream_index: absolute media stream index
    Returns:
        stream metadata
    """
    codec_type = _get_codec_type(stream)
    if codec_type == "audio":
        return _from_ffprobe_audio_stream(stream, stream_index)
    if codec_type == "subtitle":
        return _from_ffprobe_subtitle_stream(stream, stream_index)
    if codec_type == "video":
        return _from_ffprobe_video_stream(stream, stream_index)
    return Stream(
        index=stream_index,
        codec_type=codec_type,
        codec_name=_get_codec_name(stream, codec_type),
        language=_get_language(stream),
        title=_get_title(stream),
    )


def _from_ffprobe_audio_stream(
    stream: dict[str, Any], stream_index: int
) -> AudioStream:
    """Parse a probed ffmpeg stream into audio stream metadata.

    Arguments:
        stream: ffprobe stream object
        stream_index: absolute media stream index
    Returns:
        audio stream metadata
    """
    channels = stream.get("channels")
    if not isinstance(channels, int):
        channels = None
    return AudioStream(
        index=stream_index,
        codec_type="audio",
        codec_name=_get_codec_name(stream, "audio"),
        language=_get_language(stream),
        title=_get_title(stream),
        channels=channels,
    )


def _from_ffprobe_subtitle_stream(
    stream: dict[str, Any], stream_index: int
) -> SubtitleStream:
    """Parse a probed ffmpeg stream into subtitle metadata.

    Arguments:
        stream: ffprobe stream object
        stream_index: absolute media stream index
    Returns:
        subtitle stream metadata
    """
    disposition = stream.get("disposition")
    if not isinstance(disposition, dict):
        disposition = {}

    subtitle_count = stream.get("nb_read_packets")
    if isinstance(subtitle_count, int | str):
        try:
            subtitle_count = int(subtitle_count)
        except ValueError:
            subtitle_count = None
    else:
        subtitle_count = None

    return SubtitleStream(
        index=stream_index,
        codec_type="subtitle",
        codec_name=_get_codec_name(stream, "subtitle"),
        language=_get_language(stream),
        title=_get_title(stream),
        forced=bool(disposition.get("forced")),
        sdh=bool(disposition.get("hearing_impaired")),
        subtitle_count=subtitle_count,
    )


def _from_ffprobe_video_stream(
    stream: dict[str, Any], stream_index: int
) -> VideoStream:
    """Parse a probed ffmpeg stream into video stream metadata.

    Arguments:
        stream: ffprobe stream object
        stream_index: absolute media stream index
    Returns:
        video stream metadata
    """
    width = stream.get("width")
    if not isinstance(width, int):
        width = None
    height = stream.get("height")
    if not isinstance(height, int):
        height = None
    return VideoStream(
        index=stream_index,
        codec_type="video",
        codec_name=_get_codec_name(stream, "video"),
        language=_get_language(stream),
        title=_get_title(stream),
        width=width,
        height=height,
    )


def _get_codec_name(stream: dict[str, Any], fallback: str = "unknown") -> str:
    """Return codec name from an ffprobe stream.

    Arguments:
        stream: ffprobe stream object
        fallback: fallback codec name
    Returns:
        codec name
    """
    codec_name = stream.get("codec_name")
    if not isinstance(codec_name, str) or not codec_name:
        codec_name = fallback
    return codec_name


def _get_codec_type(stream: dict[str, Any]) -> str:
    """Return codec type from an ffprobe stream.

    Arguments:
        stream: ffprobe stream object
    Returns:
        codec type
    """
    codec_type = stream.get("codec_type")
    if not isinstance(codec_type, str) or not codec_type:
        codec_type = "unknown"
    return codec_type


def _get_stream_index(stream: dict[str, Any]) -> int | None:
    """Return usable stream index from an ffprobe stream.

    Arguments:
        stream: ffprobe stream object
    Returns:
        absolute media stream index, if present and nonnegative
    """
    stream_index_value = stream.get("index")
    if stream_index_value is None:
        return None
    try:
        stream_index = int(stream_index_value)
    except (TypeError, ValueError):
        return None
    if stream_index < 0:
        return None
    return stream_index


def _get_language(stream: dict[str, Any]) -> str | None:
    """Return language tag from an ffprobe stream.

    Arguments:
        stream: ffprobe stream object
    Returns:
        language tag, if present
    """
    tags = stream.get("tags")
    if not isinstance(tags, dict):
        return None
    language = tags.get("language")
    if not isinstance(language, str):
        return None
    return language


def _get_title(stream: dict[str, Any]) -> str | None:
    """Return title from an ffprobe stream.

    Arguments:
        stream: ffprobe stream object
    Returns:
        title, if present
    """
    tags = stream.get("tags")
    if not isinstance(tags, dict):
        return None
    title = tags.get("title")
    if not isinstance(title, str):
        return None
    return title
