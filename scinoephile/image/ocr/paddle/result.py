#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PaddleOCR result formatting."""

from __future__ import annotations

from .text_result import PaddleOcrTextResult

__all__ = ["format_paddle_ocr_text"]


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
    lines = _group_paddle_ocr_text_results(filtered_results)
    return "\\N".join(" ".join(result.text for result in line) for line in lines)


def _group_paddle_ocr_text_results(
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
    sorted_results = sorted(results, key=lambda result: result.bounding_box.center[1])
    lines: list[list[PaddleOcrTextResult]] = []
    line: list[PaddleOcrTextResult] = []
    previous_result: PaddleOcrTextResult | None = None

    for result in sorted_results:
        if previous_result is not None and (
            result.bounding_box.center[1]
            > previous_result.bounding_box.top_left[1] + average_height
        ):
            lines.append(
                sorted(
                    line,
                    key=lambda line_result: line_result.bounding_box.top_left[0],
                )
            )
            line = []
        line.append(result)
        previous_result = result

    if line:
        lines.append(
            sorted(line, key=lambda line_result: line_result.bounding_box.top_left[0])
        )

    return lines
