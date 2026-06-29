#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared test utilities and pytest helper decorators."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from functools import partial
from inspect import getfile
from io import StringIO
from os import getenv
from pathlib import Path
from typing import Any

from pytest import fixture, mark, raises, skip

from scinoephile.common import CommandLineInterface, package_root
from scinoephile.common.testing import run_cli_with_args

from .series_assertions import assert_series_equal
from .series_cer_result import SeriesCERResult

parametrize = mark.parametrize
skipif = mark.skipif
__all__ = [
    "SeriesCERResult",
    "assert_cli_help",
    "assert_cli_usage",
    "assert_expected_warnings",
    "assert_series_equal",
    "build_subcommands",
    "create_symlink_or_skip",
    "get_warning_messages",
    "get_usage_prefix",
    "parametrize",
    "parametrized_fixture",
    "skip_if_ci",
    "skip_if_codex",
    "skipif",
    "test_data_root",
]

test_data_root = package_root.parent / "test/data"


def assert_cli_help(cli: tuple[type[CommandLineInterface], ...]):
    """Assert that a CLI tuple shows help text.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    subcommands = build_subcommands(cli)
    stdout = StringIO()
    stderr = StringIO()
    with raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(cli[0], f"{subcommands} -h".strip())
    assert excinfo.value.code == 0
    assert stdout.getvalue().startswith(get_usage_prefix(cli))
    assert stderr.getvalue() == ""


def assert_cli_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Assert that a CLI tuple shows usage on missing args.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    subcommands = build_subcommands(cli)
    stdout = StringIO()
    stderr = StringIO()
    with raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(cli[0], subcommands)
    assert excinfo.value.code == 2
    assert stdout.getvalue() == ""
    expected_usage_prefix = get_usage_prefix(cli)
    actual_stdout = stdout.getvalue()
    actual_stderr = stderr.getvalue()
    assert actual_stderr.startswith(expected_usage_prefix), (
        "Expected stderr to start with:\n"
        f"{expected_usage_prefix!r}\n"
        "Actual stderr:\n"
        f"{actual_stderr!r}\n"
        "Actual stdout:\n"
        f"{actual_stdout!r}"
    )


def assert_expected_warnings(warnings: list[str], expected: list[str], label: str):
    """Assert that warning messages match expected values.

    Arguments:
        warnings: warning messages captured during validation
        expected: expected warning messages
        label: label for error messages
    """
    if warnings != expected:
        formatted_actual = "\n".join(warnings)
        formatted_expected = "\n".join(expected)
        raise AssertionError(
            f"{label} warnings mismatch.\n"
            f"Expected:\n{formatted_expected}\n"
            f"Actual:\n{formatted_actual}"
        )


def build_subcommands(cli: tuple[type[CommandLineInterface], ...]) -> str:
    """Build subcommand string for a CLI tuple.

    Arguments:
        cli: CLI class tuple with optional subcommands
    Returns:
        subcommand string to append to the base CLI
    """
    return " ".join(f"{command.name()}" for command in cli[1:])


def create_symlink_or_skip(
    symlink_path: Path, target_path: Path, *, target_is_directory: bool = False
):
    """Create a symlink, skipping when Windows privileges do not allow it.

    Arguments:
        symlink_path: path at which to create the symlink
        target_path: symlink target path
        target_is_directory: whether the target is a directory
    """
    try:
        symlink_path.symlink_to(target_path, target_is_directory=target_is_directory)
    except OSError as exc:
        if getattr(exc, "winerror", None) == 1314:
            skip("Windows symlink privilege is not available")
        raise


def get_usage_prefix(cli: tuple[type[CommandLineInterface], ...]) -> str:
    """Get expected usage prefix for a CLI tuple.

    Arguments:
        cli: CLI class tuple with optional subcommands
    Returns:
        expected usage prefix
    """
    subcommands = build_subcommands(cli)
    prefix = f"usage: {Path(getfile(cli[0])).name}"
    if subcommands:
        return f"{prefix} {subcommands}"
    return prefix


def get_warning_messages(records: list[Any]) -> list[str]:
    """Collect warning messages from captured log records.

    Arguments:
        records: log records captured during validation
    Returns:
        list of warning messages
    """
    return [record.getMessage() for record in records]


def parametrized_fixture(cls: type, params: list[dict[str, Any]]) -> Any:
    """Decorator for parametrized test fixtures which provides clearer test output.

    Arguments:
        cls: stage fixture class
        params: fixture parameters
    Returns:
        fixture with provided params and clear ids
    """

    def get_name(args: dict[str, Any]) -> str:
        """Build pytest parameter id for fixture output.

        Arguments:
            args: fixture parameter mapping
        Returns:
            pytest parameter id
        """
        return f"{cls.__name__}({','.join(map(str, args.values()))})"

    return partial(fixture, params=params, ids=get_name)


def skip_if_ci() -> Any:
    """Build a decorator that skips tests in continuous integration.

    Returns:
        pytest mark decorator
    """
    return skipif(
        bool(getenv("CI")),
        reason="Skip when running in CI",
    )


def skip_if_codex() -> Any:
    """Build a decorator that skips tests in Codex.

    Returns:
        pytest mark decorator
    """
    return skipif(
        bool(getenv("CODEX_ENV_PYTHON_VERSION")),
        reason="Skip when running in Codex environment",
    )
