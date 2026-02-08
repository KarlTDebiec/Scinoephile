#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subprocess-related utility functions."""

from __future__ import annotations

import shlex
import warnings
from collections.abc import Iterable
from logging import getLogger
from subprocess import PIPE, Popen, TimeoutExpired
from threading import Thread

logger = getLogger(__name__)


def run_command(
    command: list[str] | str,
    timeout: int = 600,
    acceptable_exitcodes: Iterable[int] | None = None,
) -> tuple[int, str, str]:
    """Run a provided command.

    Arguments:
        command: command to run as a list of arguments (preferred) or a string
            (deprecated). When provided as a string, it will be parsed using
            shlex.split() for safety. Using strings is deprecated and will be
            removed in a future version.
        timeout: maximum time to await command's completion
        acceptable_exitcodes: acceptable exit codes
    Returns:
        exitcode, standard output, and standard error
    Raises:
        ValueError: If exitcode is not one of acceptable_exitcodes
    """
    if acceptable_exitcodes is None:
        acceptable_exitcodes = [0]

    # Handle backward compatibility for string commands
    if isinstance(command, str):
        warnings.warn(
            "Passing command as a string is deprecated and will be removed in a "
            "future version. Please pass command as a list of arguments instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        command_list = shlex.split(command)
    else:
        command_list = command

    with Popen(command_list, stdout=PIPE, stderr=PIPE) as child:
        try:
            stdout, stderr = child.communicate(timeout=timeout)
        except TimeoutExpired:
            child.kill()
            stdout, stderr = child.communicate()

        try:
            stdout_str = stdout.decode("utf-8")
        except UnicodeDecodeError:
            stdout_str = stdout.decode("ISO-8859-1")

        try:
            stderr_str = stderr.decode("utf-8")
        except UnicodeDecodeError:
            stderr_str = stderr.decode("ISO-8859-1")

        exitcode = child.returncode

        if exitcode not in acceptable_exitcodes:
            # Format command for error message
            if isinstance(command, str):
                command_str = command
            else:
                command_str = " ".join(command_list)
            raise ValueError(
                f"subprocess for command:\n"
                f"{command_str}\n\n"
                f"failed with exit code {exitcode};\n\n"
                f"STDOUT:\n"
                f"{stdout_str}\n\n"
                f"STDERR:\n"
                f"{stderr_str}"
            )

    return exitcode, stdout_str, stderr_str


def run_command_live(
    command: list[str] | str,
    timeout: int | None = 43200,
    acceptable_exitcodes: Iterable[int] | None = None,
) -> tuple[int, str, str]:
    """Run a provided command and stream output live.

    Arguments:
        command: command to run as a list of arguments (preferred) or a string
            (deprecated). When provided as a string, it will be parsed using
            shlex.split() for safety. Using strings is deprecated and will be
            removed in a future version.
        timeout: Maximum time to await command's completion
        acceptable_exitcodes: Acceptable exit codes
    Returns:
        exitcode, standard output, and standard error
    Raises:
        ValueError: If exitcode is not one of acceptable_exitcodes
    """
    if acceptable_exitcodes is None:
        acceptable_exitcodes = [0]

    # Handle backward compatibility for string commands
    if isinstance(command, str):
        warnings.warn(
            "Passing command as a string is deprecated and will be removed in a "
            "future version. Please pass command as a list of arguments instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        command_list = shlex.split(command)
    else:
        command_list = command

    stdout_lines = []
    stderr_lines = []

    def read_stream(stream, lines):
        for line in iter(stream.readline, ""):
            logger.info(line.rstrip())
            lines.append(line)
        stream.close()

    with Popen(
        command_list,
        stdout=PIPE,
        stderr=PIPE,
        text=True,
        bufsize=0,
        encoding="utf-8",
    ) as child:
        stdout_thread = Thread(target=read_stream, args=(child.stdout, stdout_lines))
        stderr_thread = Thread(target=read_stream, args=(child.stderr, stderr_lines))
        stdout_thread.start()
        stderr_thread.start()
        stdout_thread.join(timeout)
        stderr_thread.join(timeout)

        exitcode = child.wait(timeout)

        stdout_str = "".join(stdout_lines)
        stderr_str = "".join(stderr_lines)

        if exitcode not in acceptable_exitcodes:
            # Format command for error message
            if isinstance(command, str):
                command_str = command
            else:
                command_str = " ".join(command_list)
            raise ValueError(
                f"subprocess for command:\n"
                f"{command_str}\n\n"
                f"failed with exit code {exitcode};\n\n"
                f"STDOUT:\n"
                f"{stdout_str}\n\n"
                f"STDERR:\n"
                f"{stderr_str}"
            )

    return exitcode, stdout_str, stderr_str


__all__ = [
    "run_command",
    "run_command_live",
]
