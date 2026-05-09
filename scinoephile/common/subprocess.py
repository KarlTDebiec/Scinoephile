#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subprocess-related utility functions."""

from __future__ import annotations

from collections.abc import Iterable
from os import read
from queue import Empty, Queue
from subprocess import PIPE, Popen, TimeoutExpired
from sys import stderr, stdout
from threading import Thread
from time import monotonic
from typing import IO


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

    chunks: dict[str, list[bytes]] = {"stdout": [], "stderr": []}
    output_queue: Queue[tuple[str, bytes | None]] = Queue()

    with Popen(
        command,
        stdout=PIPE,
        stderr=PIPE,
        bufsize=0,
    ) as child:
        assert child.stdout is not None
        assert child.stderr is not None

        stdout_thread = Thread(
            target=_read_stream, args=(child.stdout, "stdout", output_queue)
        )
        stderr_thread = Thread(
            target=_read_stream, args=(child.stderr, "stderr", output_queue)
        )
        stdout_thread.start()
        stderr_thread.start()

        timed_out = _monitor_live_output(child, timeout, output_queue, chunks)
        stdout_thread.join()
        stderr_thread.join()

        stdout_str = _decode_output(b"".join(chunks["stdout"]))
        stderr_str = _decode_output(b"".join(chunks["stderr"]))

        exitcode = child.returncode
        assert exitcode is not None
        if timed_out and timeout is not None:
            raise TimeoutExpired(
                command,
                timeout,
                output=stdout_str,
                stderr=stderr_str,
            )

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


def _monitor_live_output(
    child: Popen[bytes],
    timeout: int | None,
    output_queue: Queue[tuple[str, bytes | None]],
    chunks: dict[str, list[bytes]],
) -> bool:
    """Monitor subprocess output and return whether it timed out.

    Arguments:
        child: child process to monitor
        timeout: maximum idle time since the last output
        output_queue: queue containing stream output chunks
        chunks: collected output chunks by stream name
    Returns:
        whether the process timed out
    """
    last_output_time = monotonic()
    open_stream_names = {"stdout", "stderr"}
    timed_out = False

    while open_stream_names or child.poll() is None:
        if timeout is None or child.poll() is not None:
            queue_timeout = 0.1
        else:
            queue_timeout = max(0.0, timeout - (monotonic() - last_output_time))

        try:
            stream_name, chunk = output_queue.get(timeout=queue_timeout)
        except Empty:
            if timeout is not None and child.poll() is None:
                timed_out = True
                child.kill()
                child.wait()
            continue

        if chunk is None:
            open_stream_names.discard(stream_name)
            continue

        chunks[stream_name].append(chunk)
        _write_live_output(stream_name, chunk)
        last_output_time = monotonic()

    while not output_queue.empty():
        stream_name, chunk = output_queue.get_nowait()
        if chunk is not None:
            chunks[stream_name].append(chunk)
            _write_live_output(stream_name, chunk)

    child.wait()
    return timed_out


def _read_stream(
    stream: IO[bytes],
    stream_name: str,
    output_queue: Queue[tuple[str, bytes | None]],
):
    """Read subprocess stream chunks into the output queue.

    Arguments:
        stream: stream to read from
        stream_name: name of stream being read
        output_queue: queue that receives stream output chunks
    """
    try:
        while chunk := read(stream.fileno(), 4096):
            output_queue.put((stream_name, chunk))
    finally:
        output_queue.put((stream_name, None))


def _write_live_output(stream_name: str, chunk: bytes):
    """Write subprocess output chunk to the matching parent stream.

    Arguments:
        stream_name: name of stream that produced the chunk
        chunk: output chunk to write
    """
    output = _decode_output(chunk)
    if stream_name == "stderr":
        stderr.write(output)
        stderr.flush()
    else:
        stdout.write(output)
        stdout.flush()


__all__ = [
    "run_command",
    "run_command_live",
]
