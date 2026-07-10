#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Argument type helpers for optimization CLI commands."""

from __future__ import annotations

from argparse import ArgumentTypeError

from scinoephile.core.llms import Manager
from scinoephile.optimization.operations import OPERATIONS
from scinoephile.optimization.prompt_specs import PROMPT_SPECS, PromptSpec

__all__ = [
    "operation_arg",
    "prompt_spec_arg",
]


def operation_arg(value: str) -> type[Manager]:
    """Validate an optimization operation CLI argument.

    Arguments:
        value: raw CLI argument value
    Returns:
        manager class for the parsed operation
    Raises:
        ArgumentTypeError: if operation is not known
    """
    try:
        return OPERATIONS[value]
    except KeyError as exc:
        options = ", ".join(OPERATIONS)
        raise ArgumentTypeError(f"{value} is not one of {options}") from exc


def prompt_spec_arg(value: str) -> PromptSpec:
    """Validate an optimization prompt alias CLI argument.

    Arguments:
        value: raw CLI argument value
    Returns:
        registered prompt specification
    Raises:
        ArgumentTypeError: if the prompt alias is not known
    """
    try:
        return PROMPT_SPECS[value]
    except KeyError as exc:
        options = ", ".join(PROMPT_SPECS)
        raise ArgumentTypeError(f"{value} is not one of {options}") from exc
