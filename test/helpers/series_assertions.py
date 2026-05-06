#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Assertions for subtitle series tests."""

from __future__ import annotations

from pysubs2 import SSAFile

__all__ = ["assert_series_equal"]


def assert_series_equal(actual: SSAFile, expected: SSAFile):
    """Assert that subtitle series match, with mismatch details.

    Arguments:
        actual: actual subtitle series
        expected: expected subtitle series
    """
    _assert_subtitle_series(actual, "actual")
    _assert_subtitle_series(expected, "expected")

    if len(actual) != len(expected):
        raise AssertionError(
            "Subtitle series length mismatch.\n"
            f"Actual length: {len(actual)}\n"
            f"Expected length: {len(expected)}"
        )

    for event_idx, (actual_event, expected_event) in enumerate(
        zip(actual, expected), start=1
    ):
        actual_text = actual_event.text.replace("\n", "\\N")
        expected_text = expected_event.text.replace("\n", "\\N")
        if (
            actual_event.start == expected_event.start
            and actual_event.end == expected_event.end
            and actual_text == expected_text
        ):
            continue

        raise AssertionError(
            f"Subtitle event {event_idx} mismatch.\n"
            f"Actual: start={actual_event.start}, end={actual_event.end}, "
            f"text={actual_text!r}\n"
            f"Expected: start={expected_event.start}, end={expected_event.end}, "
            f"text={expected_text!r}"
        )


def _assert_subtitle_series(value: object, label: str):
    """Assert that a value is a subtitle series.

    Arguments:
        value: value to validate
        label: name of the validated value
    """
    if not isinstance(value, SSAFile):
        raise AssertionError(
            f"{label} is not a subtitle series: {type(value).__name__}"
        )
