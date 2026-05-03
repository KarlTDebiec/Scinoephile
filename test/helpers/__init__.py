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

import pytest
from pytest import fixture, mark

from scinoephile.common import CommandLineInterface, package_root
from scinoephile.common.testing import run_cli_with_args

from .series_cer_result import SeriesCERResult

__all__ = [
    "SeriesCERResult",
    "assert_cli_help",
    "assert_cli_usage",
    "assert_expected_warnings",
    "build_subcommands",
    "get_warning_messages",
    "get_usage_prefix",
    "parametrized_fixture",
    "skip_if_ci",
    "skip_if_codex",
    "test_data_root",
]


test_data_root = package_root.parent / "test" / "data"


def assert_cli_help(cli: tuple[type[CommandLineInterface], ...]):
    """Assert that a CLI tuple shows help text.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    subcommands = build_subcommands(cli)
    stdout = StringIO()
    stderr = StringIO()
    with pytest.raises(SystemExit) as excinfo:
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
    with pytest.raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(cli[0], subcommands)
    assert excinfo.value.code == 2
    assert stdout.getvalue() == ""
    assert stderr.getvalue().startswith(get_usage_prefix(cli))


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


def parametrized_fixture(cls: type, params: list[dict[str, Any]]):
    """Decorator for parametrized test fixtures which provides clearer test output.

    Arguments:
        cls: stage fixture class
        params: fixture parameters
    Returns:
        fixture with provided params and clear ids
    """

    def get_name(args):
        """Build pytest parameter id for fixture output."""
        return f"{cls.__name__}({','.join(map(str, args.values()))})"

    return partial(fixture, params=params, ids=get_name)


def skip_if_ci() -> Any:
    """Build a decorator that skips tests in continuous integration.

    Returns:
        pytest mark decorator
    """
    return mark.skipif(
        bool(getenv("CI")),
        reason="Skip when running in CI",
    )


def skip_if_codex() -> Any:
    """Build a decorator that skips tests in Codex.

    Returns:
        pytest mark decorator
    """
    return mark.skipif(
        bool(getenv("CODEX_ENV_PYTHON_VERSION")),
        reason="Skip when running in Codex environment",
    )
