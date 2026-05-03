#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Testing utilities."""

from __future__ import annotations

import sys
from contextlib import redirect_stderr, redirect_stdout
from ctypes import POINTER, byref, c_int, c_void_p, c_wchar_p
from inspect import getfile
from io import StringIO
from os import name as os_name
from pathlib import Path
from shlex import split
from unittest.mock import patch

from .command_line_interface import CommandLineInterface

CliTuple = tuple[type[CommandLineInterface], ...]
"""CLI class tuple with optional subcommands."""

__all__ = [
    "assert_cli_help",
    "assert_cli_usage",
    "build_subcommands",
    "get_usage_prefix",
    "run_cli_with_args",
]


def assert_cli_help(cli: CliTuple):
    """Assert that a CLI tuple shows help text.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    import pytest  # noqa: PLC0415

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


def assert_cli_usage(cli: CliTuple):
    """Assert that a CLI tuple shows usage on missing args.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    import pytest  # noqa: PLC0415

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


def build_subcommands(cli: CliTuple) -> str:
    """Build subcommand string for a CLI tuple.

    Arguments:
        cli: CLI class tuple with optional subcommands
    Returns:
        subcommand string to append to the base CLI
    """
    return " ".join(f"{command.name()}" for command in cli[1:])


def get_usage_prefix(cli: CliTuple) -> str:
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


def run_cli_with_args(cli: type[CommandLineInterface], args: str = ""):
    """Run CommandLineInterface as if from shell with provided args.

    Arguments:
        cli: CommandLineInterface to run
        args: Arguments to pass
    """
    with patch.object(sys, "argv", [getfile(cli)] + _split_cli_args(args)):
        cli.main()


def _split_cli_args(args: str) -> list[str]:
    """Split command-line arguments using platform-appropriate rules.

    Arguments:
        args: command-line argument string
    Returns:
        split command-line arguments
    """
    args = args.strip()
    if not args:
        return []
    if os_name != "nt":
        return split(args)

    from ctypes import WinDLL  # noqa: PLC0415

    argc = c_int()
    shell32 = WinDLL("shell32", use_last_error=True)
    shell32.CommandLineToArgvW.argtypes = [c_wchar_p, POINTER(c_int)]
    shell32.CommandLineToArgvW.restype = POINTER(c_wchar_p)
    kernel32 = WinDLL("kernel32", use_last_error=True)
    kernel32.LocalFree.argtypes = [c_void_p]
    kernel32.LocalFree.restype = c_void_p

    argv = shell32.CommandLineToArgvW(f"pipescaler-test {args}", byref(argc))
    if not argv:
        return []
    try:
        return [argv[index] for index in range(1, argc.value)]
    finally:
        kernel32.LocalFree(argv)
