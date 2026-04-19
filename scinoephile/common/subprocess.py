#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subprocess-related utility functions."""

from __future__ import annotations

from collections.abc import Iterable
from logging import getLogger
from subprocess import PIPE, Popen, TimeoutExpired
from threading import Thread
from time import monotonic
from typing import IO

logger = getLogger(__name__)


def _decode_output(content: bytes) -> str:
    """Decode subprocess output bytes with UTF-8 fallback.

    Arguments:
        content: bytes to decode
    Returns:
        decoded text
    """
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("ISO-8859-1")


def run_command(
    command: list[str],
    timeout: int = 600,
    acceptable_exitcodes: Iterable[int] | None = None,
) -> tuple[int, str, str]:
    """Run a provided command.

    Arguments:
        command: command to run as a list of arguments
        timeout: maximum time to await command's completion
        acceptable_exitcodes: acceptable exit codes
    Returns:
        exitcode, standard output, and standard error
    Raises:
        ValueError: If exitcode is not one of acceptable_exitcodes
    """
    if acceptable_exitcodes is None:
        acceptable_exitcodes = [0]

    with Popen(command, stdout=PIPE, stderr=PIPE) as child:
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
            command_str = " ".join(command)
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
    command: list[str],
    timeout: int | None = 43200,
    acceptable_exitcodes: Iterable[int] | None = None,
) -> tuple[int, str, str]:
    """Run a provided command and stream output live.

    Arguments:
        command: command to run as a list of arguments
        timeout: Maximum time to await command's completion
        acceptable_exitcodes: Acceptable exit codes
    Returns:
        exitcode, standard output, and standard error
    Raises:
        ValueError: If exitcode is not one of acceptable_exitcodes
    """
    if acceptable_exitcodes is None:
        acceptable_exitcodes = [0]

    stdout_lines = []
    stderr_lines = []

    def read_stream(stream: IO[bytes], lines: list[str]):
        """Read subprocess stream line-by-line and mirror to logs.

        Arguments:
            stream: stream to read from
            lines: list that collects the stream content
        """
        for line in iter(stream.readline, b""):
            decoded_line = _decode_output(line)
            logger.info(decoded_line.rstrip())
            lines.append(decoded_line)
        stream.close()

    with Popen(
        command,
        stdout=PIPE,
        stderr=PIPE,
        bufsize=0,
    ) as child:
        assert child.stdout is not None
        assert child.stderr is not None
        stdout_thread = Thread(target=read_stream, args=(child.stdout, stdout_lines))
        stderr_thread = Thread(target=read_stream, args=(child.stderr, stderr_lines))
        stdout_thread.start()
        stderr_thread.start()

        if timeout is None:
            exitcode = child.wait()
        else:
            deadline = monotonic() + timeout
            try:
                exitcode = child.wait(timeout=max(0.0, deadline - monotonic()))
            except TimeoutExpired as exception:
                child.kill()
                child.wait()
                stdout_thread.join()
                stderr_thread.join()
                stdout_str = "".join(stdout_lines)
                stderr_str = "".join(stderr_lines)
                raise TimeoutExpired(
                    command,
                    timeout,
                    output=stdout_str,
                    stderr=stderr_str,
                ) from exception

            stdout_thread.join(timeout=max(0.0, deadline - monotonic()))
            stderr_thread.join(timeout=max(0.0, deadline - monotonic()))
            if stdout_thread.is_alive() or stderr_thread.is_alive():
                child.kill()
                child.wait()
                stdout_thread.join()
                stderr_thread.join()
                stdout_str = "".join(stdout_lines)
                stderr_str = "".join(stderr_lines)
                raise TimeoutExpired(
                    command,
                    timeout,
                    output=stdout_str,
                    stderr=stderr_str,
                )

        if timeout is None:
            stdout_thread.join()
            stderr_thread.join()

        stdout_str = "".join(stdout_lines)
        stderr_str = "".join(stderr_lines)

        if exitcode not in acceptable_exitcodes:
            command_str = " ".join(command)
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
