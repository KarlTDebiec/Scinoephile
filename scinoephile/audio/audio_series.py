# Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series of subtitles with audio clips."""
from __future__ import annotations

from logging import info
from pathlib import Path
from typing import Any

from pydub import AudioSegment

from scinoephile.audio.audio_subtitle import AudioSubtitle
from scinoephile.common.validation import (
    validate_input_file,
    validate_output_directory,
    validate_output_file,
)
from scinoephile.core import Series


class AudioSubtitleSeries(Series):
    """Series of subtitles with audio clips."""

    event_class = AudioSubtitle
    events: list[AudioSubtitle]  # pyright: ignore[reportIncompatibleVariableOverride]

    @classmethod
    def from_video(
        cls, video_path: str | Path, subtitles: Series
    ) -> AudioSubtitleSeries:
        """Load audio from a video file and slice into clips.

        Arguments:
            video_path: Path to video or audio file
            subtitles: Subtitle series providing timing and text
        Returns:
            AudioSubtitleSeries with audio clips for each subtitle
        """
        video_path = validate_input_file(video_path)
        audio = AudioSegment.from_file(str(video_path))

        series = cls()
        series.events = []
        for sub in subtitles.events:
            clip = audio[sub.start : sub.end]
            series.events.append(
                cls.event_class(
                    start=sub.start,
                    end=sub.end,
                    text=sub.text,
                    audio=clip,
                    series=series,
                )
            )
        return series

    def save(self, path: str | Path, format_: str | None = None, **kwargs: Any) -> None:
        """Save series to an output file or directory of audio clips."""
        path = Path(path)

        if format_ == "wav" or (not format_ and path.suffix == ""):
            path = validate_output_directory(path)
            self._save_wav(path)
            info(f"Saved series to {path}")
            return

        path = validate_output_file(path)
        super().save(str(path), format_=format_, **kwargs)
        info(f"Saved series to {path}")

    def _save_wav(self, fp: Path) -> None:
        """Save series as a directory of wav files with accompanying srt."""
        if fp.exists() and fp.is_dir():
            for file in fp.iterdir():
                file.unlink()
                info(f"Deleted {file}")
        else:
            fp.mkdir(parents=True)
            info(f"Created directory {fp}")

        for i, event in enumerate(self.events, 1):
            outfile = fp / f"{i:04d}_{event.start:08d}_{event.end:08d}.wav"
            event.audio.export(outfile, format="wav")
            info(f"Saved audio to {outfile}")

        outfile = fp / f"{fp.stem}.srt"
        Series.save(self, str(outfile), format_="srt")
