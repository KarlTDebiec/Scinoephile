#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.subprocess.run_command."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from subprocess import Popen, TimeoutExpired
from threading import enumerate as enumerate_threads
from time import monotonic, sleep

from pytest import MonkeyPatch, raises

from scinoephile.common import subprocess as subprocess_module
from scinoephile.common.subprocess import run_command, run_command_live
from test.helpers import parametrize
from test.helpers.subprocess_cases import SUBPROCESS_SUCCESS_CASES


@parametrize(
    ("command", "expected_stdout_fragments"),
    [(command, fragments) for _, command, fragments in SUBPROCESS_SUCCESS_CASES],
    ids=[name for name, _, _ in SUBPROCESS_SUCCESS_CASES],
)
def test_run_command_success_cases(
    command: list[str], expected_stdout_fragments: tuple[str, ...]
):
    """Test running successful commands.

    Arguments:
        command: command to run
        expected_stdout_fragments: expected stdout fragments
    """
    exitcode, stdout, stderr = run_command(command)

    assert exitcode == 0
    assert stderr == ""
    if not expected_stdout_fragments:
        assert stdout == ""
    for fragment in expected_stdout_fragments:
        assert fragment in stdout


def test_run_command_with_stderr():
    """Test running a command that writes to stderr."""
    # Use Python to write to stderr.
    exitcode, stdout, stderr = run_command(
        [sys.executable, "-c", "import sys; sys.stderr.write('error message')"],
        acceptable_exitcodes=[0],
    )

    assert exitcode == 0
    assert "error message" in stderr


def test_run_command_failure_default():
    """Test running a command that fails with default acceptable exitcodes."""
    with raises(ValueError, match="failed with exit code"):
        run_command([sys.executable, "-c", "import sys; sys.exit(1)"])


def test_run_command_failure_custom_acceptable():
    """Test running a command with custom acceptable exitcodes."""
    exitcode, stdout, stderr = run_command(
        [sys.executable, "-c", "import sys; sys.exit(42)"], acceptable_exitcodes=[42]
    )

    assert exitcode == 42


def test_run_command_with_cwd_path(tmp_path: Path):
    """Test running a command with a working directory.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    exitcode, stdout, stderr = run_command(
        [sys.executable, "-c", "from pathlib import Path; print(Path.cwd())"],
        cwd_path=tmp_path,
    )

    assert exitcode == 0
    assert stdout.strip() == str(tmp_path)
    assert stderr == ""


def test_run_command_with_env():
    """Test running a command with environment variables."""
    env = os.environ.copy()
    env["SCINOEPHILE_TEST_RUN_COMMAND_ENV"] = "expected"

    exitcode, stdout, stderr = run_command(
        [
            sys.executable,
            "-c",
            "import os; print(os.environ['SCINOEPHILE_TEST_RUN_COMMAND_ENV'])",
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


def test_run_command_unicode_output():
    """Test handling of Unicode output."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    exitcode, stdout, stderr = run_command(
        [sys.executable, "-c", "print('Hello 世界')"], env=env
    )

    assert exitcode == 0
    assert "Hello" in stdout


@parametrize(
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
    heartbeat_path = tmp_path / "heartbeat.txt"
    descendant_code = (
        "import sys, time\nfrom pathlib import Path\n"
        "print('descendant output', flush=True)\n"
        "print('descendant error', file=sys.stderr, flush=True)\n"
        f"heartbeat = Path({str(heartbeat_path)!r})\n"
        "heartbeat.write_text('0')\n"
        "for i in range(1, 61):\n"
        " heartbeat.write_text(str(i))\n time.sleep(0.05)\n"
    )
    parent_code = (
        "import subprocess, sys, time\nfrom pathlib import Path\n"
        f"subprocess.Popen([sys.executable, '-S', '-c', {descendant_code!r}])\n"
        f"heartbeat = Path({str(heartbeat_path)!r})\n"
        "while not heartbeat.exists():\n    time.sleep(0.01)\n"
        "print('parent ready', flush=True)\n"
    )
    if not parent_exits:
        parent_code += "time.sleep(10)"
    # Keep interpreter site initialization outside this short cleanup regression
    command = [sys.executable, "-S", "-c", parent_code]
    start_time = monotonic()
    if live:
        with raises(TimeoutExpired) as exc:
            run_command_live(command, timeout=1.0)
        stdout = exc.value.output
        stderr = exc.value.stderr
    else:
        exitcode, stdout, stderr = run_command(
            command, timeout=1.0, acceptable_exitcodes=[0, -9, 1]
        )
        if parent_exits:
            assert exitcode == 0
        else:
            assert exitcode != 0
    assert monotonic() - start_time < 2.0
    assert isinstance(stdout, str)
    assert isinstance(stderr, str)
    assert "parent ready" in stdout
    assert "descendant output" in stdout
    assert "descendant error" in stderr
    assert heartbeat_path.exists()
    assert not any(
        thread.name.startswith("scinoephile-reader-") for thread in enumerate_threads()
    )
    sleep(0.1)
    heartbeat = heartbeat_path.read_text()
    sleep(0.2)
    if kill_tree:
        assert heartbeat_path.read_text() == heartbeat
    else:
        assert heartbeat_path.read_text() != heartbeat


@parametrize("live", [False, True])
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
