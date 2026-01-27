#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.argument_parsing."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from common.argument_parsing import (  # ty:ignore[unresolved-import]
    input_file_arg,
    int_arg,
)


def test_validators_in_argparse(tmp_path: Path):
    """Test using validators in ArgumentParser."""
    parser = ArgumentParser()

    test_file = tmp_path / "input.txt"
    test_file.write_text("test")

    parser.add_argument("--input", type=input_file_arg())
    parser.add_argument("--number", type=int_arg(min_value=0))

    args = parser.parse_args(["--input", str(test_file), "--number", "42"])

    assert isinstance(args.input, Path)
    assert args.input.exists()
    assert args.number == 42
