#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.subprocess.run_command."""

from __future__ import annotations

import pytest
from common.subprocess import run_command  # ty:ignore[unresolved-import]


def test_run_command_success():
    """Test running a successful command."""
    exitcode, stdout, stderr = run_command("echo 'Hello World'")

    assert exitcode == 0
    assert "Hello World" in stdout
    assert stderr == ""


def test_run_command_with_stderr():
    """Test running a command that writes to stderr."""
    # Use Python to write to stderr.
    exitcode, stdout, stderr = run_command(
        "python3 -c \"import sys; sys.stderr.write('error message')\"",
        acceptable_exitcodes=[0],
    )

    assert exitcode == 0
    assert "error message" in stderr


def test_run_command_failure_default():
    """Test running a command that fails with default acceptable exitcodes."""
    with pytest.raises(ValueError, match="failed with exit code"):
        run_command("exit 1")


def test_run_command_failure_custom_acceptable():
    """Test running a command with custom acceptable exitcodes."""
    exitcode, stdout, stderr = run_command("exit 42", acceptable_exitcodes=[42])

    assert exitcode == 42


def test_run_command_timeout():
    """Test command timeout behavior."""
    # Command that sleeps longer than timeout. The command will be killed and
    # return a negative exit code.
    exitcode, stdout, stderr = run_command(
        "sleep 10", timeout=1, acceptable_exitcodes=[-9, -15]
    )

    # Command should be killed, exitcode is negative (signal).
    assert exitcode in [-9, -15]  # SIGKILL or SIGTERM


def test_run_command_unicode_output():
    """Test handling of unicode output."""
    exitcode, stdout, stderr = run_command("echo 'Hello 世界'")

    assert exitcode == 0
    assert "Hello" in stdout


def test_run_command_multiple_lines():
    """Test command with multiple lines of output."""
    exitcode, stdout, stderr = run_command("echo 'line1'; echo 'line2'")

    assert exitcode == 0
    assert "line1" in stdout
    assert "line2" in stdout


def test_run_command_empty_output():
    """Test command with no output."""
    exitcode, stdout, stderr = run_command("true")

    assert exitcode == 0
    assert stdout == ""
    assert stderr == ""
