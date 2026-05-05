#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PaddleOCR result processing."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "PaddleOcrBoundingBox",
    "PaddleOcrPoint",
    "PaddleOcrTextResult",
    "format_paddle_ocr_text",
    "group_paddle_ocr_text_results",
]


@dataclass(frozen=True)
class PaddleOcrPoint:
    """Point in a PaddleOCR bounding box."""

    x: float
    """X coordinate."""
    y: float
    """Y coordinate."""


@dataclass(frozen=True)
class PaddleOcrBoundingBox:
    """PaddleOCR text bounding box."""

    top_left: PaddleOcrPoint
    """Top-left point."""
    top_right: PaddleOcrPoint
    """Top-right point."""
    bottom_right: PaddleOcrPoint
    """Bottom-right point."""
    bottom_left: PaddleOcrPoint
    """Bottom-left point."""

    @property
    def center(self) -> PaddleOcrPoint:
        """Center point."""
        return PaddleOcrPoint(
            (
                self.top_left.x
                + self.top_right.x
                + self.bottom_right.x
                + self.bottom_left.x
            )
            / 4,
            (
                self.top_left.y
                + self.top_right.y
                + self.bottom_right.y
                + self.bottom_left.y
            )
            / 4,
        )

    @property
    def height(self) -> float:
        """Bounding box height."""
        return max(
            abs(self.bottom_left.y - self.top_left.y),
            abs(self.bottom_right.y - self.top_right.y),
        )


@dataclass(frozen=True)
class PaddleOcrTextResult:
    """PaddleOCR text detection result."""

    text: str
    """Recognized text."""
    confidence: float
    """Recognition confidence."""
    bounding_box: PaddleOcrBoundingBox
    """Text bounding box."""


def format_paddle_ocr_text(
    results: list[PaddleOcrTextResult],
    *,
    min_confidence: float = 0.0,
) -> str:
    """Format PaddleOCR results as subtitle text.

    Arguments:
        results: PaddleOCR text results
        min_confidence: minimum confidence to include
    Returns:
        subtitle text with ASS/SRT newline escapes
    """
    filtered_results = [
        result for result in results if result.confidence >= min_confidence
    ]
    lines = group_paddle_ocr_text_results(filtered_results)
    return "\\N".join(" ".join(result.text for result in line) for line in lines)


def group_paddle_ocr_text_results(
    results: list[PaddleOcrTextResult],
) -> list[list[PaddleOcrTextResult]]:
    """Group PaddleOCR results into text lines.

    This geometry-based line grouping is adapted from SubtitleEdit's PaddleOCR
    result formatting.

    Arguments:
        results: PaddleOCR text results
    Returns:
        text results grouped into lines
    """
    if not results:
        return []

    average_height = sum(result.bounding_box.height for result in results) / len(
        results
    )
    sorted_results = sorted(results, key=lambda result: result.bounding_box.center.y)
    lines: list[list[PaddleOcrTextResult]] = []
    line: list[PaddleOcrTextResult] = []
    previous_result: PaddleOcrTextResult | None = None

    for result in sorted_results:
        if previous_result is not None and (
            result.bounding_box.center.y
            > previous_result.bounding_box.top_left.y + average_height
        ):
            lines.append(_sort_line(line))
            line = []
        line.append(result)
        previous_result = result

    if line:
        lines.append(_sort_line(line))

    return lines


def _sort_line(
    results: list[PaddleOcrTextResult],
) -> list[PaddleOcrTextResult]:
    """Sort one text line left-to-right.

    Arguments:
        results: text results in a line
    Returns:
        sorted text results
    """
    return sorted(results, key=lambda result: result.bounding_box.top_left.x)
