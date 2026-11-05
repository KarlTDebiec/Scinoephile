#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of captured and live subprocess execution."""

from __future__ import annotations

import ctypes
import os
import signal
import sys
from collections.abc import Callable, Generator
from contextlib import AbstractContextManager, contextmanager, nullcontext
from ctypes import wintypes
from pathlib import Path
from subprocess import Popen, TimeoutExpired
from threading import enumerate as enumerate_threads
from time import monotonic, sleep

from common import subprocess as subprocess_module
from common.subprocess import run_command, run_command_live
from common.testing import echo_command
from pytest import FixtureRequest, MonkeyPatch, fixture, mark, raises

_SUBPROCESS_SUCCESS_CASES: list[tuple[str, list[str], str]] = [
    ("echo", echo_command("Hello World"), "Hello World\n"),
    ("arguments", echo_command("arg1", "arg2", "arg3"), "arg1 arg2 arg3\n"),
    ("spaces", echo_command("hello world"), "hello world\n"),
    (
        "special-chars",
        echo_command("$HOME", "$(whoami)", "; ls"),
        "$HOME $(whoami) ; ls\n",
    ),
    ("semicolon-literal", echo_command("test; rm -rf /"), "test; rm -rf /\n"),
    (
        "pipe-literal",
        echo_command("test | cat /etc/passwd"),
        "test | cat /etc/passwd\n",
    ),
    ("backticks-literal", echo_command("`whoami`"), "`whoami`\n"),
    (
        "quotes",
        echo_command("'single quotes'", '"double quotes"'),
        "'single quotes' \"double quotes\"\n",
    ),
    (
        "multiple-lines",
        [sys.executable, "-c", "print('line1'); print('line2')"],
        "line1\nline2\n",
    ),
    ("empty-output", [sys.executable, "-c", ""], ""),
    ("full-path", [sys.executable, "-c", "print('test')"], "test\n"),
]


@fixture(params=[run_command, run_command_live], ids=["capture", "live"])
def run(request: FixtureRequest) -> Callable[..., tuple[int, str, str]]:
    """Provide each public subprocess interface for the shared contract checks.

    Arguments:
        request: parametrized subprocess function
    Returns:
        subprocess function under test
    """
    return request.param


@mark.parametrize(
    ("command", "expected_stdout"),
    [(command, expected) for _, command, expected in _SUBPROCESS_SUCCESS_CASES],
    ids=[name for name, _, _ in _SUBPROCESS_SUCCESS_CASES],
)
def test_run_command_success_cases(
    run: Callable[..., tuple[int, str, str]], command: list[str], expected_stdout: str
):
    """Preserve literal arguments, multiple lines, and empty output.

    Arguments:
        run: subprocess interface
        command: command to run
        expected_stdout: complete normalized output
    """
    exitcode, stdout, stderr = run(command)
    assert exitcode == 0
    assert stderr == ""
    assert stdout.replace("\r\n", "\n") == expected_stdout


def test_run_command_with_stderr(run: Callable[..., tuple[int, str, str]]):
    """Capture the child's standard error separately from standard output.

    Arguments:
        run: subprocess interface
    """
    exitcode, stdout, stderr = run(
        [sys.executable, "-c", "import sys; sys.stderr.write('error message')"],
        acceptable_exitcodes=[0],
    )

    assert exitcode == 0
    assert stdout == ""
    assert stderr == "error message"


@mark.parametrize(
    "code, acceptable, error",
    [(0, None, None), (1, None, ValueError), (42, [42], None)],
)
def test_exit_codes(
    run: Callable[..., tuple[int, str, str]],
    code: int,
    acceptable: list[int] | None,
    error: type[Exception] | None,
):
    """Reject failures unless the caller explicitly accepts their exit status.

    Arguments:
        run: subprocess interface
        code: child exit status
        acceptable: accepted statuses, or none for defaults
        error: expected exception, or none for success
    """
    options = {}
    if acceptable is not None:
        options["acceptable_exitcodes"] = acceptable
    expectation: AbstractContextManager[object] = nullcontext()
    if error is not None:
        expectation = raises(error, match="failed with exit code")
    with expectation:
        assert run(
            [sys.executable, "-c", f"import sys; sys.exit({code})"], **options
        ) == (code, "", "")


def test_run_command_with_cwd_path(
    run: Callable[..., tuple[int, str, str]], tmp_path: Path
):
    """Test running a command with a working directory.

    Arguments:
        run: subprocess interface
        tmp_path: temporary directory provided by pytest
    """
    exitcode, stdout, stderr = run(
        [sys.executable, "-c", "from pathlib import Path; print(Path.cwd())"],
        cwd_path=tmp_path,
    )

    assert exitcode == 0
    assert stdout.strip() == str(tmp_path)
    assert stderr == ""


def test_run_command_with_env(run: Callable[..., tuple[int, str, str]]):
    """Test running a command with environment variables.

    Arguments:
        run: subprocess interface
    """
    env = os.environ.copy()
    env["COMMON_TEST_RUN_COMMAND_ENV"] = "expected"

    exitcode, stdout, stderr = run(
        [
            sys.executable,
            "-c",
            "import os; print(os.environ['COMMON_TEST_RUN_COMMAND_ENV'])",
        ],
        env=env,
    )

    assert exitcode == 0
    assert stdout.strip() == "expected"
    assert stderr == ""


def test_run_command_timeout():
    """Test command timeout behavior."""
    start_time = monotonic()
    exitcode, stdout, stderr = run_command(
        [sys.executable, "-c", "import time; time.sleep(10)"],
        timeout=0,
        acceptable_exitcodes=[-9, -15, 1],
    )
    elapsed = monotonic() - start_time

    assert exitcode != 0
    assert elapsed < 1.0


@mark.parametrize(
    "payload, expected", [("Hello 世界".encode(), "Hello 世界"), (b"\xff", "ÿ")]
)
def test_output_decoding(
    run: Callable[..., tuple[int, str, str]], payload: bytes, expected: str
):
    """Decode Unicode and fallback byte encodings without losing characters.

    Arguments:
        run: subprocess interface
        payload: child output bytes
        expected: decoded output
    """
    assert run(
        [sys.executable, "-c", f"import sys; sys.stdout.buffer.write({payload!r})"]
    ) == (0, expected, "")


def test_live_timeout():
    """Raise a timeout from the streaming interface without waiting for the child."""
    start_time = monotonic()
    with raises(TimeoutExpired):
        run_command_live(
            [sys.executable, "-c", "import time; time.sleep(2)"], timeout=0
        )
    assert monotonic() - start_time < 1.0


@mark.parametrize(
    ("live", "parent_exits", "kill_tree"),
    [
        (False, False, True),
        (False, True, True),
        (True, False, True),
        (True, True, True),
        (False, True, False),
        (True, True, False),
    ],
)
def test_timeout_cleans_up_inherited_pipes(
    live: bool,
    parent_exits: bool,
    kill_tree: bool,
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Terminate descendants and bound readers even when tree cleanup misses them.

    Arguments:
        live: whether to use the live logging helper
        parent_exits: whether the direct child exits before the command deadline
        kill_tree: whether process-tree cleanup is allowed to terminate descendants
        tmp_path: directory for the descendant heartbeat
        monkeypatch: fixture for simulating an escaped descendant
    """
    if not kill_tree:

        def kill_direct_child(child: Popen[bytes], job: object):
            """Simulate tree cleanup missing descendants.

            Arguments:
                child: direct child to reap
                job: unused process-tree ownership
            """
            if child.poll() is None:
                child.kill()
            child.wait(timeout=1)

        monkeypatch.setattr(
            subprocess_module, "_terminate_process_tree", kill_direct_child
        )
    with _inherited_pipe_command(tmp_path, parent_exits) as (
        command,
        heartbeat_path,
        ready_path,
    ):
        # Allow both interpreters to reach readiness under parallel load
        timeout = 5.0
        start_time = monotonic()
        if live:
            with raises(TimeoutExpired) as exc:
                run_command_live(command, timeout=timeout)
            stdout = exc.value.output
            stderr = exc.value.stderr
        else:
            exitcode, stdout, stderr = run_command(
                command, timeout=timeout, acceptable_exitcodes=[0, -9, 1]
            )
            if parent_exits:
                assert exitcode == 0, f"stdout={stdout!r}; stderr={stderr!r}"
            else:
                assert exitcode != 0
        elapsed = monotonic() - start_time
        diagnostic = f"elapsed={elapsed:.3f}; stdout={stdout!r}; stderr={stderr!r}"
        assert timeout <= elapsed < timeout + 2.0, diagnostic
        assert isinstance(stdout, str)
        assert isinstance(stderr, str)
        assert ready_path.exists(), diagnostic
        assert "parent ready" in stdout, diagnostic
        assert "descendant output" in stdout, diagnostic
        assert "descendant error" in stderr, diagnostic
        assert heartbeat_path.exists(), diagnostic
        assert not any(
            thread.name.startswith("subprocess-reader-")
            for thread in enumerate_threads()
        )
        heartbeat = heartbeat_path.read_text()
        if kill_tree:
            sleep(0.2)
            assert heartbeat_path.read_text() == heartbeat
        else:
            heartbeat_deadline = monotonic() + 2.0
            while (
                heartbeat_path.read_text() == heartbeat
                and monotonic() < heartbeat_deadline
            ):
                sleep(0.05)
            assert heartbeat_path.read_text() != heartbeat


@mark.parametrize("live", [False, True])
def test_capture_preserves_complete_output(live: bool):
    """Capture both streams beyond pipe-buffer sizes without truncation.

    Arguments:
        live: whether to use live logging with its deadline disabled
    """
    command = [
        sys.executable,
        "-c",
        "import sys; sys.stdout.write('x' * 131072); sys.stderr.write('y' * 131072)",
    ]
    if live:
        exitcode, stdout, stderr = run_command_live(command, timeout=None)
    else:
        exitcode, stdout, stderr = run_command(command, timeout=5)
    assert exitcode == 0
    assert stdout == "x" * 131072
    assert stderr == "y" * 131072


@contextmanager
def _inherited_pipe_command(
    tmp_path: Path, parent_exits: bool
) -> Generator[tuple[list[str], Path, Path]]:
    """Build an inherited-pipe command and always clean up its owned descendant.

    Arguments:
        tmp_path: directory containing only this command's control files
        parent_exits: whether the direct child exits after its descendant is ready
    Yields:
        command, descendant heartbeat path, and direct-child readiness path
    """
    heartbeat_path = tmp_path / "heartbeat.txt"
    pid_path = tmp_path / "descendant.pid"
    ready_path = tmp_path / "parent.ready"
    stop_path = tmp_path / "stop"
    descendant_code = (
        "import sys, time\nfrom pathlib import Path\n"
        "print('descendant output', flush=True)\n"
        "print('descendant error', file=sys.stderr, flush=True)\n"
        f"heartbeat = Path({str(heartbeat_path)!r})\n"
        f"stop = Path({str(stop_path)!r})\n"
        "with heartbeat.open('a') as output:\n"
        " for i in range(1200):\n"
        "  if stop.exists():\n   break\n"
        "  output.write(str(i) + '\\n')\n  output.flush()\n  time.sleep(0.05)\n"
    )
    parent_code = (
        "import subprocess, sys, time\nfrom pathlib import Path\n"
        "descendant = subprocess.Popen("
        f"[sys.executable, '-S', '-c', {descendant_code!r}])\n"
        f"Path({str(pid_path)!r}).write_text(str(descendant.pid))\n"
        f"heartbeat = Path({str(heartbeat_path)!r})\n"
        "while not heartbeat.exists():\n    time.sleep(0.01)\n"
        "print('parent ready', flush=True)\n"
        f"Path({str(ready_path)!r}).write_text('ready')\n"
    )
    if not parent_exits:
        parent_code += "time.sleep(60)"
    try:
        yield [sys.executable, "-S", "-c", parent_code], heartbeat_path, ready_path
    finally:
        stop_path.touch()
        if pid_path.exists():
            _terminate_test_descendant(int(pid_path.read_text()))


def _terminate_test_descendant(pid: int):
    """Terminate the fixture's owned descendant even if an assertion fails.

    Arguments:
        pid: descendant process ID recorded by the command fixture
    Raises:
        OSError: if an existing Windows descendant cannot be opened or terminated
    """
    if os.name != "nt":
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        return

    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.OpenProcess.restype = wintypes.HANDLE
    api.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    api.TerminateProcess.restype = wintypes.BOOL
    api.TerminateProcess.argtypes = (wintypes.HANDLE, wintypes.UINT)
    api.WaitForSingleObject.restype = wintypes.DWORD
    api.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    api.CloseHandle.restype = wintypes.BOOL
    api.CloseHandle.argtypes = (wintypes.HANDLE,)
    handle = api.OpenProcess(0x00100001, False, pid)
    if not handle:
        error = ctypes.get_last_error()
        if error != 87:
            raise ctypes.WinError(error)
        return
    try:
        if api.WaitForSingleObject(handle, 0) == 258:
            if not api.TerminateProcess(handle, 1):
                error = ctypes.get_last_error()
                if api.WaitForSingleObject(handle, 1000) != 0:
                    raise ctypes.WinError(error)
        assert api.WaitForSingleObject(handle, 5000) == 0
    finally:
        api.CloseHandle(handle)
