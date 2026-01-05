#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series of subtitles with images."""

from __future__ import annotations

import re
from html import escape, unescape
from logging import info
from pathlib import Path
from typing import Any, Self, override

import numpy as np
from PIL import Image

from scinoephile.common import DirectoryNotFoundError
from scinoephile.common.validation import (
    val_input_dir_path,
    val_input_path,
    val_output_dir_path,
    val_output_path,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.image.colors import get_fill_and_outline_colors_from_hist

from .subtitle import ImageSubtitle
from .sup import read_sup_series

__all__ = ["ImageSeries"]


class ImageSeries(Series):
    """Series of subtitles with images."""

    event_class = ImageSubtitle
    """Class of individual subtitle events."""
    events: list[ImageSubtitle]
    """Individual subtitle events."""

    @override
    def __init__(self):
        """Initialize."""
        super().__init__()

        self._fill_color = None
        self._outline_color = None

    @property
    def fill_color(self) -> int:
        """Fill color of text images."""
        if self._fill_color is None:
            self._init_fill_and_outline_colors()
        if self._fill_color is None:
            raise ScinoephileError("Fill color could not be determined.")
        return self._fill_color

    @property
    def outline_color(self) -> int:
        """Outline color of text images."""
        if self._outline_color is None:
            self._init_fill_and_outline_colors()
        if self._outline_color is None:
            raise ScinoephileError("Outline color could not be determined.")
        return self._outline_color

    @override
    def save(
        self,
        path: Path | str,
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
        if format_ == "png" or (not format_ and path.suffix == ""):
            output_dir = val_output_dir_path(path)
            self._save_png(output_dir, encoding=encoding, errors=errors)
            info(f"Saved series to {output_dir}")
            return

        # Otherwise, continue as superclass
        exist_ok = kwargs.pop("exist_ok", False)
        output_path = val_output_path(path, exist_ok=exist_ok)
        super().save(
            output_path,
            encoding=encoding,
            format_=format_,
            fps=fps,
            errors=errors,
            **kwargs,
        )
        info(f"Saved series to {output_path}")

    def _save_png(
        self,
        dir_path: Path,
        encoding: str = "utf-8",
        errors: str | None = None,
    ):
        """Save series to directory of png files.

        Arguments:
            dir_path: Path to output directory
            encoding: output file encoding
            errors: encoding error handling
        """
        self._save_html(dir_path, encoding=encoding, errors=errors)

    def _save_html(
        self,
        dir_path: Path,
        encoding: str = "utf-8",
        errors: str | None = None,
    ):
        """Save series to directory with HTML index and png files.

        Arguments:
            dir_path: Path to output directory
            encoding: output file encoding
            errors: encoding error handling
        """
        # Prepare empty directory, deleting existing files if needed
        if dir_path.exists() and dir_path.is_dir():
            for file in dir_path.iterdir():
                file.unlink()
                info(f"Deleted {file}")
        else:
            dir_path.mkdir(parents=True)
            info(f"Created directory {dir_path}")

        # Save images
        image_paths = []
        for i, event in enumerate(self, 1):
            outfile_path = dir_path / f"{i:04d}.png"
            event.img.save(outfile_path)
            image_paths.append(outfile_path)
            info(f"Saved image to {outfile_path}")

        # Save HTML index
        html_lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            '   <meta charset="UTF-8" />',
            "   <title>Subtitle images</title>",
            "</head>",
            "<body>",
        ]
        for i, (event, image_path) in enumerate(zip(self, image_paths), 1):
            start = self._format_html_time(event.start)
            end = self._format_html_time(event.end)
            line = (
                f"#{i}:{start}->{end}"
                "<div style='text-align:center'>"
                f"<img src='{image_path.name}' />"
            )
            text = event.text.replace("\\N", "\n")
            if text.strip():
                text = escape(text).replace("\n", "<br />")
                line += (
                    "<br />"
                    "<div style='font-size:22px; background-color:WhiteSmoke'>"
                    f"{text}</div>"
                )
            line += "</div><br /><hr />"
            html_lines.append(line)
        html_lines.extend(["</body>", "</html>"])
        html_path = dir_path / "index.html"
        html_path.write_text("\n".join(html_lines), encoding=encoding, errors=errors)
        info(f"Saved HTML to {html_path}")

    @classmethod
    @override
    def load(
        cls,
        path: Path | str,
        encoding: str = "utf-8",
        format_: str | None = None,
        fps: float | None = None,
        errors: str | None = None,
        **kwargs: Any,
    ) -> Self:
        """Load series from an input file.

        Arguments:
            path: input file path
            encoding: input file encoding
            format_: input file format
            fps: frames per second
            errors: encoding error handling
            **kwargs: additional keyword arguments
        Returns:
            loaded series
        """
        try:
            validated_path = val_input_dir_path(path)
            return cls._load_html(
                validated_path,
                encoding=encoding,
                errors=errors,
            )
        except (DirectoryNotFoundError, NotADirectoryError):
            validated_path = val_input_path(path)
            if format_ == "sup" or validated_path.suffix == ".sup":
                return cls._load_sup(validated_path)
            raise ValueError(
                f"{cls.__name__}'s path must be path to a directory containing one "
                "index.html file and N png files, or a .sup file."
            )

    @classmethod
    def _load_html(
        cls,
        dir_path: Path,
        encoding: str = "utf-8",
        errors: str | None = None,
    ) -> Self:
        """Load series from a directory of png files and HTML index.

        Arguments:
            dir_path: Path to input directory
            encoding: input file encoding
            errors: encoding error handling
        Returns:
            loaded series
        """
        series = cls()
        series.format = "png"

        html_path = dir_path / "index.html"
        if not html_path.exists():
            raise ScinoephileError(f"Expected {html_path} to exist.")
        html_text = html_path.read_text(encoding=encoding, errors=errors)
        html_events = cls._parse_html_events(html_text, dir_path)

        for html_event in html_events:
            img = Image.open(html_event["path"])
            img, converted = cls._convert_rgba_to_la(img)
            if converted:
                img.save(html_event["path"])
                info(f"Converted {html_event['path']} to LA and resaved")
            series.events.append(
                cls.event_class(
                    start=html_event["start"],
                    end=html_event["end"],
                    img=img,
                    text=html_event["text"],
                    series=series,
                )
            )

        return series

    @staticmethod
    def _format_html_time(time_ms: int) -> str:
        """Format time in milliseconds for HTML image subtitles.

        Arguments:
            time_ms: time in milliseconds
        Returns:
            formatted time string
        """
        total_seconds, milliseconds = divmod(time_ms, 1000)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
        if minutes:
            return f"{minutes}:{seconds:02d},{milliseconds:03d}"
        return f"{seconds},{milliseconds:03d}"

    @staticmethod
    def _parse_html_time(time_str: str) -> int:
        """Parse time string from HTML image subtitles into milliseconds.

        Arguments:
            time_str: time string
        Returns:
            time in milliseconds
        """
        time_str = time_str.strip()
        if "," in time_str:
            time_part, ms_part = time_str.split(",", 1)
        else:
            time_part, ms_part = time_str, "0"
        ms = int(ms_part.ljust(3, "0")[:3])
        parts = time_part.split(":")
        if len(parts) == 1:
            hours = 0
            minutes = 0
            seconds = int(parts[0])
        elif len(parts) == 2:
            hours = 0
            minutes = int(parts[0])
            seconds = int(parts[1])
        elif len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
        else:
            raise ValueError(f"Unrecognized time format: {time_str}")
        return int(((hours * 3600) + (minutes * 60) + seconds) * 1000 + ms)

    @classmethod
    def _parse_html_events(
        cls,
        html_text: str,
        dir_path: Path,
    ) -> list[dict[str, Any]]:
        """Parse HTML events for image subtitles.

        Arguments:
            html_text: HTML content
            dir_path: directory containing images
        Returns:
            list of parsed event data
        """
        pattern = re.compile(
            r"#(?P<index>\d+):(?P<start>[^-]+)->(?P<end>[^<]+)"
            r"<div style=['\"]text-align:center['\"]>"
            r"<img src=['\"](?P<img>[^'\"]+)['\"] />"
            r"(?:<br /><div style=['\"]font-size:22px; "
            r"background-color:WhiteSmoke['\"]>(?P<text>.*?)</div>)?"
            r"</div><br /><hr />",
            re.DOTALL,
        )
        events = []
        for match in pattern.finditer(html_text):
            image_name = match.group("img")
            image_path = dir_path / image_name
            raw_text = match.group("text") or ""
            text = unescape(raw_text.replace("<br />", "\n"))
            events.append(
                {
                    "index": int(match.group("index")),
                    "start": cls._parse_html_time(match.group("start")),
                    "end": cls._parse_html_time(match.group("end")),
                    "path": image_path,
                    "text": text,
                }
            )
        if not events:
            raise ScinoephileError(
                f"No subtitle entries found in HTML file for {dir_path}."
            )
        return events

    @classmethod
    def _load_sup(cls, file_path: Path) -> Self:
        """Load series from a sup file.

        Arguments:
            file_path: path to sup file
        Returns:
            loaded series
        """
        data = np.frombuffer(file_path.read_bytes(), dtype=np.uint8)
        starts, ends, images = read_sup_series(data)
        if len(starts) != len(ends) or len(starts) != len(images):
            raise ScinoephileError(
                f"Sup data in {file_path} is malformed: "
                f"{len(starts)} starts, {len(ends)} ends, {len(images)} images."
            )

        series = cls()
        series.format = "sup"
        for start, end, image in zip(starts, ends, images):
            img = Image.fromarray(image, "RGBA")
            img, _ = cls._convert_rgba_to_la(img)
            series.events.append(
                cls.event_class(
                    start=int(round(start * 1000)),
                    end=int(round(end * 1000)),
                    img=img,
                )
            )
        return series

    def _init_fill_and_outline_colors(self):
        """Initialize the fill and outline colors used in this series.

        * Uses the most common two colors, which works correctly for tested images.
        * Tested images used a 16-color palette.
        """
        hist = np.zeros(256, dtype=np.uint64)
        for subtitle in self.events:
            grayscale = subtitle.arr[:, :, 0]
            alpha = subtitle.arr[:, :, 1]
            mask = alpha != 0
            values = grayscale[mask]
            np.add.at(hist, values, 1)

        fill, outline = get_fill_and_outline_colors_from_hist(hist)
        self._fill_color = fill
        self._outline_color = outline

    @staticmethod
    def _convert_rgba_to_la(img: Image.Image) -> tuple[Image.Image, bool]:
        """Convert RGBA images with grayscale color channels to LA.

        Arguments:
            img: Image to convert
        Returns:
            Image and whether it was converted
        """
        if img.mode != "RGBA":
            return img, False
        arr = np.array(img)
        if np.all(arr[:, :, 0] == arr[:, :, 1]) and np.all(
            arr[:, :, 1] == arr[:, :, 2]
        ):
            return img.convert("LA"), True
        return img, False
