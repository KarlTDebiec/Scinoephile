#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of core CLI argument type helpers."""

from __future__ import annotations

from argparse import ArgumentTypeError

from pytest import raises

from scinoephile.core.cli.argument_types import language_arg


def test_language_arg_normalizes_language_tag():
    """Test language_arg normalizes loose language tags."""
    assert language_arg("ZHO-hant") == "zho-Hant"


def test_language_arg_rejects_empty_tag():
    """Test language_arg rejects empty language tags."""
    with raises(ArgumentTypeError, match="language tag may not be empty"):
        language_arg("")
