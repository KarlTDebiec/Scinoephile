#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Argument type helpers for optimization CLI commands."""

from __future__ import annotations

from argparse import ArgumentTypeError
from importlib import import_module

from scinoephile.core.llms import OperationSpec, Prompt
from scinoephile.optimization.operations import OPERATIONS

__all__ = [
    "operation_arg",
    "source_prompt_arg",
]


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


def source_prompt_arg(value: str) -> type[Prompt]:
    """Import and validate a source prompt class CLI argument.

    Arguments:
        value: fully qualified Python class path
    Returns:
        imported prompt class
    Raises:
        ArgumentTypeError: if the path cannot be imported or is not a prompt class
    """
    try:
        module_name, class_name = value.rsplit(".", maxsplit=1)
        prompt_cls = getattr(import_module(module_name), class_name)
    except (AttributeError, ImportError, ValueError) as exc:
        raise ArgumentTypeError(f"Unable to import prompt class {value}") from exc
    if not isinstance(prompt_cls, type) or not issubclass(prompt_cls, Prompt):
        raise ArgumentTypeError(f"{value} is not a prompt class")
    return prompt_cls
