#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared subprocess command test cases."""

from __future__ import annotations

import sys

from scinoephile.common.testing import echo_command

__all__ = ["SUBPROCESS_SUCCESS_CASES"]

SUBPROCESS_SUCCESS_CASES: list[tuple[str, list[str], tuple[str, ...]]] = [
    ("echo", echo_command("Hello World"), ("Hello World",)),
    ("arguments", echo_command("arg1", "arg2", "arg3"), ("arg1", "arg2", "arg3")),
    ("spaces", echo_command("hello world"), ("hello world",)),
    (
        "special-chars",
        echo_command("$HOME", "$(whoami)", "; ls"),
        ("$HOME", "$(whoami)", "; ls"),
    ),
    ("semicolon-literal", echo_command("test; rm -rf /"), ("test; rm -rf /",)),
    (
        "pipe-literal",
        echo_command("test | cat /etc/passwd"),
        ("test | cat /etc/passwd",),
    ),
    ("backticks-literal", echo_command("`whoami`"), ("`whoami`",)),
    (
        "quotes",
        echo_command("'single quotes'", '"double quotes"'),
        ("'single quotes'", '"double quotes"'),
    ),
    (
        "multiple-lines",
        [sys.executable, "-c", "print('line1'); print('line2')"],
        ("line1", "line2"),
    ),
    ("empty-output", [sys.executable, "-c", ""], ()),
    ("full-path", [sys.executable, "-c", "print('test')"], ("test",)),
]
