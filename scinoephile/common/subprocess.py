#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subprocess-related utility functions."""

from __future__ import annotations

import ctypes
import os
import signal
import sys
from collections.abc import Iterable, Mapping
from importlib import import_module
from logging import getLogger
from os import read, set_blocking
from pathlib import Path
from subprocess import PIPE, Popen, TimeoutExpired
from threading import Event, Thread
from time import monotonic
from typing import IO

__all__ = ["run_command", "run_command_live"]

logger = getLogger(__name__)
_CLEANUP_TIMEOUT = 1.0


def run_command(
    command: list[str],
    timeout: float = 600,
    acceptable_exitcodes: Iterable[int] | None = None,
    *,
    cwd_path: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> tuple[int, str, str]:
    """Run an argument list without a shell and capture its output.

    On timeout, terminate the command's process group or Windows job and cancel
    output readers after bounded cleanup. The resulting exit code is checked normally;
    the command deadline does not raise TimeoutExpired. Output uses UTF-8 with
    ISO-8859-1 fallback.

    Arguments:
        command: command to run as a list of arguments
        timeout: seconds to wait before killing the child; defaults to 600
        acceptable_exitcodes: allowed exit codes; defaults to [0]
        cwd_path: working directory; None inherits the current directory
        env: complete child environment; None inherits the current environment
    Returns:
        exitcode, standard output, and standard error
    Raises:
        OSError: if the child cannot be started or assigned to a Windows job
        TimeoutExpired: if cleanup cannot reap the direct child within its deadline
        ValueError: if the exit code is not accepted, including after a timeout
    """
    if acceptable_exitcodes is None:
        acceptable_exitcodes = [0]

    child = Popen(
        command,
        stdout=PIPE,
        stderr=PIPE,
        cwd=cwd_path,
        env=env,
        bufsize=0,
        start_new_session=os.name != "nt",
    )
    stdout_str, stderr_str = _collect_output(child, timeout, live=False)
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
    timeout: float | None = 86400,
    acceptable_exitcodes: Iterable[int] | None = None,
    *,
    cwd_path: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> tuple[int, str, str]:
    """Run an argument list and log both output streams at INFO level.

    Both streams are also captured and returned as text, decoded as UTF-8 with
    ISO-8859-1 fallback. Newlines and carriage returns delimit live log records.
    On timeout, terminate the command's process group or Windows job, cancel output
    readers after bounded cleanup, and raise TimeoutExpired with captured text in
    output and stderr.

    Arguments:
        command: command to run as a list of arguments
        timeout: seconds allowed for process exit and stream readers to finish;
          defaults to 86400; None disables the deadline
        acceptable_exitcodes: allowed exit codes; defaults to [0]
        cwd_path: working directory; None inherits the current directory
        env: complete child environment; None inherits the current environment
    Returns:
        exitcode, standard output, and standard error
    Raises:
        OSError: if the child cannot be started or assigned to a Windows job
        TimeoutExpired: if the process or its output readers exceed the deadline
        ValueError: if the exit code is not accepted
    """
    if acceptable_exitcodes is None:
        acceptable_exitcodes = [0]

    child = Popen(
        command,
        stdout=PIPE,
        stderr=PIPE,
        cwd=cwd_path,
        env=env,
        bufsize=0,
        start_new_session=os.name != "nt",
    )
    stdout_str, stderr_str = _collect_output(child, timeout, live=True)
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


def _collect_output(
    child: Popen[bytes], timeout: float | None, *, live: bool
) -> tuple[str, str]:
    """Collect both streams within the command deadline and bound cleanup.

    Arguments:
        child: process whose output and lifetime are owned by this call
        timeout: command deadline in seconds, or None to disable it
        live: whether output records are mirrored to logs
    Returns:
        captured standard output and standard error
    Raises:
        OSError: if pipe setup or process cleanup fails
        TimeoutExpired: if a live command exceeds its deadline or cleanup cannot reap
          the direct child within the cleanup window
    """
    assert child.stdout is not None
    assert child.stderr is not None
    stdout_chunks: list[bytes] = []
    stderr_chunks: list[bytes] = []
    stop_event = Event()
    readers: list[Thread] = []
    completed = False
    job: _WindowsJob | None = None
    deadline = None
    if timeout is not None:
        deadline = monotonic() + timeout
    try:
        if os.name == "nt":
            job = _WindowsJob(child)
        for label, stream, chunks in (
            ("stdout", child.stdout, stdout_chunks),
            ("stderr", child.stderr, stderr_chunks),
        ):
            set_blocking(stream.fileno(), False)
            reader = Thread(
                target=_read_stream,
                args=(stream, chunks, stop_event),
                kwargs={"live": live},
                name=f"subprocess-reader-{label}-{child.pid}",
                daemon=True,
            )
            reader.start()
            readers.append(reader)
        completed = _wait_for_output(child, readers, deadline)
    finally:
        try:
            if not completed:
                _terminate_process_tree(child, job)
        finally:
            try:
                stop_event.set()
                cleanup_deadline = monotonic() + _CLEANUP_TIMEOUT
                for reader in readers:
                    reader.join(timeout=max(0.0, cleanup_deadline - monotonic()))
                child.stdout.close()
                child.stderr.close()
            finally:
                if job is not None:
                    job.close()
    stdout = _decode_output(b"".join(stdout_chunks))
    stderr = _decode_output(b"".join(stderr_chunks))
    if not completed and live:
        assert timeout is not None
        raise TimeoutExpired(child.args, timeout, output=stdout, stderr=stderr)
    return stdout, stderr


def _decode_output(content: bytes) -> str:
    """Decode UTF-8 output, falling back to ISO-8859-1 for invalid UTF-8.

    Arguments:
        content: bytes to decode
    Returns:
        decoded text
    """
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("ISO-8859-1")


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


def _read_stream(
    stream: IO[bytes], chunks: list[bytes], stop_event: Event, *, live: bool
):
    """Capture a nonblocking stream, optionally logging records, until EOF or cancel.

    Arguments:
        stream: subprocess output stream
        chunks: captured byte chunks
        stop_event: cancellation request that bounds draining pending bytes
        live: whether complete records are mirrored to logs
    """
    pending = b""
    drain_reads = 0
    try:
        while True:
            try:
                chunk = read(stream.fileno(), 4096)
            except BlockingIOError:
                if stop_event.is_set():
                    break
                stop_event.wait(0.05)
                continue
            if not chunk:
                break
            chunks.append(chunk)
            if live:
                pending = _log_live_records(pending + chunk)
            if stop_event.is_set():
                # Limit draining when an inherited pipe still has an active writer
                drain_reads += 1
                if drain_reads >= 16:
                    break
        if live and pending:
            logger.info(_decode_output(pending))
    finally:
        stream.close()


def _terminate_process_tree(child: Popen[bytes], job: _WindowsJob | None):
    """Terminate the owned process group or job, then reap the direct child.

    Arguments:
        child: direct child whose process group or job is owned by this call
        job: Windows job, or None for a POSIX group or failed Windows setup
    Raises:
        OSError: if process-tree termination fails
        TimeoutExpired: if cleanup cannot reap the direct child within its deadline
    """
    try:
        if job is not None:
            job.terminate()
        elif os.name != "nt":
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    finally:
        if child.poll() is None:
            child.kill()
        child.wait(timeout=_CLEANUP_TIMEOUT)


def _wait_for_output(
    child: Popen[bytes], readers: list[Thread], deadline: float | None
) -> bool:
    """Wait for the direct child and output readers within one deadline.

    Arguments:
        child: direct child process
        readers: threads collecting standard output and standard error
        deadline: monotonic deadline, or None to wait without a timeout
    Returns:
        whether both the child and its readers finish before the deadline
    """
    try:
        remaining = None
        if deadline is not None:
            remaining = max(0.0, deadline - monotonic())
        child.wait(timeout=remaining)
        for reader in readers:
            remaining = None
            if deadline is not None:
                remaining = max(0.0, deadline - monotonic())
            reader.join(timeout=remaining)
    except TimeoutExpired:
        return False
    return not any(reader.is_alive() for reader in readers)


class _WindowsJob:
    """Own the native Windows job used to terminate a command and its descendants."""

    def __init__(self, child: Popen[bytes]):
        """Create a job and associate the direct child with it.

        Assignment follows process startup. Children created before assignment can
        escape the job, so output readers still require bounded cancellation.

        Arguments:
            child: newly started Windows command
        Raises:
            OSError: if a job cannot be created or the running child cannot be assigned
        """
        if sys.platform != "win32":
            raise OSError("Windows Job Objects require Windows")
        api = ctypes.WinDLL("kernel32", use_last_error=True)
        wintypes = import_module("ctypes.wintypes")
        for name, restype, argtypes in (
            ("CreateJobObjectW", wintypes.HANDLE, (wintypes.LPVOID, wintypes.LPCWSTR)),
            (
                "OpenProcess",
                wintypes.HANDLE,
                (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD),
            ),
            (
                "AssignProcessToJobObject",
                wintypes.BOOL,
                (wintypes.HANDLE, wintypes.HANDLE),
            ),
            ("TerminateJobObject", wintypes.BOOL, (wintypes.HANDLE, wintypes.UINT)),
            ("CloseHandle", wintypes.BOOL, (wintypes.HANDLE,)),
        ):
            function = getattr(api, name)
            function.restype = restype
            function.argtypes = argtypes
        self._api = api
        self._handle = api.CreateJobObjectW(None, None)
        if not self._handle:
            raise ctypes.WinError(ctypes.get_last_error())
        process_handle = api.OpenProcess(0x0101, False, child.pid)
        try:
            if not process_handle or not api.AssignProcessToJobObject(
                self._handle, process_handle
            ):
                error = ctypes.get_last_error()
                if child.poll() is not None:
                    self.close()
                    return
                raise ctypes.WinError(error)
        except BaseException:
            self.close()
            raise
        finally:
            if process_handle:
                api.CloseHandle(process_handle)

    def close(self):
        """Release the owned native job handle."""
        if sys.platform == "win32" and self._handle:
            self._api.CloseHandle(self._handle)
            self._handle = None

    def terminate(self):
        """Terminate processes associated with this job.

        Raises:
            OSError: if Windows cannot terminate the job
        """
        if sys.platform != "win32":
            raise OSError("Windows Job Objects require Windows")
        if self._handle and not self._api.TerminateJobObject(self._handle, 1):
            raise ctypes.WinError(ctypes.get_last_error())
