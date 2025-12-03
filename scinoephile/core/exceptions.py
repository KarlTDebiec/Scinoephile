#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core Scinoephile exceptions."""

from __future__ import annotations


class ScinoephileError(Exception):
    """Scinoephile error."""


class RateLimitError(ScinoephileError):
    """Raised when a rate limit is encountered.

    Attributes:
        wait_time: Number of seconds to wait before retrying if provided.
    """

    def __init__(self, message: str, wait_time: float | None = None):
        """Initialize.

        Arguments:
            message: Description of the rate limit error.
            wait_time: Number of seconds to wait before retrying if available.
        """
        super().__init__(message)
        self.wait_time = wait_time
