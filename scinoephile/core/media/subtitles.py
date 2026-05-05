#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle extraction from media files."""

from __future__ import annotations

from pathlib import Path

import ffmpeg

from scinoephile.core.exceptions import ScinoephileError

from .constants import DEFAULT_SUBTITLE_LANGUAGES
from .subtitle_stream import SubtitleStream

__all__ = [
    "extract_subtitle_stream",
    "extract_subtitles",
    "get_subtitle_output_path",
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


def extract_subtitles(
    infile_path: Path,
    output_dir_path: Path,
    languages: list[str] | tuple[str, ...] = DEFAULT_SUBTITLE_LANGUAGES,
) -> list[Path]:
    """Extract subtitle streams whose language tags match requested ISO codes.

    Arguments:
        infile_path: video input file containing subtitle streams
        output_dir_path: directory to which matching subtitle streams will be extracted
        languages: ISO 639 language codes to extract
    Returns:
        output paths created by this call
    Raises:
        ScinoephileError: if ffprobe or ffmpeg fails
    """
    language_codes = {language.lower() for language in languages}

    extracted_paths = []
    for stream in get_subtitle_streams(infile_path):
        if stream.language is None or stream.language.lower() not in language_codes:
            continue

        outfile_path = get_subtitle_output_path(output_dir_path, stream)
        if outfile_path.exists():
            continue

        extracted_paths.append(
            extract_subtitle_stream(infile_path, stream, outfile_path)
        )

    return extracted_paths


def get_subtitle_output_path(
    output_dir_path: Path,
    stream: SubtitleStream,
) -> Path:
    """Get the output path for an extracted subtitle stream.

    Arguments:
        output_dir_path: directory to which matching subtitles will be extracted
        stream: subtitle stream to extract
    Returns:
        subtitle output path
    Raises:
        ValueError: if the stream has no language tag
    """
    if stream.language is None:
        raise ValueError("Subtitle stream must have a language to build output path")
    filename = f"{stream.language}-{stream.index}.{stream.extension}"
    return Path(output_dir_path) / filename


def get_subtitle_streams(
    infile_path: Path, counts: bool = False
) -> list[SubtitleStream]:
    """Return subtitle streams in a media file.

    Arguments:
        infile_path: media input file to inspect
        counts: whether to include subtitle packet counts
    Returns:
        subtitle stream metadata
    Raises:
        ScinoephileError: if ffprobe fails
    """
    try:
        if counts:
            probe = ffmpeg.probe(str(infile_path), count_packets=None)
        else:
            probe = ffmpeg.probe(str(infile_path))
    except ffmpeg.Error as exc:
        raise ScinoephileError(f"Could not probe media file {infile_path}") from exc

    subtitle_streams = []
    for stream in probe.get("streams", []):
        if not isinstance(stream, dict):
            continue
        subtitle_stream = SubtitleStream.from_ffprobe_stream(stream)
        if subtitle_stream is not None:
            subtitle_streams.append(subtitle_stream)

    return subtitle_streams
