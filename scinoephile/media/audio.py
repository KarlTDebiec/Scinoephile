#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audio stream selection and extraction utilities."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path

import ffmpeg

from scinoephile.common.validation import val_input_path, val_output_path
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.media.audio_stream import AudioStream

from .probe import get_streams

__all__ = ["extract_audio"]

logger = getLogger(__name__)


def extract_audio(
    infile_path: Path,
    outfile_path: Path,
    *,
    stream_index: int | None = None,
    overwrite: bool = False,
) -> AudioStream:
    """Extract a selected audio stream as a transcription-ready mono WAV file.

    Multichannel streams with a center channel use that channel; other streams are
    downmixed to mono. Output is sampled at 16 kHz.

    Arguments:
        infile_path: media input file
        outfile_path: WAV output file
        stream_index: absolute media stream index, or None for the first audio stream
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
    )
    return stream


def _extract_audio_track(
    infile_path: Path,
    outfile_path: Path,
    stream_index: int,
    channels: int,
):
    """Extract a known media audio stream as a mono 16 kHz WAV file.

    Arguments:
        infile_path: media input file
        outfile_path: WAV output file
        stream_index: absolute media stream index
        channels: number of channels in the selected stream
    Raises:
        ScinoephileError: if ffmpeg cannot extract the stream
    """
    try:
        if channels >= 6:
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
        else:
            logger.info(
                f"Downmixing audio stream {stream_index} from {infile_path} to "
                f"{outfile_path}"
            )
            ffmpeg.input(str(infile_path)).output(
                str(outfile_path),
                format="wav",
                ar=16000,
                map=f"0:{stream_index}",
                ac=1,
            ).run(quiet=False, overwrite_output=True)
    except (ffmpeg.Error, OSError) as exc:
        raise ScinoephileError(
            f"Could not extract audio stream {stream_index} from {infile_path} "
            f"to {outfile_path}"
        ) from exc
