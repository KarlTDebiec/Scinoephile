#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""General-purpose functions related to argument parsing."""

from __future__ import annotations

from argparse import (
    ArgumentParser,
    ArgumentTypeError,
    _ArgumentGroup,  # noqa pylint
)
from collections.abc import Callable, Collection
from pathlib import Path
from typing import Any, TypedDict, Unpack

from .validation import (
    val_float,
    val_input_dir_path,
    val_input_path,
    val_int,
    val_output_dir_path,
    val_output_path,
    val_str,
)

__all__ = [
    "FloatValidatorKwargs",
    "IntValidatorKwargs",
    "OutputPathValidatorKwargs",
    "StrValidatorKwargs",
    "float_arg",
    "get_arg_groups_by_name",
    "get_optional_args_group",
    "get_required_args_group",
    "get_validator",
    "input_dir_arg",
    "input_file_arg",
    "int_arg",
    "output_dir_arg",
    "output_file_arg",
    "str_arg",
]


class FloatValidatorKwargs(TypedDict, total=False):
    """Keyword arguments for val_float."""

    n_values: int | None
    min_value: float | None
    max_value: float | None


class IntValidatorKwargs(TypedDict, total=False):
    """Keyword arguments for val_int."""

    n_values: int | None
    min_value: int | None
    max_value: int | None
    acceptable_values: Collection[int] | None


class OutputPathValidatorKwargs(TypedDict, total=False):
    """Keyword arguments for val_output_path."""

    exist_ok: bool


class StrValidatorKwargs(TypedDict, total=False):
    """Keyword arguments for val_str."""

    options: Collection[str]


def get_optional_args_group(parser: ArgumentParser) -> _ArgumentGroup:
    """Get the optional arguments group from an argparser.

    Arguments:
        parser: Argparser to get group from
    Returns:
        Optional arguments group
    """
    action_groups = parser._action_groups  # noqa pylint: disable=protected-access
    return next(
        ag for ag in action_groups if ag.title in ["optional arguments", "options"]
    )


def get_required_args_group(parser: ArgumentParser) -> _ArgumentGroup:
    """Get or create a 'required arguments' group from an argparser.

    Arguments:
        parser: Argparser to get group from
    Returns:
        Required arguments group
    """
    action_groups = parser._action_groups  # noqa pylint: disable=protected-access
    for group in action_groups:
        if group.title == "required arguments":
            return group

    # Move "optional arguments" group below "required arguments" group
    optional = action_groups.pop()
    required = parser.add_argument_group("required arguments")
    action_groups.append(optional)

    return required


def get_arg_groups_by_name(
    parser: ArgumentParser,
    *names: str,
    optional_arguments_name: str = "optional arguments",
) -> dict[str, _ArgumentGroup]:
    """Get or create one or more argument groups by name.

    Groups will be ordered by the order in which they are specified, with additional
    groups whose names were not included in names appearing after the specified groups.

    For example, if names = ("input arguments", "operation arguments",
    "output arguments"), groups by these names will be created, yielding the final order
    of ("input arguments", "operation arguments", "output arguments",
    "optional arguments").

    The default "optional arguments" group may be renamed by providing
    optional_arguments_name.

    Arguments:
        parser: Argparser to get groups from
        *names: Names of groups to get or create
        optional_arguments_name: Name of optional arguments group
    Returns:
        Dictionary of names to argument groups
    """
    specified_groups = {}
    for name in names:
        action_groups = parser._action_groups  # noqa pylint: disable=protected-access
        for i, ag in enumerate(action_groups):
            if ag.title == name:
                specified_groups[name] = action_groups.pop(i)
                break
        else:
            parser.add_argument_group(name)
            specified_groups[name] = action_groups.pop()

    action_groups = parser._action_groups  # noqa pylint: disable=protected-access
    additional_groups = {}
    while len(action_groups) > 0:
        ag = action_groups.pop()
        if ag.title in ["options", "optional arguments"]:
            ag.title = optional_arguments_name
        if ag.title:
            additional_groups[ag.title] = ag

    action_groups.extend(specified_groups.values())
    action_groups.extend(additional_groups.values())

    return {**specified_groups, **additional_groups}


def get_validator[T](function: Callable[..., T], **kwargs: Any) -> Callable[[Any], T]:
    """Get a function that can be called with the same signature as function.

    Arguments:
        function: Function to be wrapped
        **kwargs: Keyword arguments to pass to wrapped function
    Returns:
        Wrapped function
    """

    def wrapped(value: Any) -> T:
        """Wrapped function.

        Arguments:
            value: Value to be validated
        Returns:
            Validated value
        Raises:
            ArgumentTypeError: If TypeError is raised by wrapped function
        """
        try:
            return function(value, **kwargs)
        except TypeError as exc:
            raise ArgumentTypeError from exc

    return wrapped


def float_arg(
    **kwargs: Unpack[FloatValidatorKwargs],
) -> Callable[[Any], float | list[float]]:
    """Validate a float argument.

    Arguments:
        **kwargs: keyword arguments to pass to val_float
    Returns:
        value validator function
    """
    return get_validator(val_float, **kwargs)


def input_dir_arg() -> Callable[[Any], Path | list[Path]]:
    """Validate an input directory path argument.

    Returns:
        value validator function
    """
    return get_validator(val_input_dir_path)


def input_file_arg() -> Callable[[Any], Path | list[Path]]:
    """Validate an input file path argument.

    Returns:
        value validator function
    """
    return get_validator(val_input_path)


def int_arg(**kwargs: Unpack[IntValidatorKwargs]) -> Callable[[Any], int | list[int]]:
    """Validate an int argument.

    Arguments:
        **kwargs: keyword arguments to pass to val_int
    Returns:
        value validator function
    """
    return get_validator(val_int, **kwargs)


def output_dir_arg() -> Callable[[Any], Path | list[Path]]:
    """Validate an output directory path argument.

    Returns:
        value validator function
    """
    return get_validator(val_output_dir_path)


def output_file_arg(
    **kwargs: Unpack[OutputPathValidatorKwargs],
) -> Callable[[Any], Path | list[Path]]:
    """Validate an output file path argument.

    Arguments:
        **kwargs: keyword arguments to pass to val_output_path
    Returns:
        value validator function
    """
    return get_validator(val_output_path, **kwargs)


def str_arg(**kwargs: Unpack[StrValidatorKwargs]) -> Callable[[Any], str]:
    """Validate a string argument.

    Arguments:
        **kwargs: keyword arguments to pass to val_str
    Returns:
        value validator function
    """
    return get_validator(val_str, **kwargs)
