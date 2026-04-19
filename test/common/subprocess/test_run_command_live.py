#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.subprocess.run_command_live."""

from __future__ import annotations

import sys
from subprocess import TimeoutExpired
from time import monotonic

import pytest
from common.subprocess import run_command_live  # ty:ignore[unresolved-import]


def test_run_command_live_success_list():
    """Test running a successful command with live output using list format."""
    exitcode, stdout, stderr = run_command_live(["echo", "Hello World"])

    assert exitcode == 0
    assert "Hello World" in stdout
    assert stderr == ""


def test_run_command_live_with_arguments():
    """Test running a command with multiple arguments."""
    exitcode, stdout, stderr = run_command_live(["echo", "arg1", "arg2", "arg3"])

    assert exitcode == 0
    assert "arg1" in stdout
    assert "arg2" in stdout
    assert "arg3" in stdout


def test_run_command_live_with_spaces():
    """Test running a command with arguments containing spaces."""
    exitcode, stdout, stderr = run_command_live(["echo", "hello world"])

    assert exitcode == 0
    assert "hello world" in stdout


def test_run_command_live_with_special_chars():
    """Test running a command with special shell characters."""
    # Test with characters that would be problematic with shell=True
    exitcode, stdout, stderr = run_command_live(["echo", "$HOME", "$(whoami)", "; ls"])

    assert exitcode == 0
    # These should be printed literally, not expanded
    assert "$HOME" in stdout
    assert "$(whoami)" in stdout
    assert "; ls" in stdout


def test_run_command_live_injection_prevention():
    """Test that command injection is prevented.

    This test verifies that shell metacharacters like semicolons, pipes,
    and command substitution are treated as literal strings rather than
    being executed as shell commands.
    """
    # This would be dangerous with shell=True, but is safe now
    exitcode, stdout, stderr = run_command_live(["echo", "test; rm -rf /"])

    assert exitcode == 0
    # The semicolon and rm command should be in the output as literal text
    assert "test; rm -rf /" in stdout

    # Test pipe character
    exitcode, stdout, stderr = run_command_live(["echo", "test | cat /etc/passwd"])
    assert exitcode == 0
    assert "test | cat /etc/passwd" in stdout

    # Test backticks
    exitcode, stdout, stderr = run_command_live(["echo", "`whoami`"])
    assert exitcode == 0
    assert "`whoami`" in stdout


def test_run_command_live_with_quotes():
    """Test running a command with quoted arguments."""
    exitcode, stdout, stderr = run_command_live(
        ["echo", "'single quotes'", '"double quotes"']
    )

    assert exitcode == 0
    assert "'single quotes'" in stdout
    assert '"double quotes"' in stdout


def test_run_command_live_with_stderr():
    """Test running a command with live stderr output."""
    exitcode, stdout, stderr = run_command_live(
        ["python3", "-c", "import sys; sys.stderr.write('error message')"],
        acceptable_exitcodes=[0],
    )

    assert exitcode == 0
    assert "error message" in stderr


def test_run_command_live_failure_default():
    """Test running a command that fails with default acceptable exitcodes."""
    with pytest.raises(ValueError, match="failed with exit code"):
        run_command_live(["sh", "-c", "exit 1"])


def test_run_command_live_failure_custom_acceptable():
    """Test running a command with custom acceptable exitcodes."""
    exitcode, stdout, stderr = run_command_live(
        ["sh", "-c", "exit 42"], acceptable_exitcodes=[42]
    )

    assert exitcode == 42


def test_run_command_live_multiple_lines():
    """Test command with multiple lines of output."""
    exitcode, stdout, stderr = run_command_live(
        ["sh", "-c", "echo 'line1'; echo 'line2'"]
    )

    assert exitcode == 0
    assert "line1" in stdout
    assert "line2" in stdout


def test_run_command_live_empty_output():
    """Test command with no output using live streaming."""
    exitcode, stdout, stderr = run_command_live(["true"])

    assert exitcode == 0
    assert stdout == ""
    assert stderr == ""


def test_run_command_live_with_path():
    """Test command with executable specified by full path."""
    exitcode, stdout, stderr = run_command_live(["/bin/echo", "test"])

    assert exitcode == 0
    assert "test" in stdout


def test_run_command_live_timeout():
    """Test command timeout behavior."""
    start_time = monotonic()
    with pytest.raises(TimeoutExpired):
        run_command_live(
            [sys.executable, "-c", "import time; time.sleep(2)"], timeout=1
        )
    elapsed = monotonic() - start_time

    assert elapsed < 2


def test_run_command_live_non_utf8_output():
    """Test handling of non-UTF-8 output."""
    exitcode, stdout, stderr = run_command_live(
        [sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'\\xff')"]
    )

    assert exitcode == 0
    assert stdout == "ÿ"
    assert stderr == ""
