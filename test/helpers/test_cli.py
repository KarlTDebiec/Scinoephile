#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for project CLI assertion helpers."""

from __future__ import annotations

from argparse import ArgumentParser

from pytest import MonkeyPatch, raises

from scinoephile.common.cli import CommandLineInterface
from test import helpers


class RequiredArgCli(CommandLineInterface):
    """Test CLI that requires an argument."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)
        parser.add_argument("--name", required=True)

    @classmethod
    def _main(cls, *, name: str):
        """Execute test CLI.

        Arguments:
            name: name
        """


def test_assert_cli_usage_failure_reports_streams(monkeypatch: MonkeyPatch):
    """Test CLI usage assertion failures include expected and actual streams.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    monkeypatch.setattr(
        helpers, "get_usage_prefix", lambda cli: "usage: intentionally-wrong.py"
    )

    with raises(AssertionError) as excinfo:
        helpers.assert_cli_usage((RequiredArgCli,))

    message = str(excinfo.value)
    assert "Expected stderr to start with:" in message
    assert "usage: intentionally-wrong.py" in message
    assert "Actual stderr:" in message
    assert "Actual stdout:" in message
