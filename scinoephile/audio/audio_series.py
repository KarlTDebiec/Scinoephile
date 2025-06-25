#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series of subtitles with audio."""

from __future__ import annotations

import re
from logging import info
from pathlib import Path
from typing import Any

import ffmpeg
from pydub import AudioSegment
from pysubs2 import SSAFile

from scinoephile.audio.audio_subtitle import AudioSubtitle
from scinoephile.common import NotAFileError
from scinoephile.common.file import get_temp_directory_path
from scinoephile.common.validation import (
    validate_input_directory,
    validate_input_file,
    validate_output_directory,
    validate_output_file,
)
from scinoephile.core import ScinoephileException, Series
from scinoephile.core.blocks import get_blocks_by_pause


class AudioSeries(Series):
    """Series of subtitles with audio."""

    event_class = AudioSubtitle
    """Class of individual subtitle events."""
    events: list[AudioSubtitle]
    """Individual subtitle events."""
    block_audio_pattern = re.compile(r"^\d{4}-\d{4}_\d{8}-\d{8}\.wav$")
    """Pattern for block audio files."""
    subtitle_audio_pattern = re.compile(r"^\d{4}_\d{8}-\d{8}\.wav$")
    """Pattern for subtitle audio files."""

    def __init__(self):
        """Initialize."""
        super().__init__()

        self._audio = None
        self._blocks = None
        self._block_audio = None

    @property
    def audio(self) -> AudioSegment:
        """Audio of series."""
        return self._audio

    @audio.setter
    def audio(self, audio: AudioSegment) -> None:
        """Set audio of series.

        Arguments:
            audio: Audio of series
        """
        self._audio = audio

    @property
    def blocks(self) -> list[tuple[int, int, int, int]]:
        """Blocks of audio in series."""
        if self._blocks is None:
            self._init_blocks()
        return self._blocks

    @property
    def block_audio(self) -> list[AudioSegment]:
        """Audio of blocks in series."""
        return self._block_audio

    @block_audio.setter
    def block_audio(self, block_audio: list[AudioSegment]) -> None:
        """Set audio of blocks in series.

        Arguments:
            block_audio: Audio of blocks in series
        """
        self._block_audio = block_audio

    def save(self, path: str, format_: str | None = None, **kwargs: Any) -> None:
        """Save series to an output file.

        Arguments:
            path: Output file path
            format_: Output file format
            **kwargs: Additional keyword arguments
        """
        path = Path(path)

        # Check if directory
        if format_ == "wav" or (not format_ and path.suffix == ""):
            path = validate_output_directory(path)
            self._save_wav(path, **kwargs)
            info(f"Saved series to {path}")
            return

        # Otherwise, continue as superclass SSAFile
        path = validate_output_file(path)
        SSAFile.save(self, path, format_=format_, **kwargs)
        info(f"Saved series to {path}")

    def _save_wav(self, fp: Path, **kwargs: Any) -> None:
        """Save series to directory of wav files.

        Arguments:
            fp: Path to outpt directory
            **kwargs: Additional keyword arguments
        """
        # Prepare empty directory, deleting existing files if needed
        if fp.exists() and fp.is_dir():
            for file in fp.iterdir():
                file.unlink()
                info(f"Deleted {file}")
        else:
            fp.mkdir(parents=True)
            info(f"Created directory {fp}")

        # Save audio
        outfile_path = fp / f"{fp.stem}.wav"
        self.audio.export(outfile_path, format="wav")
        info(f"Saved full audio to {outfile_path}")
        for i, event in enumerate(self.events, 1):
            outfile_path = fp / f"{i:04d}_{event.start:08d}-{event.end:08d}.wav"
            event.aud.export(outfile_path, format="wav")
            info(f"Saved audio to {outfile_path}")
        for block, block_audio in zip(self.blocks, self.block_audio):
            outfile_path = (
                fp / f"{block[0]:04d}-{block[1]:04d}_{block[2]:08d}-{block[3]:08d}.wav"
            )
            block_audio.export(outfile_path, format="wav")
            info(f"Saved block audio to {outfile_path}")

        # Save text
        outfile_path = fp / f"{fp.stem}.srt"
        super().save(outfile_path, format_="srt")

    @classmethod
    def load(
        cls,
        path: str,
        encoding: str = "utf-8",
        format_: str | None = None,
        **kwargs: Any,
    ) -> AudioSeries:
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
            validated_path = validate_input_directory(path)
            return cls._load_wav(validated_path, **kwargs)
        except NotADirectoryError as exc:
            try:
                validated_path = validate_input_file(path)
                video_path = kwargs.pop("video_path", None)
                validated_video_path = validate_input_file(video_path)
                return cls._load_video(
                    fp=validated_path,
                    video_fp=validated_video_path,
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
    def _load_video(
        cls, fp: Path, video_fp: Path, audio_track: int = 0, buffer=1000, **kwargs: Any
    ) -> AudioSeries:
        """Load series from a subtitle file and associated video file.

        Arguments:
            fp: Path to subtitle file
            video_fp: Path to video file
            audio_track: Audio track (zero-indexed)
            buffer: Additional buffer to include before and after subtitles (ms)
            **kwargs: Additional keyword arguments
        Returns:
            Loaded series
        """
        series = cls()
        series.format = "wav"

        # Load text
        text_series = Series.load(fp)

        # Probe audio track to determine number of channels
        info(f"Probing audio track {audio_track} in {video_fp}")
        probe = ffmpeg.probe(str(video_fp))
        audio_streams = [s for s in probe["streams"] if s["codec_type"] == "audio"]
        try:
            stream = audio_streams[audio_track]
            channels = int(stream["channels"])
            info(f"Audio track has {channels} channels")
        except (IndexError, KeyError, ValueError) as exc:
            raise ScinoephileException(
                f"Could not determine number of channels for audio track {audio_track} "
                f"in {video_fp}"
            ) from exc

        # Load full audio from video
        with get_temp_directory_path() as temp_dir:
            full_audio_path = temp_dir / "full_audio.wav"
            if channels >= 6:
                info(
                    f"Extracting center channel of audio stream {audio_track} "
                    f"from {video_fp} to {full_audio_path}"
                )
                (
                    ffmpeg.input(
                        str(video_fp),
                    )
                    .output(
                        str(full_audio_path),
                        format="wav",
                        ar=16000,
                        **{
                            "filter_complex": f"[0:a:{audio_track}]pan=mono|c0=c2[out]",
                            "map": "[out]",
                        },
                    )
                    .run(
                        quiet=False,
                        overwrite_output=True,
                    )
                )
            else:
                info(
                    f"Downmixing audio stream {audio_track} "
                    f"from {video_fp} to {full_audio_path}"
                )
                ffmpeg.input(
                    str(video_fp),
                ).output(
                    str(full_audio_path),
                    format="wav",
                    ar=16000,
                    map=f"0:a:{audio_track}",
                    ac=1,
                ).run(
                    quiet=False,
                    overwrite_output=True,
                )

            # Load full audio as AudioSegment
            info(f"Loading full audio from {full_audio_path}")
            full_audio = AudioSegment.from_wav(full_audio_path)
            series.audio = full_audio

        # Slice and build series
        for i, event in enumerate(text_series, 1):
            original_start = event.start
            original_end = event.end

            # Previous and next events (may be None at boundaries)
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

            info(f"Slicing audio for subtitle {i} ({start_time} - {end_time})")
            clip = full_audio[start_time:end_time]
            series.events.append(
                cls.event_class(
                    start=original_start,
                    end=original_end,
                    aud=clip,
                    text=event.text,
                    series=series,
                )
            )

        # Slice block audio
        block_audio = []
        for i, (start_idx, end_idx, start_ms, end_ms) in enumerate(series.blocks):
            # Determine buffered start
            if i > 0:
                _, _, prev_start, prev_end = series.blocks[i - 1]
                max_start = start_ms - buffer
                midpoint = (start_ms + prev_end) // 2
                buffered_start = max(midpoint, max_start)
            else:
                buffered_start = max(0, start_ms - buffer)

            # Determine buffered end
            if i + 1 < len(series.blocks):
                _, _, next_start, next_end = series.blocks[i + 1]
                min_end = end_ms + buffer
                midpoint = (end_ms + next_start) // 2
                buffered_end = min(midpoint, min_end)
            else:
                buffered_end = min(len(full_audio), end_ms + buffer)

            info(
                f"Slicing audio for block {start_idx}-{end_idx} "
                f"({buffered_start} - {buffered_end})"
            )
            block_clip = full_audio[buffered_start:buffered_end]
            block_audio.append(block_clip)
        series.block_audio = block_audio

        return series

    @classmethod
    def _load_wav(cls, fp: Path, **kwargs: Any) -> AudioSeries:
        """Load series from a directory of wav files.

        Arguments:
            fp: Path to input directory
            **kwargs: Additional keyword arguments
        Returns:
            Loaded series
        """
        series = cls()
        series.format = "wav"

        # Load text
        srt_path = fp / f"{fp.stem}.srt"
        text_series = Series.load(srt_path)

        # Load full audio file
        audio_path = fp / f"{fp.stem}.wav"
        if audio_path.exists():
            series.audio = AudioSegment.from_wav(audio_path)
            info(f"Loaded full audio from {audio_path}")

        # Load subtitle audio files
        infiles = sorted(
            path
            for path in fp.iterdir()
            if path.suffix == ".wav" and cls.subtitle_audio_pattern.match(path.name)
        )
        if len(text_series) != len(infiles):
            raise ScinoephileException(
                f"Number of audio files in {fp} ({len(series)}) "
                f"does not match number of subtitles in {srt_path} "
                f"({len(text_series)})"
            )
        for text_event, infile in zip(text_series, infiles):
            audio = AudioSegment.from_wav(infile)
            series.events.append(
                cls.event_class(
                    start=text_event.start,
                    end=text_event.end,
                    aud=audio,
                    text=text_event.text,
                    series=series,
                )
            )

        # Load block audio files
        infiles = sorted(
            path
            for path in fp.iterdir()
            if path.suffix == ".wav" and cls.block_audio_pattern.match(path.name)
        )
        if len(series.blocks) != len(infiles):
            raise ScinoephileException(
                f"Number of block audio files in {fp} ({len(infiles)}) "
                f"does not match number of blocks in series ({len(series.blocks)})"
            )
        block_audio = []
        for infile, (start_idx, end_idx, start_ms, end_ms) in zip(
            infiles, series.blocks
        ):
            audio = AudioSegment.from_wav(infile)
            block_audio.append(audio)
        series.block_audio = block_audio

        return series

    def _init_blocks(self) -> None:
        """Initialize blocks of audio in series."""
        blocks_series = get_blocks_by_pause(self)
        blocks = []
        i = 1
        for block in blocks_series:
            start = i
            end = i + len(block.events) - 1
            start_time = block.events[0].start
            end_time = block.events[-1].end
            i += len(block.events)
            blocks.append((start, end, start_time, end_time))
        self._blocks = blocks
