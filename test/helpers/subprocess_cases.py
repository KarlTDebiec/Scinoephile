#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared subprocess command test cases."""

from __future__ import annotations

import sys

from scinoephile.common.testing import echo_command

__all__ = ["SUBPROCESS_SUCCESS_CASES"]

SUBPROCESS_SUCCESS_CASES: list[tuple[str, list[str], str]] = [
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
