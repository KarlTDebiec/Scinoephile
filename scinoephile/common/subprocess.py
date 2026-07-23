#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subprocess-related utility functions."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from logging import getLogger
from os import read
from pathlib import Path
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
    *,
    cwd_path: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> tuple[int, str, str]:
    """Run a provided command.

    Arguments:
        command: command to run as a list of arguments
        timeout: maximum time to await command's completion
        acceptable_exitcodes: acceptable exit codes
        cwd_path: working directory
        env: environment variables
    Returns:
        exitcode, standard output, and standard error
    Raises:
        ValueError: If exitcode is not one of acceptable_exitcodes
    """
    if acceptable_exitcodes is None:
        acceptable_exitcodes = [0]

    with Popen(command, stdout=PIPE, stderr=PIPE, cwd=cwd_path, env=env) as child:
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
    timeout: int | None = 86400,
    acceptable_exitcodes: Iterable[int] | None = None,
    *,
    cwd_path: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> tuple[int, str, str]:
    """Run a provided command and stream output live.

    Arguments:
        command: command to run as a list of arguments
        timeout: maximum time to await command's completion
        acceptable_exitcodes: acceptable exit codes
        cwd_path: working directory
        env: environment variables
    Returns:
        exitcode, standard output, and standard error
    Raises:
        ValueError: If exitcode is not one of acceptable_exitcodes
    """
    if acceptable_exitcodes is None:
        acceptable_exitcodes = [0]

    stdout_chunks = []
    stderr_chunks = []

    with Popen(
        command,
        stdout=PIPE,
        stderr=PIPE,
        cwd=cwd_path,
        env=env,
        bufsize=0,
    ) as child:
        assert child.stdout is not None
        assert child.stderr is not None
        stdout_thread = Thread(target=_read_stream, args=(child.stdout, stdout_chunks))
        stderr_thread = Thread(target=_read_stream, args=(child.stderr, stderr_chunks))
        stdout_thread.start()
        stderr_thread.start()

        exitcode = _wait_for_live_process(
            child,
            command,
            timeout,
            stdout_thread,
            stderr_thread,
            stdout_chunks,
            stderr_chunks,
        )

        stdout_str = _decode_output(b"".join(stdout_chunks))
        stderr_str = _decode_output(b"".join(stderr_chunks))

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


def _handle_live_timeout(
    child: Popen[bytes],
    command: list[str],
    timeout: int,
    stdout_thread: Thread,
    stderr_thread: Thread,
    stdout_chunks: list[bytes],
    stderr_chunks: list[bytes],
):
    """Handle live subprocess timeout.

    Arguments:
        child: child process
        command: command run by the child process
        timeout: timeout that was exceeded
        stdout_thread: thread reading standard output
        stderr_thread: thread reading standard error
        stdout_chunks: standard output chunks read so far
        stderr_chunks: standard error chunks read so far
    """
    child.kill()
    child.wait()
    stdout_thread.join()
    stderr_thread.join()
    raise TimeoutExpired(
        command,
        timeout,
        output=_decode_output(b"".join(stdout_chunks)),
        stderr=_decode_output(b"".join(stderr_chunks)),
    )


def _log_live_records(output: bytes) -> bytes:
    """Log complete live output records and return any incomplete remainder.

    Arguments:
        output: output bytes to log
    Returns:
        incomplete trailing output
    """
    record_start = 0
    for index, character in enumerate(output):
        if character not in {10, 13}:
            continue
        record = output[record_start:index]
        if record:
            logger.info(_decode_output(record))
        record_start = index + 1
    return output[record_start:]


def _read_stream(stream: IO[bytes], chunks: list[bytes]):
    """Read subprocess stream chunks and mirror records to logs.

    Arguments:
        stream: stream to read from
        chunks: list that collects the stream content
    """
    pending = b""
    try:
        while chunk := read(stream.fileno(), 4096):
            chunks.append(chunk)
            pending = _log_live_records(pending + chunk)
        if pending:
            logger.info(_decode_output(pending))
    finally:
        stream.close()


def _wait_for_live_process(
    child: Popen[bytes],
    command: list[str],
    timeout: int | None,
    stdout_thread: Thread,
    stderr_thread: Thread,
    stdout_chunks: list[bytes],
    stderr_chunks: list[bytes],
) -> int:
    """Wait for a live subprocess and its stream reader threads.

    Arguments:
        child: child process
        command: command run by the child process
        timeout: maximum time to await command's completion
        stdout_thread: thread reading standard output
        stderr_thread: thread reading standard error
        stdout_chunks: standard output chunks read so far
        stderr_chunks: standard error chunks read so far
    Returns:
        exitcode
    """
    if timeout is None:
        exitcode = child.wait()
        stdout_thread.join()
        stderr_thread.join()
        return exitcode

    deadline = monotonic() + timeout
    try:
        exitcode = child.wait(timeout=max(0.0, deadline - monotonic()))
    except TimeoutExpired as exception:
        try:
            _handle_live_timeout(
                child,
                command,
                timeout,
                stdout_thread,
                stderr_thread,
                stdout_chunks,
                stderr_chunks,
            )
        except TimeoutExpired as timeout_exception:
            raise timeout_exception from exception

    stdout_thread.join(timeout=max(0.0, deadline - monotonic()))
    stderr_thread.join(timeout=max(0.0, deadline - monotonic()))
    if stdout_thread.is_alive() or stderr_thread.is_alive():
        _handle_live_timeout(
            child,
            command,
            timeout,
            stdout_thread,
            stderr_thread,
            stdout_chunks,
            stderr_chunks,
        )
    return exitcode


__all__ = [
    "run_command",
    "run_command_live",
]
