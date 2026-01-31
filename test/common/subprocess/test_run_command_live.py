#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.subprocess.run_command_live."""

from __future__ import annotations

import pytest
from common.subprocess import run_command_live  # ty:ignore[unresolved-import]


def test_run_command_live_success():
    """Test running a successful command with live output."""
    exitcode, stdout, stderr = run_command_live("echo 'Hello World'")

    assert exitcode == 0
    assert "Hello World" in stdout
    assert stderr == ""


def test_run_command_live_with_stderr():
    """Test running a command with live stderr output."""
    exitcode, stdout, stderr = run_command_live(
        "python3 -c \"import sys; sys.stderr.write('error message')\"",
        acceptable_exitcodes=[0],
    )

    assert exitcode == 0
    assert "error message" in stderr


def test_run_command_live_failure_default():
    """Test running a command that fails with default acceptable exitcodes."""
    with pytest.raises(ValueError, match="failed with exit code"):
        run_command_live("exit 1")


def test_run_command_live_failure_custom_acceptable():
    """Test running a command with custom acceptable exitcodes."""
    exitcode, stdout, stderr = run_command_live("exit 42", acceptable_exitcodes=[42])

    assert exitcode == 42


def test_run_command_live_multiple_lines():
    """Test command with multiple lines of output."""
    exitcode, stdout, stderr = run_command_live("echo 'line1'; echo 'line2'")

    assert exitcode == 0
    assert "line1" in stdout
    assert "line2" in stdout


def test_run_command_live_empty_output():
    """Test command with no output using live streaming."""
    exitcode, stdout, stderr = run_command_live("true")

    assert exitcode == 0
    assert stdout == ""
    assert stderr == ""
