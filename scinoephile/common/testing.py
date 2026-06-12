#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Testing utilities."""

from __future__ import annotations

import ctypes
import sys
from ctypes import POINTER, byref, c_int, c_void_p, c_wchar_p
from inspect import getfile
from platform import system
from shlex import split
from unittest.mock import patch

from .command_line_interface import CommandLineInterface

__all__ = [
    "echo_command",
    "run_cli_with_args",
]


def echo_command(*arguments: str) -> list[str]:
    """Build a portable command that echoes arguments without shell expansion.

    Arguments:
        *arguments: arguments to echo
    Returns:
        command argument list
    """
    return [
        sys.executable,
        "-c",
        (
            "import sys; "
            "sys.stdout.reconfigure(encoding='utf-8'); "
            "print(' '.join(sys.argv[1:]))"
        ),
        *arguments,
    ]


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
    if system() != "Windows":
        return split(args)

    argc = c_int()
    win_dll = getattr(ctypes, "WinDLL")
    shell32 = win_dll("shell32", use_last_error=True)
    shell32.CommandLineToArgvW.argtypes = [c_wchar_p, POINTER(c_int)]
    shell32.CommandLineToArgvW.restype = POINTER(c_wchar_p)
    kernel32 = win_dll("kernel32", use_last_error=True)
    kernel32.LocalFree.argtypes = [c_void_p]
    kernel32.LocalFree.restype = c_void_p

    argv = shell32.CommandLineToArgvW(f"pipescaler-test {args}", byref(argc))
    if not argv:
        return []
    try:
        return [argv[index] for index in range(1, argc.value)]
    finally:
        kernel32.LocalFree(argv)
