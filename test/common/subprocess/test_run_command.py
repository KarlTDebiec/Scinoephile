#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.subprocess.run_command."""

from __future__ import annotations

import pytest
from common.subprocess import run_command  # ty:ignore[unresolved-import]


def test_run_command_success_list():
    """Test running a successful command with list format."""
    exitcode, stdout, stderr = run_command(["echo", "Hello World"])

    assert exitcode == 0
    assert "Hello World" in stdout
    assert stderr == ""


def test_run_command_with_arguments():
    """Test running a command with multiple arguments."""
    exitcode, stdout, stderr = run_command(["echo", "arg1", "arg2", "arg3"])

    assert exitcode == 0
    assert "arg1" in stdout
    assert "arg2" in stdout
    assert "arg3" in stdout


def test_run_command_with_spaces():
    """Test running a command with arguments containing spaces."""
    exitcode, stdout, stderr = run_command(["echo", "hello world"])

    assert exitcode == 0
    assert "hello world" in stdout


def test_run_command_with_special_chars():
    """Test running a command with special shell characters."""
    # Test with characters that would be problematic with shell=True
    exitcode, stdout, stderr = run_command(["echo", "$HOME", "$(whoami)", "; ls"])

    assert exitcode == 0
    # These should be printed literally, not expanded
    assert "$HOME" in stdout
    assert "$(whoami)" in stdout
    assert "; ls" in stdout


def test_run_command_injection_prevention():
    """Test that command injection is prevented.

    This test verifies that shell metacharacters like semicolons, pipes,
    and command substitution are treated as literal strings rather than
    being executed as shell commands.
    """
    # This would be dangerous with shell=True, but is safe now
    exitcode, stdout, stderr = run_command(["echo", "test; rm -rf /"])

    assert exitcode == 0
    # The semicolon and rm command should be in the output as literal text
    assert "test; rm -rf /" in stdout

    # Test pipe character
    exitcode, stdout, stderr = run_command(["echo", "test | cat /etc/passwd"])
    assert exitcode == 0
    assert "test | cat /etc/passwd" in stdout

    # Test backticks
    exitcode, stdout, stderr = run_command(["echo", "`whoami`"])
    assert exitcode == 0
    assert "`whoami`" in stdout


def test_run_command_with_quotes():
    """Test running a command with quoted arguments."""
    exitcode, stdout, stderr = run_command(
        ["echo", "'single quotes'", '"double quotes"']
    )

    assert exitcode == 0
    assert "'single quotes'" in stdout
    assert '"double quotes"' in stdout


def test_run_command_with_stderr():
    """Test running a command that writes to stderr."""
    # Use Python to write to stderr.
    exitcode, stdout, stderr = run_command(
        ["python3", "-c", "import sys; sys.stderr.write('error message')"],
        acceptable_exitcodes=[0],
    )

    assert exitcode == 0
    assert "error message" in stderr


def test_run_command_failure_default():
    """Test running a command that fails with default acceptable exitcodes."""
    with pytest.raises(ValueError, match="failed with exit code"):
        run_command(["sh", "-c", "exit 1"])


def test_run_command_failure_custom_acceptable():
    """Test running a command with custom acceptable exitcodes."""
    exitcode, stdout, stderr = run_command(
        ["sh", "-c", "exit 42"], acceptable_exitcodes=[42]
    )

    assert exitcode == 42


def test_run_command_timeout():
    """Test command timeout behavior."""
    # Command that sleeps longer than timeout. The command will be killed and
    # return a negative exit code.
    exitcode, stdout, stderr = run_command(
        ["sleep", "10"], timeout=1, acceptable_exitcodes=[-9, -15]
    )

    # Command should be killed, exitcode is negative (signal).
    assert exitcode in [-9, -15]  # SIGKILL or SIGTERM


def test_run_command_unicode_output():
    """Test handling of unicode output."""
    exitcode, stdout, stderr = run_command(["echo", "Hello 世界"])

    assert exitcode == 0
    assert "Hello" in stdout


def test_run_command_multiple_lines():
    """Test command with multiple lines of output."""
    exitcode, stdout, stderr = run_command(["sh", "-c", "echo 'line1'; echo 'line2'"])

    assert exitcode == 0
    assert "line1" in stdout
    assert "line2" in stdout


def test_run_command_empty_output():
    """Test command with no output."""
    exitcode, stdout, stderr = run_command(["true"])

    assert exitcode == 0
    assert stdout == ""
    assert stderr == ""


def test_run_command_with_path():
    """Test command with executable specified by full path."""
    exitcode, stdout, stderr = run_command(["/bin/echo", "test"])

    assert exitcode == 0
    assert "test" in stdout
