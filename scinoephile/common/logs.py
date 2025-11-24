#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Logging utilities."""

from __future__ import annotations

from logging import DEBUG, ERROR, INFO, WARNING, basicConfig, getLogger


def set_logging_verbosity(verbosity: int):
    """Set the level of verbosity of logging.

    Arguments:
        verbosity: level of verbosity
    """
    basicConfig()
    match verbosity:
        case 0:
            getLogger().setLevel(level=ERROR)
        case 1:
            getLogger().setLevel(level=WARNING)
        case 2:
            getLogger().setLevel(level=INFO)
        case _:
            getLogger().setLevel(level=DEBUG)


__all__ = [
    "set_logging_verbosity",
]
