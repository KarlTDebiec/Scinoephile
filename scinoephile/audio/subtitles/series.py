#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series of subtitles with audio."""

from __future__ import annotations

import re
from logging import getLogger
from os import PathLike
from pathlib import Path
from typing import Any, Self, TypedDict, override

import ffmpeg
from pydub import AudioSegment

from scinoephile.common.file import get_temp_directory_path
from scinoephile.common.validation import (
    val_input_dir_path,
    val_input_path,
    val_output_dir_path,
    val_output_path,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series

from .subtitle import AudioSubtitle

__all__ = [
    "AudioSeries",
    "AudioSeriesLoadKwargs",
]

logger = getLogger(__name__)


class AudioSeriesLoadKwargs(TypedDict, total=False):
    """Keyword arguments for AudioSeries.load() methods."""

    buffer: int
    """Additional buffer to include before and after each subtitle (ms)."""


class AudioSeries(Series):
    """Series of subtitles with audio."""

    event_class = AudioSubtitle
    """Class of individual subtitle events."""
    events: list[AudioSubtitle]
    """Individual subtitle events."""
    block_audio_pattern = re.compile(
        r"^(?P<start_idx>\d{4})-(?P<end_idx>\d{4})_"
        r"(?P<buffered_start>\d{8})-(?P<buffered_end>\d{8})\.wav$"
    )

    """Pattern for block audio files."""
    subtitle_audio_pattern = re.compile(r"^\d{4}_\d{8}-\d{8}\.wav$")
    """Pattern for subtitle audio files."""

    @override
    def __init__(self, audio: AudioSegment, events: list[AudioSubtitle] | None = None):
        """Initialize.

        Arguments:
            audio: Series audio
            events: individual subtitle events
        """
        if audio is None:
            raise ValueError("AudioSeries requires audio")
        super().__init__()
        self._audio = audio
        if events is not None:
            self.events = events
        self._blocks: list[AudioSeries] | None = None
        # Attributes for AudioSeries blocks created by _init_blocks
        self.buffered_start: int | None = None
        self.buffered_end: int | None = None

    @property
    def audio(self) -> AudioSegment:
        """Audio of series."""
        return self._audio

    @audio.setter
    def audio(self, audio: AudioSegment):
        """Set audio of series.

        Arguments:
            audio: Audio of series
        """
        self._audio = audio

    @property
    @override
    def blocks(self) -> list[AudioSeries]:
        """List of blocks in the series.

        For AudioSeries, each returned AudioSeries block includes:
        - buffered_start: Start time of buffered audio (extends before subtitles)
        - buffered_end: End time of buffered audio (extends after subtitles)
        - audio: Buffered audio segment (includes audio beyond subtitle times)

        The buffering provides context audio around subtitle boundaries.
        """
        if self._blocks is None:
            self._init_blocks()
        assert self._blocks is not None
        return self._blocks

    @blocks.setter
    @override
    def blocks(self, blocks: list[AudioSeries]):
        """Set blocks of the series.

        Arguments:
            blocks: List of blocks in the series
        """
        self._blocks = blocks

    @override
    def save(
        self,
        path: str | PathLike[Any],
        encoding: str = "utf-8",
        format_: str | None = None,
        fps: float | None = None,
        errors: str | None = None,
        **kwargs: Any,
    ):
        """Save series to an output file.

        Arguments:
            path: output file path
            encoding: output file encoding
            format_: output file format
            fps: frames per second
            errors: encoding error handling
            **kwargs: additional keyword arguments
        """
        path = Path(path)

        # Check if directory
        if format_ == "wav" or (not format_ and path.suffix == ""):
            validated_output_dir_path = val_output_dir_path(path)
            self._save_wav(validated_output_dir_path)
            logger.info(f"Saved series to {validated_output_dir_path}")
            return

        # Otherwise, continue as superclass
        validated_output_path = val_output_path(path, exist_ok=True)
        super().save(
            validated_output_path,
            encoding=encoding,
            format_=format_,
            fps=fps,
            errors=errors,
            **kwargs,
        )
        logger.info(f"Saved series to {validated_output_path}")

    @override
    def slice(self, start: int, end: int) -> Self:
        """Slice series.

        Arguments:
            start: start index
            end: end index
        Returns:
            new sliced series
        """
        audio = self.audio[self.events[start].start : self.events[end - 1].end]
        sliced = type(self)(audio=audio)
        sliced.events = [
            self.event_class(**event.as_dict()) for event in self.events[start:end]
        ]
        return sliced

    @classmethod
    @override
    def load(
        cls,
        path: str | PathLike[Any],
        encoding: str = "utf-8",
        format_: str | None = None,
        fps: float | None = None,
        errors: str | None = None,
        **kwargs: Any,
    ) -> Self:
        """Load series from a directory of wav files.

        Arguments:
            path : input directory path
            encoding: input file encoding
            format_: input file format
            fps: frames per second
            errors: encoding error handling
            **kwargs: additional keyword arguments
        Returns:
            loaded series
        """
        validated_path = val_input_dir_path(path)
        buffer = kwargs.pop("buffer", 1000)
        validated_srt_path = val_input_path(
            validated_path / f"{validated_path.stem}.srt"
        )
        text_series = Series.load(
            validated_srt_path,
            encoding=encoding,
            format_=format_,
            fps=fps,
            errors=errors,
            **kwargs,
        )

        validated_audio_path = val_input_path(
            validated_path / f"{validated_path.stem}.wav"
        )
        full_audio = AudioSegment.from_wav(validated_audio_path)
        logger.info(f"Loaded full audio from {validated_audio_path}")

        return cls.build_series(text_series, full_audio, buffer)

    @classmethod
    def load_from_media(
        cls,
        media_path: Path | str,
        subtitle_path: Path | str,
        stream_index: int = 0,
        buffer: int = 1000,
        **kwargs: Any,
    ) -> Self:
        """Load series from a subtitle file and associated media file.

        Arguments:
            media_path: path to media file
            subtitle_path: path to subtitle file
            stream_index: audio stream index (zero-based)
            buffer: additional buffer to include before and after subtitles (ms)
            **kwargs: additional keyword arguments passed to Series.load
        Returns:
            loaded series
        """
        validated_media_path = val_input_path(media_path)
        validated_subtitle_path = val_input_path(subtitle_path)
        text_series = Series.load(validated_subtitle_path, **kwargs)

        try:
            probe = ffmpeg.probe(str(validated_media_path))
        except ffmpeg.Error as exc:
            raise ScinoephileError(
                f"Could not probe media file {validated_media_path}"
            ) from exc
        audio_streams = [
            stream
            for stream in probe.get("streams", [])
            if stream.get("codec_type") == "audio"
        ]
        if not audio_streams:
            raise ScinoephileError(
                f"No audio streams found in media file {validated_media_path}"
            )
        if stream_index < 0 or stream_index >= len(audio_streams):
            raise ScinoephileError(
                f"Invalid audio stream index {stream_index} for "
                f"{validated_media_path}; found {len(audio_streams)} audio stream(s)."
            )
        stream = audio_streams[stream_index]
        channels = stream.get("channels")
        try:
            channel_count = int(channels)
        except (TypeError, ValueError) as exc:
            raise ScinoephileError(
                f"Audio stream {stream_index} in {validated_media_path} "
                "cannot be used for transcription."
            ) from exc

        with get_temp_directory_path() as temp_dir_path:
            full_audio_path = temp_dir_path / "full_audio.wav"
            try:
                cls.extract_audio_track(
                    validated_media_path,
                    full_audio_path,
                    stream_index,
                    channel_count,
                )
                logger.info(f"Loading full audio from {full_audio_path}")
                full_audio = AudioSegment.from_wav(full_audio_path)
            except ffmpeg.Error as exc:
                raise ScinoephileError(
                    f"Could not extract audio stream {stream_index} from "
                    f"{validated_media_path}"
                ) from exc

        return cls.build_series(text_series, full_audio, buffer)

    @classmethod
    def build_series(
        cls,
        text_series: Series,
        full_audio: AudioSegment,
        buffer: int,
    ) -> Self:
        """Construct a series from text and full audio.

        Arguments:
            text_series: Series of subtitle events
            full_audio: Full audio segment for the series
            buffer: Additional buffer before and after each subtitle (ms)
        Returns:
            Loaded series with audio clips
        """
        series = cls(audio=full_audio)
        series.format = "wav"

        events = []
        for i, event in enumerate(text_series, 1):
            original_start = event.start
            original_end = event.end

            # Previous and next events
            prev_event = text_series[i - 2] if i > 1 else None
            next_event = text_series[i] if i < len(text_series) else None

            # Determine buffered start
            if prev_event:
                max_start = original_start - buffer
                midpoint = (original_start + prev_event.end) // 2
                start_time = max(midpoint, max_start)
            else:
                start_time = max(0, original_start - buffer)

            # Determine buffered end
            if next_event:
                min_end = original_end + buffer
                midpoint = (original_end + next_event.start) // 2
                end_time = min(midpoint, min_end)
            else:
                end_time = min(len(full_audio), original_end + buffer)

            logger.debug(f"Slicing audio for subtitle {i} ({start_time} - {end_time})")
            clip = full_audio[start_time:end_time]
            events.append(
                cls.event_class(
                    start=original_start,
                    end=original_end,
                    audio=clip,
                    text=event.text,
                )
            )
        series.events = events

        return series

    @staticmethod
    def extract_audio_track(
        video_input_path: Path,
        audio_output_path: Path,
        audio_track: int,
        channels: int,
    ):
        """Extract a mono audio track from a video file.

        Arguments:
            video_input_path: Path to input video file
            audio_output_path: Path to output audio file
            audio_track: Audio track (zero-indexed)
            channels: Number of channels in audio track
        """
        if channels >= 6:
            logger.info(
                "Extracting center channel of audio stream "
                f"{audio_track} from {video_input_path} to {audio_output_path}"
            )
            ffmpeg.input(str(video_input_path)).output(
                str(audio_output_path),
                format="wav",
                ar=16000,
                **{
                    "filter_complex": f"[0:a:{audio_track}]pan=mono|c0=c2[out]",
                    "map": "[out]",
                },
            ).run(quiet=False, overwrite_output=True)
        else:
            logger.info(
                f"Downmixing audio stream {audio_track} from {video_input_path} to "
                f"{audio_output_path}"
            )
            ffmpeg.input(str(video_input_path)).output(
                str(audio_output_path),
                format="wav",
                ar=16000,
                map=f"0:a:{audio_track}",
                ac=1,
            ).run(quiet=False, overwrite_output=True)

    @override
    def _init_blocks(self):
        """Initialize blocks."""
        # First get the basic block indexes
        block_indexes = Series.get_block_indexes_by_pause(self)

        # Calculate buffered times and create series for each block
        blocks = []
        for i, (start_idx, end_idx) in enumerate(block_indexes):
            block_start_time = self.events[start_idx].start
            block_end_time = self.events[end_idx - 1].end

            # Buffer start
            if i == 0:
                buffered_start = max(0, block_start_time - 1000)
            else:
                prev_end = self.events[block_indexes[i - 1][1] - 1].end
                max_unbuffered_end = (prev_end + block_start_time) // 2
                buffered_start = max(max_unbuffered_end, block_start_time - 1000)

            # Buffer end
            if i < len(block_indexes) - 1:
                next_start = self.events[block_indexes[i + 1][0]].start
                min_unbuffered_start = (block_end_time + next_start) // 2
                buffered_end = min(block_end_time + 1000, min_unbuffered_start)
            else:
                buffered_end = min(len(self.audio), block_end_time + 1000)

            # Slice audio
            logger.debug(
                f"Slicing audio for block {block_start_time}-{block_end_time} "
                f"({buffered_start} - {buffered_end})"
            )
            block_audio = self.audio[buffered_start:buffered_end]

            # Create AudioSeries block
            block = self.slice(start_idx, end_idx)
            # Store buffered timing information as attributes
            block.buffered_start = buffered_start
            block.buffered_end = buffered_end
            # Override the audio with the buffered version
            block.audio = block_audio

            blocks.append(block)

        self._blocks = blocks

    def _save_wav(self, output_dir_path: Path):
        """Save series to directory of wav files.

        Arguments:
            output_dir_path: path to output directory
        """
        # Prepare empty directory, deleting existing files if needed
        if output_dir_path.exists() and output_dir_path.is_dir():
            for file in output_dir_path.iterdir():
                if file.is_file() or file.is_symlink():
                    file.unlink()
                    logger.info(f"Deleted {file}")
        else:
            output_dir_path.mkdir(parents=True)
            logger.info(f"Created directory {output_dir_path}")

        # Save audio
        outfile_path = output_dir_path / f"{output_dir_path.stem}.wav"
        self.audio.export(outfile_path, format="wav")
        logger.info(f"Saved full audio to {outfile_path}")

        # Calculate block indices and save block audio
        current_idx = 0
        for block in self.blocks:
            start_idx = current_idx
            end_idx = current_idx + len(block)
            current_idx = end_idx

            outfile_path = (
                output_dir_path / f"{start_idx + 1:04d}-{end_idx:04d}_"
                f"{block.buffered_start:08d}-{block.buffered_end:08d}.wav"
            )
            block.audio.export(outfile_path, format="wav")
            logger.info(f"Saved block audio to {outfile_path}")

        # Save text
        outfile_path = output_dir_path / f"{output_dir_path.stem}.srt"
        super().save(outfile_path, format_="srt")
