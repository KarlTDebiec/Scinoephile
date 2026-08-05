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
    """Channel and sample-rate preparation used during audio extraction."""

    TRANSCRIPTION = "transcription"
    """Prepare the current transcription input: mono at 16 kHz."""
    NATIVE_CENTER = "native-center"
    """Preserve the source sample rate and extract only the center channel."""
    NATIVE_CENTER_HEAVY = "native-center-heavy"
    """Preserve the source sample rate and mix center with quieter front channels."""
    NATIVE_MONO = "native-mono"
    """Preserve the source sample rate and downmix the complete stream to mono."""
    NATIVE_STEREO = "native-stereo"
    """Preserve the source sample rate and downmix the complete stream to stereo."""


def extract_audio(
    infile_path: Path,
    outfile_path: Path,
    *,
    stream_index: int | None = None,
    mode: AudioExtractionMode = AudioExtractionMode.TRANSCRIPTION,
    overwrite: bool = False,
) -> AudioStream:
    """Extract and prepare a selected audio stream as a WAV file.

    The default mode extracts a transcription-ready mono 16-kHz signal. Native-rate
    modes preserve the source sample rate while selecting or mixing channels.

    Arguments:
        infile_path: media input file
        outfile_path: WAV output file
        stream_index: absolute media stream index, or None for the first audio stream
        mode: channel and sample-rate preparation mode
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
    if stream.channels is None:
        raise ScinoephileError(
            f"Audio stream {stream.index} in {validated_infile_path} has no "
            "channel count"
        )
    _extract_audio_track(
        validated_infile_path,
        validated_outfile_path,
        stream.index,
        stream.channels,
        mode,
    )
    return stream


def _extract_audio_track(
    infile_path: Path,
    outfile_path: Path,
    stream_index: int,
    channels: int,
    mode: AudioExtractionMode,
):
    """Extract a known media audio stream using the selected preparation mode.

    Arguments:
        infile_path: media input file
        outfile_path: WAV output file
        stream_index: absolute media stream index
        channels: number of channels in the selected stream
        mode: channel and sample-rate preparation mode
    Raises:
        ScinoephileError: if ffmpeg cannot extract the stream
    """
    try:
        if mode is AudioExtractionMode.TRANSCRIPTION and channels >= 6:
            logger.info(
                f"Extracting center channel of audio stream {stream_index} from "
                f"{infile_path} to {outfile_path}"
            )
            ffmpeg.input(str(infile_path)).output(
                str(outfile_path),
                format="wav",
                ar=16000,
                **{
                    "filter_complex": f"[0:{stream_index}]pan=mono|c0=c2[out]",
                    "map": "[out]",
                },
            ).run(quiet=False, overwrite_output=True)
        elif mode is AudioExtractionMode.TRANSCRIPTION:
            logger.info(
                f"Downmixing audio stream {stream_index} from {infile_path} to "
                f"{outfile_path}"
            )
            ffmpeg.input(str(infile_path)).output(
                str(outfile_path), format="wav", ar=16000, map=f"0:{stream_index}", ac=1
            ).run(quiet=False, overwrite_output=True)
        elif mode is AudioExtractionMode.NATIVE_CENTER:
            logger.info(
                f"Extracting native-rate center channel of audio stream "
                f"{stream_index} from {infile_path} to {outfile_path}"
            )
            ffmpeg.input(str(infile_path)).output(
                str(outfile_path),
                format="wav",
                **{
                    "filter_complex": (
                        f"[0:{stream_index}]channelmap=map=FC:channel_layout=mono[out]"
                    ),
                    "map": "[out]",
                },
            ).run(quiet=False, overwrite_output=True)
        elif mode is AudioExtractionMode.NATIVE_CENTER_HEAVY:
            logger.info(
                f"Extracting native-rate center-heavy mix of audio stream "
                f"{stream_index} from {infile_path} to {outfile_path}"
            )
            ffmpeg.input(str(infile_path)).output(
                str(outfile_path),
                format="wav",
                **{
                    "filter_complex": (
                        f"[0:{stream_index}]"
                        "channelmap=map=FL|FR|FC:channel_layout=3.0,"
                        "pan=mono|c0=0.15*c0+0.15*c1+0.70*c2[out]"
                    ),
                    "map": "[out]",
                },
            ).run(quiet=False, overwrite_output=True)
        elif mode is AudioExtractionMode.NATIVE_MONO:
            logger.info(
                f"Downmixing complete audio stream {stream_index} to native-rate "
                f"mono from {infile_path} to {outfile_path}"
            )
            ffmpeg.input(str(infile_path)).output(
                str(outfile_path), format="wav", map=f"0:{stream_index}", ac=1
            ).run(quiet=False, overwrite_output=True)
        else:
            logger.info(
                f"Downmixing complete audio stream {stream_index} to native-rate "
                f"stereo from {infile_path} to {outfile_path}"
            )
            ffmpeg.input(str(infile_path)).output(
                str(outfile_path), format="wav", map=f"0:{stream_index}", ac=2
            ).run(quiet=False, overwrite_output=True)
    except ffmpeg.Error as exc:
        if mode is AudioExtractionMode.NATIVE_CENTER:
            raise ScinoephileError(
                f"Could not extract audio stream {stream_index} from {infile_path} "
                f"to {outfile_path}; mode {mode.value} requires a front center "
                "(FC) channel"
            ) from exc
        if mode is AudioExtractionMode.NATIVE_CENTER_HEAVY:
            raise ScinoephileError(
                f"Could not extract audio stream {stream_index} from {infile_path} "
                f"to {outfile_path}; mode {mode.value} requires front left (FL), "
                "front right (FR), and front center (FC) channels"
            ) from exc
        raise ScinoephileError(
            f"Could not extract audio stream {stream_index} from {infile_path} "
            f"to {outfile_path}"
        ) from exc
    except OSError as exc:
        raise ScinoephileError(
            f"Could not extract audio stream {stream_index} from {infile_path} "
            f"to {outfile_path}"
        ) from exc
