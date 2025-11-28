#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""General-purpose validation functions not tied to a particular project."""

from __future__ import annotations

from collections.abc import Collection, Iterable
from logging import info
from os.path import defpath, expanduser, expandvars
from pathlib import Path
from platform import system
from shutil import which
from typing import Any, overload

from .exception import (
    ArgumentConflictError,
    DirectoryNotFoundError,
    ExecutableNotFoundError,
    NotAFileError,
    UnsupportedPlatformError,
)


def val_executable(
    name: str, supported_platforms: Collection[str] | None = None
) -> Path:
    """Validates executable and returns its absolute path.

    Arguments:
        name: executable name
        supported_platforms: Platforms that support executable;
          default: "Darwin", "Linux", "Windows"
    Returns:
        Absolute path of executable
    Raises:
        ExecutableNotFoundError: if executable is not found in path
        UnsupportedPlatformError: if executable is not supported on current platform
    """
    if supported_platforms is None:
        supported_platforms = {"Darwin", "Linux", "Windows"}

    if system() not in supported_platforms:
        raise UnsupportedPlatformError(
            f"Executable '{name}' is not supported on {system()}"
        )

    which_executable = which(name)
    if not which_executable:
        raise ExecutableNotFoundError(f"Executable '{name}' not found in '{defpath}'")
    executable_path = Path(which_executable).resolve()

    return executable_path


@overload
def val_float(
    value: float,
    *,
    n_values: int | None = None,
    min_value: float | None = None,
    max_value: float | None = None,
) -> float: ...
@overload
def val_float(
    value: Iterable[Any],
    *,
    n_values: int | None = None,
    min_value: float | None = None,
    max_value: float | None = None,
) -> list[float]: ...
def val_float(
    value: float | Iterable[Any],
    *,
    n_values: int | None = None,
    min_value: float | None = None,
    max_value: float | None = None,
) -> float | list[float]:
    """Validate one or more floats.

    Arguments:
        value: Single value or iterable of values to validate
        n_values: Number of values expected, if applicable
        min_value: Minimum value of float, if applicable
        max_value: Maximum value of float, if applicable
    Returns:
        Single float or list of floats depending on input
    Raises:
        ArgumentConflictError: If min_value is greater than max_value
        TypeError: If a value may not be cast to a float
        ValueError: If a value is invalid or the list is the wrong length
    """
    if min_value is not None and max_value is not None and (min_value >= max_value):
        raise ArgumentConflictError("min_value must be less than max_value")

    def _val_float(value_to_validate: Any) -> float:
        try:
            validated_value = float(value_to_validate)
        except ValueError as exc:
            raise TypeError(
                f"{value_to_validate} is of type "
                f"{type(value_to_validate)}, cannot be cast to float"
            ) from exc
        if min_value is not None and validated_value < min_value:
            raise ValueError(
                f"{validated_value} is less than minimum value of {min_value}"
            )
        if max_value is not None and validated_value > max_value:
            raise ValueError(
                f"{validated_value} is greater than maximum value of {max_value}"
            )
        return validated_value

    # Handle non-iterables and iterables we don't want to iterate over
    if isinstance(value, str) or not isinstance(value, Iterable):
        return _val_float(value)

    # Handle iterables
    validated_values = [_val_float(value_to_validate) for value_to_validate in value]
    if n_values is not None and len(validated_values) != n_values:
        raise ValueError(
            f"'{validated_values}' is of length {len(validated_values)}, "
            f"not '{n_values}'"
        )
    return validated_values


@overload
def val_input_dir_path(value: Path | str) -> Path: ...
@overload
def val_input_dir_path(value: Iterable[Path | str]) -> list[Path]: ...
def val_input_dir_path(value: Path | str | Iterable[Path | str]) -> Path | list[Path]:
    """Validate input directory path(s) and make them absolute.

    Arguments:
        value: Path or paths to input directories
    Returns:
        Validated path or paths
    Raises:
        DirectoryNotFoundError: If any path does not exist
        NotADirectoryError: If any path is not a directory
        TypeError: If any value cannot be cast to Path
    """

    def _val_input_dir(value_to_validate: Path | str) -> Path:
        """Validate a path.

        Arguments:
            value_to_validate: Path to validate
        Returns:
            Validated path
        Raises:
            DirectoryNotFoundError: If path does not exist
            NotADirectoryError: If path is not a directory
            TypeError: If value cannot be cast to Path
        """
        try:
            validated_value = Path(
                expandvars(expanduser(str(value_to_validate)))
            ).resolve()
        except ValueError as exc:
            raise TypeError(
                f"{value_to_validate} is of type "
                f"{type(value_to_validate)}, cannot be cast to Path"
            ) from exc
        if not validated_value.exists():
            raise DirectoryNotFoundError(
                f"Input directory {validated_value} does not exist"
            )
        if not validated_value.is_dir():
            raise NotADirectoryError(
                f"Input directory {validated_value} is not a directory"
            )
        return validated_value

    # Handle non-iterables and iterables we don't want to iterate over
    if isinstance(value, Path | str) or not isinstance(value, Iterable):
        return _val_input_dir(value)

    # Handle iterables
    return [_val_input_dir(value_to_validate) for value_to_validate in value]


@overload
def val_input_path(value: Path | str) -> Path: ...
@overload
def val_input_path(value: Iterable[Path | str]) -> list[Path]: ...
def val_input_path(value: Path | str | Iterable[Path | str]) -> Path | list[Path]:
    """Validate input file path(s) and make them absolute.

    Arguments:
        value: Path or paths to input files
    Returns:
        Validated path or paths
    Raises:
        FileNotFoundError: If any file does not exist
        NotAFileError: If any path is not a file
        TypeError: If any value cannot be cast to Path
    """

    def _val_input_path(value_to_validate: Path | str) -> Path:
        """Validate a path.

        Arguments:
            value_to_validate: Path to validate
        Returns:
            Validated path
        Raises:
            FileNotFoundError: If path does not exist
            NotAFileError: If path is not a file
            TypeError: If value cannot be cast to Path
        """
        try:
            validated_value = Path(
                expandvars(expanduser(str(value_to_validate)))
            ).resolve()
        except ValueError as exc:
            raise TypeError(
                f"{value_to_validate} is of type "
                f"{type(value_to_validate)}, cannot be cast to Path"
            ) from exc
        if not validated_value.exists():
            raise FileNotFoundError(f"Input file {validated_value} does not exist")
        if not validated_value.is_file():
            raise NotAFileError(f"Input file {validated_value} is not a file")
        return validated_value

    # Handle non-iterables and iterables we don't want to iterate over
    if isinstance(value, Path | str) or not isinstance(value, Iterable):
        return _val_input_path(value)

    # Handle iterables
    return [_val_input_path(value_to_validate) for value_to_validate in value]


@overload
def val_int(
    value: int,
    *,
    n_values: int | None = None,
    min_value: int | None = None,
    max_value: int | None = None,
    acceptable_values: Collection[int] | None = None,
) -> int: ...
@overload
def val_int(
    value: Iterable[Any],
    *,
    n_values: int | None = None,
    min_value: int | None = None,
    max_value: int | None = None,
    acceptable_values: Collection[int] | None = None,
) -> list[int]: ...
def val_int(
    value: int | Iterable[Any],
    *,
    n_values: int | None = None,
    min_value: int | None = None,
    max_value: int | None = None,
    acceptable_values: Collection[int] | None = None,
) -> int | list[int]:
    """Validate one or more ints.

    Arguments:
        value: Single value or iterable of values to validate
        n_values: Number of values expected, if applicable
        min_value: Minimum value of int, if applicable
        max_value: Maximum value of int, if applicable
        acceptable_values: Acceptable int values, if applicable
    Returns:
        Single int or list of ints depending on input
    Raises:
        ArgumentConflictError: If min_value is greater than max_value
        TypeError: If a value may not be cast to an int
        ValueError: If a value is invalid or the list is the wrong length
    """
    if min_value is not None and max_value is not None and (min_value >= max_value):
        raise ArgumentConflictError("min_value must be less than max_value")

    def _val_int(value_to_validate: Any) -> int:
        """Validate a single value as an int.

        Arguments:
            value_to_validate: Value to validate
        Returns:
            Value as an int
        """
        try:
            validated_value = int(value_to_validate)
        except ValueError as exc:
            raise TypeError(
                f"{value_to_validate} is of type "
                f"{type(value_to_validate)}, cannot be cast to int"
            ) from exc
        if min_value is not None and validated_value < min_value:
            raise ValueError(
                f"{validated_value} is less than minimum value of {min_value}"
            )
        if max_value is not None and validated_value > max_value:
            raise ValueError(
                f"{validated_value} is greater than maximum value of {max_value}"
            )
        if acceptable_values is not None and validated_value not in acceptable_values:
            raise ValueError(f"{validated_value} is not one of {acceptable_values}")
        return validated_value

    # Handle non-iterables and iterables we don't want to iterate over
    if isinstance(value, str) or not isinstance(value, Iterable):
        return _val_int(value)

    # Handle iterables
    validated_values = [_val_int(value_to_validate) for value_to_validate in value]
    if n_values is not None and len(validated_values) != n_values:
        raise ValueError(
            f"'{validated_values}' is of length {len(validated_values)}, "
            f"not '{n_values}'"
        )
    return validated_values


@overload
def val_output_dir_path(value: Path | str) -> Path: ...
@overload
def val_output_dir_path(value: Iterable[Path | str]) -> list[Path]: ...
def val_output_dir_path(value: Path | str | Iterable[Path | str]) -> Path | list[Path]:
    """Validate output directory path(s), make them absolute, and create them if needed.

    Arguments:
        value: Path or paths to output directories
    Returns:
        Validated path or paths
    Raises:
        NotADirectoryError: If any path is not a directory
        TypeError: If any value cannot be cast to Path
    """

    def _val_output_dir_path(value_to_validate: Path | str) -> Path:
        """Validate a path.

        Arguments:
            value_to_validate: Path to validate
        Returns:
            Validated path
        Raises:
            FileExistsError: If path already exists
            NotADirectoryError: If path is not a directory
            TypeError: If value cannot be cast to Path
        """
        try:
            validated_value = Path(
                expandvars(expanduser(str(value_to_validate)))
            ).resolve()
        except ValueError as exc:
            raise TypeError(
                f"{value_to_validate} is of type "
                f"{type(value_to_validate)}, cannot be cast to Path"
            ) from exc
        if not validated_value.exists():
            validated_value.mkdir(parents=True)
            info(f"Created directory {validated_value}")
            return validated_value
        if not validated_value.is_dir():
            raise NotADirectoryError(f"{validated_value} is not a directory")
        return validated_value

    # Handle non-iterables and iterables we don't want to iterate over
    if isinstance(value, Path | str) or not isinstance(value, Iterable):
        return _val_output_dir_path(value)

    # Handle iterables
    return [_val_output_dir_path(v) for v in value]


@overload
def val_output_path(value: Path | str, exist_ok: bool = False) -> Path: ...
@overload
def val_output_path(
    value: Iterable[Path | str], exist_ok: bool = False
) -> list[Path]: ...
def val_output_path(
    value: Path | str | Iterable[Path | str], exist_ok: bool = False
) -> Path | list[Path]:
    """Validate output file path(s) and make them absolute.

    Arguments:
        value: Path or paths to output files
        exist_ok: Whether to allow output files to already exist
    Returns:
        Validated path or paths
    Raises:
        FileExistsError: If the file exists and exist_ok is False
        NotAFileError: If a path exists and is not a file
        TypeError: If any value cannot be cast to a Path
    """

    def _val_output_path(value_to_validate: Path | str) -> Path:
        """Validate a path.

        Arguments:
            value_to_validate: Path to validate
        Returns:
            Validated path
        Raises:
            FileExistsError: If file exists and exist_ok is False
            TypeError: If value cannot be cast to a Path
        """
        try:
            validated_value = Path(
                expandvars(expanduser(str(value_to_validate)))
            ).resolve()
        except ValueError as exc:
            raise TypeError(
                f"{value_to_validate} is of type "
                f"{type(value_to_validate)}, cannot be cast to Path"
            ) from exc
        if validated_value.exists() and not exist_ok:
            raise FileExistsError(f"Output file {validated_value} already exists")
        if not validated_value.parent.exists():
            validated_value.parent.mkdir(parents=True)
            info(f"Created directory {validated_value.parent}")
        return validated_value

    # Handle non-iterables and iterables we don't want to iterate over
    if isinstance(value, Path | str) or not isinstance(value, Iterable):
        return _val_output_path(value)

    # Handle iterables
    return [_val_output_path(value_to_validate) for value_to_validate in value]


def val_str(value: Any, options: Iterable[str]) -> str:
    """Validate a str.

    Arguments:
        value: Input value to validate
        options: Acceptable string values, if applicable
    Returns:
        Value as a str
    Raises:
        ArgumentConflictError: If an option cannot be cast to a string
        TypeError: If value may not be cast to a str
        ValueError: If value is not one of the provided options
    """
    case_insensitive_options = {}
    for option in options:
        try:
            validated_option = str(option)
        except ValueError:
            raise ArgumentConflictError(
                f"Option '{option}' is of type '{type(option)}', not str"
            ) from None
        case_insensitive_options[validated_option.lower()] = validated_option

    try:
        value = str(value)
    except ValueError:
        raise TypeError(f"'{value}' is of type '{type(value)}', not str") from None
    value = value.lower()

    if value not in case_insensitive_options:
        raise ValueError(
            f"'{value}' is not one of options '{case_insensitive_options.keys()}'"
        ) from None

    return case_insensitive_options[value]


__all__ = [
    "val_executable",
    "val_float",
    "val_input_dir_path",
    "val_input_path",
    "val_int",
    "val_output_dir_path",
    "val_output_path",
    "val_str",
]
