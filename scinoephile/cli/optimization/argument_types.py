#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Argument type helpers for optimization CLI commands."""

from __future__ import annotations

from argparse import ArgumentTypeError

from scinoephile.core.llms import OperationSpec
from scinoephile.optimization.operations import OPERATIONS

__all__ = ["operation_arg"]


def operation_arg(value: str) -> OperationSpec:
    """Validate an optimization operation CLI argument.

    Arguments:
        value: raw CLI argument value
    Returns:
        parsed operation specification
    Raises:
        ArgumentTypeError: if operation is not known
    """
    try:
        return OPERATIONS[value]
    except KeyError as exc:
        options = ", ".join(OPERATIONS)
        raise ArgumentTypeError(f"{value} is not one of {options}") from exc
