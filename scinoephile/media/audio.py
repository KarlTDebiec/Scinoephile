#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audio stream selection and extraction utilities."""

from __future__ import annotations

from enum import StrEnum
from logging import getLogger
from pathlib import Path

import ffmpeg

from scinoephile.common.validation import val_input_path, val_output_path
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.media.audio_stream import AudioStream

from .probe import get_streams

__all__ = ["AudioExtractionMode", "extract_audio"]

logger = getLogger(__name__)


class AudioExtractionMode(StrEnum):
    """Channel preparation used during audio extraction."""

    ORIGINAL = "original"
    """Preserve the source sample rate and channel layout."""
    CENTER = "center"
    """Preserve the source sample rate and extract only the center channel."""
    CENTER_HEAVY = "center-heavy"
    """Preserve the source sample rate and mix center with quieter front channels."""
    MONO = "mono"
    """Preserve the source sample rate and downmix the complete stream to mono."""
    STEREO = "stereo"
    """Preserve the source sample rate and downmix the complete stream to stereo."""


def extract_audio(
    infile_path: Path,
    outfile_path: Path,
    *,
    stream_index: int | None = None,
    mode: AudioExtractionMode = AudioExtractionMode.ORIGINAL,
    overwrite: bool = False,
) -> AudioStream:
    """Extract and prepare a selected audio stream as a WAV file.

    The default mode preserves the source sample rate and channel layout. Other modes
    preserve the source sample rate while selecting or mixing channels.

    Arguments:
        infile_path: media input file
        outfile_path: WAV output file
        stream_index: absolute media stream index, or None for the first audio stream
        mode: channel preparation mode
        overwrite: whether to overwrite an existing output file
    Returns:
        selected audio stream metadata
    Raises:
        ScinoephileError: if paths, stream selection, or extraction are invalid
    """
    try:
        validated_infile_path = val_input_path(infile_path)
        validated_outfile_path = val_output_path(outfile_path, exist_ok=True)
    except (OSError, TypeError, ValueError) as exc:
        raise ScinoephileError(f"Unable to extract audio: {exc}") from exc

    if validated_outfile_path.suffix.lower() != ".wav":
        raise ScinoephileError("Audio outfile must have a .wav extension")
    if validated_infile_path == validated_outfile_path:
        raise ScinoephileError("Audio infile and outfile must be different files")
    if validated_outfile_path.exists() and not overwrite:
        raise ScinoephileError(
            f"Audio outfile already exists: {validated_outfile_path}; "
            "use --overwrite to replace it"
        )

    stream: AudioStream | None = None
    for candidate in get_streams(validated_infile_path):
        if stream_index is None:
            if isinstance(candidate, AudioStream):
                stream = candidate
                break
            continue
        if candidate.index != stream_index:
            continue
        if not isinstance(candidate, AudioStream):
            raise ScinoephileError(
                f"Stream index {stream_index} is not an audio stream"
            )
        stream = candidate
        break

    if stream is None:
        if stream_index is None:
            raise ScinoephileError(f"No audio streams found in {validated_infile_path}")
        raise ScinoephileError(
            f"No stream index {stream_index} found in {validated_infile_path}"
        )
    _extract_audio_track(
        validated_infile_path, validated_outfile_path, stream.index, mode
    )
    return stream


def _extract_audio_track(
    infile_path: Path, outfile_path: Path, stream_index: int, mode: AudioExtractionMode
):
    """Extract a known media audio stream using the selected preparation mode.

    Arguments:
        infile_path: media input file
        outfile_path: WAV output file
        stream_index: absolute media stream index
        mode: channel preparation mode
    Raises:
        ScinoephileError: if ffmpeg cannot extract the stream
    """
    output_kwargs: dict[str, object] = {"format": "wav"}
    required_channels: str | None = None
    if mode is AudioExtractionMode.ORIGINAL:
        operation = f"Extracting original audio stream {stream_index}"
        output_kwargs["map"] = f"0:{stream_index}"
    elif mode is AudioExtractionMode.CENTER:
        operation = (
            f"Extracting native-rate center channel of audio stream {stream_index}"
        )
        required_channels = "a front center (FC) channel"
        output_kwargs.update(
            filter_complex=(
                f"[0:{stream_index}]channelmap=map=FC:channel_layout=mono[out]"
            ),
            map="[out]",
        )
    elif mode is AudioExtractionMode.CENTER_HEAVY:
        operation = (
            f"Extracting native-rate center-heavy mix of audio stream {stream_index}"
        )
        required_channels = (
            "front left (FL), front right (FR), and front center (FC) channels"
        )
        output_kwargs.update(
            filter_complex=(
                f"[0:{stream_index}]"
                "channelmap=map=FL|FR|FC:channel_layout=3.0,"
                "pan=mono|c0=0.15*c0+0.15*c1+0.70*c2[out]"
            ),
            map="[out]",
        )
    else:
        output_channels = 1
        if mode is AudioExtractionMode.STEREO:
            output_channels = 2
        operation = (
            f"Downmixing complete audio stream {stream_index} to native-rate "
            f"{mode.value}"
        )
        output_kwargs.update(map=f"0:{stream_index}", ac=output_channels)

    logger.info(f"{operation} from {infile_path} to {outfile_path}")
    try:
        ffmpeg.input(str(infile_path)).output(str(outfile_path), **output_kwargs).run(
            quiet=False, overwrite_output=True
        )
    except (ffmpeg.Error, OSError) as exc:
        message = (
            f"Could not extract audio stream {stream_index} from {infile_path} "
            f"to {outfile_path}"
        )
        if isinstance(exc, ffmpeg.Error) and required_channels is not None:
            message = f"{message}; mode {mode.value} requires {required_channels}"
        raise ScinoephileError(message) from exc
