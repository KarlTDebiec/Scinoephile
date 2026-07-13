#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Series of subtitles with images."""

from __future__ import annotations

import re
from collections import Counter
from html import escape, unescape
from logging import getLogger
from os import PathLike
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Self, override

import numpy as np
from PIL import Image

from scinoephile.common.validation import (
    val_input_dir_path,
    val_input_file_or_dir_path,
    val_output_dir_path,
    val_output_path,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.image.bboxes import get_bboxes
from scinoephile.image.colors import get_fill_and_outline_colors_from_hist
from scinoephile.image.drawing import convert_rgba_img_to_la

from .subtitle import ImageSubtitle
from .sup import read_sup_series

__all__ = ["ImageSeries"]


logger = getLogger(__name__)


_DEFAULT_TEXT_FONT_SIZE = 50
_TEXT_FONT_SIZE_PERCENTILE = 0.75


class ImageSeries(Series):
    """Series of subtitles with images."""

    event_class = ImageSubtitle
    """Class of individual subtitle events."""
    events: list[ImageSubtitle]
    """Individual subtitle events."""

    @override
    def __init__(self, events: list[ImageSubtitle] | None = None):
        """Initialize.

        Arguments:
            events: individual subtitle events
        """
        super().__init__()
        if events is not None:
            self.events = events
        self._fill_color = None
        self._outline_color = None
        self._text_font_size = None
        self._blocks: list[ImageSeries] | None = None

    @override
    def __setattr__(self, name: str, value: object):
        """Set attribute, invalidating cached image properties after event replacement.

        Arguments:
            name: attribute name
            value: attribute value
        """
        super().__setattr__(name, value)
        if name == "events":
            if hasattr(self, "_fill_color"):
                self._fill_color = None
            if hasattr(self, "_outline_color"):
                self._outline_color = None
            if hasattr(self, "_text_font_size"):
                self._text_font_size = None

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

    @property
    def text_font_size(self) -> int:
        """Detected font size of subtitle text images."""
        if self._text_font_size is None:
            self._init_text_font_size()
        if self._text_font_size is None:
            raise ScinoephileError("Text font size could not be determined.")
        return self._text_font_size

    @property
    @override
    def blocks(self) -> list[ImageSeries]:
        """List of blocks in the series."""
        if self._blocks is None:
            self._init_blocks()
        assert self._blocks is not None
        return self._blocks

    @blocks.setter
    @override
    def blocks(self, blocks: list[ImageSeries]):
        """Set blocks of the series.

        Arguments:
            blocks: List of blocks in the series
        """
        self._blocks = blocks

    def copy_text_from(self, source: Series):
        """Copy subtitle text from a source series into this image series.

        Arguments:
            source: source text subtitle series
        Raises:
            ScinoephileError: if source and image subtitle counts differ
        """
        if len(source) != len(self):
            raise ScinoephileError(f"Length mismatch: {len(source)} vs {len(self)}")
        for source_subtitle, image_subtitle in zip(source, self.events):
            image_subtitle.text = source_subtitle.text

    def save_html_index(
        self,
        dir_path: str | PathLike[Any],
        encoding: str = "utf-8",
        errors: str | None = None,
    ):
        """Save only the HTML index for an existing image subtitle directory.

        Arguments:
            dir_path: path to existing image subtitle directory
            encoding: output file encoding
            errors: encoding error handling
        """
        try:
            validated_dir_path = val_input_dir_path(dir_path)
            html_lines = self.html_header_lines()
            for i, event in enumerate(self, 1):
                image_name = f"{i:04d}.png"
                html_lines.append(
                    self.format_html_entry(
                        index=i,
                        start=event.start,
                        end=event.end,
                        image_name=image_name,
                        text=event.text,
                    )
                )
            html_lines.extend(self.html_footer_lines())
            html_path = validated_dir_path / "index.html"
            html_path.write_text(
                "\n".join(html_lines), encoding=encoding, errors=errors
            )
        except (OSError, TypeError, UnicodeError, ValueError) as exc:
            raise ScinoephileError(
                f"Unable to save HTML index to {dir_path}: {exc}"
            ) from exc
        logger.info(f"Saved HTML to {html_path}")

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

        try:
            # Check if directory
            if format_ == "html" or (not format_ and path.suffix == ""):
                validated_output_dir_path = val_output_dir_path(path)
                self._save_html(
                    validated_output_dir_path,
                    encoding=encoding,
                    errors=errors,
                )
                logger.info(f"Saved series to {validated_output_dir_path}")
                return

            # Otherwise, continue as superclass
            exist_ok = kwargs.pop("exist_ok", False)
            validated_output_path = val_output_path(path, exist_ok=exist_ok)
            super().save(
                validated_output_path,
                encoding=encoding,
                format_=format_,
                fps=fps,
                errors=errors,
                **kwargs,
            )
        except (OSError, UnicodeError, ValueError) as exc:
            raise ScinoephileError(
                f"Unable to save {type(self).__name__} to {path}: {exc}"
            ) from exc
        logger.info(f"Saved series to {validated_output_path}")

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
            validated_path = val_input_file_or_dir_path(path)
            if validated_path.is_dir():
                return cls._load_html(
                    validated_path,
                    encoding=encoding,
                    errors=errors,
                )
            if format_ == "sup" or validated_path.suffix == ".sup":
                return cls._load_sup(validated_path)
        except (OSError, UnicodeError, ValueError) as exc:
            raise ScinoephileError(
                f"Unable to load {cls.__name__} from {path}: {exc}"
            ) from exc
        raise ScinoephileError(
            f"{cls.__name__}'s path must be path to a directory containing one "
            "index.html file and N png files, or a .sup file."
        )

    @override
    def _init_blocks(self):
        """Initialize blocks."""
        self._blocks = [
            self.slice(start_idx, end_idx)
            for start_idx, end_idx in Series.get_block_indexes_by_pause(self)
        ]

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

    def _init_text_font_size(self):
        """Initialize the representative subtitle text font size."""
        size_counts: Counter[int] = Counter()
        for subtitle in self.events:
            if subtitle.bboxes is None:
                bboxes = get_bboxes(subtitle.img)
            else:
                bboxes = subtitle.bboxes
            size_counts.update(bbox.height for bbox in bboxes)

        if not size_counts:
            self._text_font_size = _DEFAULT_TEXT_FONT_SIZE
            return

        threshold = sum(size_counts.values()) * _TEXT_FONT_SIZE_PERCENTILE
        cumulative_count = 0
        for height in sorted(size_counts):
            cumulative_count += size_counts[height]
            if cumulative_count >= threshold:
                self._text_font_size = height
                return
        self._text_font_size = max(size_counts)

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
        # Stage the complete managed output before changing the destination
        with TemporaryDirectory(
            dir=dir_path.parent,
            prefix=f".{dir_path.name}.",
        ) as staging_dir_name:
            staging_dir_path = Path(staging_dir_name)
            image_paths = []
            for i, event in enumerate(self, 1):
                image_path = staging_dir_path / f"{i:04d}.png"
                event.img.save(image_path)
                image_paths.append(image_path)
            self.save_html_index(
                staging_dir_path,
                encoding=encoding,
                errors=errors,
            )

            # Reject conflicting directories before replacing any managed files
            staged_paths = [*image_paths, staging_dir_path / "index.html"]
            for staged_path in staged_paths:
                output_path = dir_path / staged_path.name
                if output_path.is_dir():
                    raise IsADirectoryError(f"{output_path} is a directory")

            # Replace images first and the index last, preserving unrelated entries
            for image_path in image_paths:
                image_path.replace(dir_path / image_path.name)
            (staging_dir_path / "index.html").replace(dir_path / "index.html")
        logger.info(f"Saved images and HTML to {dir_path}")

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
        html_path = dir_path / "index.html"
        if not html_path.exists():
            raise ScinoephileError(f"Expected {html_path} to exist.")
        html_text = html_path.read_text(encoding=encoding, errors=errors)
        html_events = cls.parse_html_events(html_text, dir_path)

        series = cls()
        series.format = "png"
        events = []
        for html_event in html_events:
            with Image.open(html_event["path"]) as opened:
                img = opened.copy()
            img, converted = convert_rgba_img_to_la(img)
            if converted:
                img.save(html_event["path"])
                logger.info(f"Converted {html_event['path']} to LA and resaved")
            events.append(
                cls.event_class(
                    start=html_event["start"],
                    end=html_event["end"],
                    img=img,
                    text=html_event["text"],
                )
            )
        series.events = events
        return series

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

        events = []
        for start, end, image in zip(starts, ends, images):
            img = Image.fromarray(image, "RGBA")
            img, _ = convert_rgba_img_to_la(img)
            events.append(
                cls.event_class(
                    start=int(round(start * 1000)),
                    end=int(round(end * 1000)),
                    img=img,
                )
            )
        series = cls(events=events)
        series.format = "sup"
        return series

    @classmethod
    def parse_html_events(
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
        image_div_attributes = (
            r"(?: (?:style=['\"]text-align:center['\"]|"
            r"class=['\"]subtitle-image['\"]))?"
        )
        text_div_attributes = (
            r"(?: (?:style=['\"]font-size:22px; background-color:WhiteSmoke['\"]|"
            r"class=['\"]subtitle-text['\"]))?"
        )
        pattern = re.compile(
            r"(?:<a id=['\"](?:sub|subtitle-number)-(?P<anchor_index>\d+)['\"] "
            r"href=['\"]#(?:sub|subtitle-number)-\d+['\"]>)?"
            r"#(?P<index>\d+)(?:</a>)?:"
            r"(?P<start>[^-]+)->(?P<end>[^<]+)"
            rf"<div{image_div_attributes}>"
            r"<img src=['\"](?P<img>[^'\"]+)['\"] />"
            rf"(?:<br /><div{text_div_attributes}>(?P<text>.*?)</div>)?"
            r"</div><br /><hr />",
            re.DOTALL,
        )
        events = []
        for match in pattern.finditer(html_text):
            index = int(match.group("index"))
            anchor_index = match.group("anchor_index")
            if anchor_index is not None and int(anchor_index) != index:
                raise ValueError(
                    f"Subtitle anchor index {anchor_index} does not match {index}."
                )
            image_name = match.group("img")
            image_path = dir_path / image_name
            raw_text = match.group("text") or ""
            text = unescape(raw_text.replace("<br />", "\n")).replace("\n", "\\N")
            events.append(
                {
                    "index": index,
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

    @staticmethod
    def format_html_entry(
        *,
        index: int,
        start: int,
        end: int,
        image_name: str,
        text: str,
    ) -> str:
        """Format one HTML subtitle entry.

        Arguments:
            index: one-based subtitle index
            start: start time in milliseconds
            end: end time in milliseconds
            image_name: subtitle image file name
            text: subtitle text using ASS newline escapes
        Returns:
            formatted HTML subtitle entry
        """
        start_text = ImageSeries._format_html_time(start)
        end_text = ImageSeries._format_html_time(end)
        anchor_id = f"sub-{index}"
        line = (
            f"<a id='{anchor_id}' href='#{anchor_id}'>#{index}</a>:"
            f"{start_text}->{end_text}"
            "<div>"
            f"<img src='{escape(image_name, quote=True)}' />"
        )
        text_with_newline = text.replace("\\N", "\n")
        if text_with_newline.strip():
            html_text = escape(text_with_newline).replace("\n", "<br />")
            line += f"<br /><div>{html_text}</div>"
        line += "</div><br /><hr />"
        return line

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

    @staticmethod
    def html_footer_lines() -> list[str]:
        """Return HTML footer lines for image subtitle indexes.

        Returns:
            HTML footer lines
        """
        return ["</body>", "</html>"]

    @staticmethod
    def html_header_lines() -> list[str]:
        """Return HTML header lines for image subtitle indexes.

        Returns:
            HTML header lines
        """
        return [
            "<!DOCTYPE html>",
            '<html lang="">',
            "<head>",
            '   <meta charset="UTF-8" />',
            "   <title>Subtitle images</title>",
            "   <style>",
            "      body > div {",
            "         text-align: center;",
            "",
            "         img {",
            "            image-rendering: pixelated;",
            "         }",
            "",
            "         > div {",
            "            background-color: WhiteSmoke;",
            "            font-size: 22px;",
            "         }",
            "      }",
            "   </style>",
            "</head>",
            "<body>",
        ]
