#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series of subtitles with audio."""

from __future__ import annotations

import re
from logging import debug, info
from pathlib import Path
from typing import Any, Self, override
from warnings import catch_warnings, filterwarnings

import ffmpeg
from pysubs2 import SSAFile

with catch_warnings():
    filterwarnings("ignore", category=SyntaxWarning)
    filterwarnings("ignore", category=RuntimeWarning)
    from pydub import AudioSegment


from scinoephile.audio.audio_block import AudioBlock
from scinoephile.audio.audio_subtitle import AudioSubtitle
from scinoephile.common import DirectoryNotFoundError, NotAFileError
from scinoephile.common.file import get_temp_directory_path
from scinoephile.common.validation import (
    val_input_dir_path,
    val_input_path,
    val_output_dir_path,
    val_output_path,
)
from scinoephile.core import ScinoephileError, Series
from scinoephile.core.block import Block
from scinoephile.core.blocks import get_block_indexes_by_pause


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
    def __init__(self, audio: AudioSegment | None = None):
        """Initialize.

        Arguments:
            audio: Series audio
        """
        super().__init__()

        self._audio = audio

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
    def blocks(self) -> list[AudioBlock]:
        """List of blocks in the series."""
        if self._blocks is None:
            self._init_blocks()
        return self._blocks

    @blocks.setter
    @override
    def blocks(self, blocks: list[AudioBlock]):
        """Set blocks of the series.

        Arguments:
            blocks: List of blocks in the series
        """
        self._blocks = blocks

    @override
    def save(self, path: str, format_: str | None = None, **kwargs: Any):
        """Save series to an output file.

        Arguments:
            path: Output file path
            format_: Output file format
            **kwargs: Additional keyword arguments
        """
        path = Path(path)

        # Check if directory
        if format_ == "wav" or (not format_ and path.suffix == ""):
            path = val_output_dir_path(path)
            self._save_wav(path, **kwargs)
            info(f"Saved series to {path}")
            return

        # Otherwise, continue as superclass SSAFile
        path = val_output_path(path, exist_ok=True)
        SSAFile.save(self, path, format_=format_, **kwargs)
        info(f"Saved series to {path}")

    @override
    def slice(self, start_idx: int, end_idx: int) -> Self:
        """Slice series.

        Arguments:
            start_idx: Start index of slice
            end_idx: End index of slice
        Returns:
            New sliced series
        """
        sliced = super().slice(start_idx, end_idx)
        sliced.audio = self.audio[self[start_idx].start : self[end_idx - 1].end]
        return sliced

    @override
    def _init_blocks(self):
        """Initialize blocks."""
        blocks = [
            Block(self, start_idx, end_idx)
            for start_idx, end_idx in get_block_indexes_by_pause(self)
        ]
        audio_blocks = []
        for i, block in enumerate(blocks):
            # Buffer start
            if i == 0:
                buffered_start = max(0, block.start - 1000)
            else:
                max_unbuffered_end = (blocks[i - 1].end + block.start) // 2
                buffered_start = max(max_unbuffered_end, block.start - 1000)

            # Buffer end
            if i < len(blocks) - 1:
                min_unbuffered_start = (block.end + blocks[i + 1].start) // 2
                buffered_end = min(block.end + 1000, min_unbuffered_start)
            else:
                buffered_end = min(len(self.audio), block.end + 1000)

            # Slice audio
            debug(
                f"Slicing audio for block {block.start}-{block.end} "
                f"({buffered_start} - {buffered_end})"
            )
            audio = self.audio[buffered_start:buffered_end]

            # Create Audio Block
            audio_block = AudioBlock(
                series=self,
                start_idx=block.start_idx,
                end_idx=block.end_idx,
                buffered_start=buffered_start,
                buffered_end=buffered_end,
                audio=audio,
            )
            audio_blocks.append(audio_block)
        self._blocks = audio_blocks

    def _save_wav(self, fp: Path, **kwargs: Any):
        """Save series to directory of wav files.

        Arguments:
            fp: Path to outpt directory
            **kwargs: Additional keyword arguments
        """
        # Prepare empty directory, deleting existing files if needed
        if fp.exists() and fp.is_dir():
            for file in fp.iterdir():
                if file.is_file() or file.is_symlink():
                    file.unlink()
                    info(f"Deleted {file}")
        else:
            fp.mkdir(parents=True)
            info(f"Created directory {fp}")

        # Save audio
        outfile_path = fp / f"{fp.stem}.wav"
        self.audio.export(outfile_path, format="wav")
        info(f"Saved full audio to {outfile_path}")
        for block in self.blocks:
            outfile_path = (
                fp / f"{block.start_idx + 1:04d}-{block.end_idx:04d}_"
                f"{block.buffered_start:08d}-{block.buffered_end:08d}.wav"
            )
            block.audio.export(outfile_path, format="wav")
            info(f"Saved block audio to {outfile_path}")

        # Save text
        outfile_path = fp / f"{fp.stem}.srt"
        super().save(outfile_path, format_="srt")

    @classmethod
    @override
    def load(
        cls,
        path: Path | str,
        encoding: str = "utf-8",
        format_: str | None = None,
        **kwargs: Any,
    ) -> Self:
        """Load series from an input file.

        Arguments:
            path : Input file path
            encoding: Input file encoding
            format_: Input file format
            **kwargs: Additional keyword arguments
        Returns:
            Loaded series
        """
        try:
            validated_path = val_input_dir_path(path)
            return cls._load_wav(validated_path, **kwargs)
        except (DirectoryNotFoundError, NotADirectoryError):
            try:
                validated_path = val_input_path(path)
                video_path = kwargs.pop("video_path", None)
                validated_video_path = val_input_path(video_path)
                return cls._load_video(
                    subtitle_path=validated_path,
                    video_path=validated_video_path,
                    **kwargs,
                )
            except (FileNotFoundError, KeyError, NotAFileError) as exc:
                raise ValueError(
                    f"{cls.__name__}'s path must be either path to a directory "
                    "containing one srt file containing N subtitles and N wav files, "
                    "or path to an srt file with a separate video file provided as the "
                    "argument 'video_path'.",
                ) from exc

    @classmethod
    def _build_series(
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
        series = cls()
        series.format = "wav"
        series.audio = full_audio

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

            debug(f"Slicing audio for subtitle {i} ({start_time} - {end_time})")
            clip = full_audio[start_time:end_time]
            series.events.append(
                cls.event_class(
                    start=original_start,
                    end=original_end,
                    audio=clip,
                    text=event.text,
                    series=series,
                )
            )

        return series

    @classmethod
    def _load_video(
        cls,
        subtitle_path: Path,
        video_path: Path,
        audio_track: int = 0,
        buffer=1000,
        **kwargs: Any,
    ) -> Self:
        """Load series from a subtitle file and associated video file.

        Arguments:
            subtitle_path: Path to subtitle file
            video_path: Path to video file
            audio_track: Audio track (zero-indexed)
            buffer: Additional buffer to include before and after subtitles (ms)
            **kwargs: Additional keyword arguments
        Returns:
            Loaded series
        """
        # Load text
        text_series = Series.load(subtitle_path)

        # Probe audio track to determine number of channels
        info(f"Probing audio track {audio_track} in {video_path}")
        probe = ffmpeg.probe(str(video_path))
        audio_streams = [s for s in probe["streams"] if s["codec_type"] == "audio"]
        try:
            stream = audio_streams[audio_track]
            channels = int(stream["channels"])
            info(f"Audio track has {channels} channels")
        except (IndexError, KeyError, ValueError) as exc:
            raise ScinoephileError(
                f"Could not determine number of channels for audio track {audio_track} "
                f"in {video_path}"
            ) from exc

        # Load full audio from video
        with get_temp_directory_path() as temp_dir_path:
            full_audio_path = temp_dir_path / "full_audio.wav"
            cls._extract_audio_track(video_path, full_audio_path, audio_track, channels)
            info(f"Loading full audio from {full_audio_path}")
            full_audio = AudioSegment.from_wav(full_audio_path)

        return cls._build_series(text_series, full_audio, buffer)

    @classmethod
    def _load_wav(cls, dir_path: Path, buffer=1000, **kwargs: Any) -> Self:
        """Load series from a directory of wav files.

        Arguments:
            dir_path: Path to input directory
            buffer: Additional buffer to include before and after subtitles (ms)
            **kwargs: Additional keyword arguments
        Returns:
            Loaded series
        """
        # Load text
        srt_path = dir_path / f"{dir_path.stem}.srt"
        text_series = Series.load(srt_path)

        # Load full audio file
        audio_path = dir_path / f"{dir_path.stem}.wav"
        full_audio = AudioSegment.from_wav(audio_path)
        info(f"Loaded full audio from {audio_path}")

        return cls._build_series(text_series, full_audio, buffer)

    @staticmethod
    def _extract_audio_track(
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
            info(
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
            info(
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
