#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.DictionaryBuildUnihanCli."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

from scinoephile.cli.dictionary.build.dictionary_build_cli import DictionaryBuildCli
from scinoephile.cli.dictionary.build.dictionary_build_unihan_cli import (
    DictionaryBuildUnihanCli,
)
from scinoephile.cli.dictionary.dictionary_cli import DictionaryCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args
from scinoephile.dictionaries.unihan import UnihanDictionaryService
from test.helpers import assert_cli_help, build_subcommands, get_usage_prefix


@pytest.mark.parametrize(
    "cli",
    [
        (DictionaryBuildUnihanCli,),
        (DictionaryBuildCli, DictionaryBuildUnihanCli),
        (DictionaryCli, DictionaryBuildCli, DictionaryBuildUnihanCli),
        (ScinoephileCli, DictionaryCli, DictionaryBuildCli, DictionaryBuildUnihanCli),
    ],
)
def test_dictionary_build_unihan_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test Unihan build subcommand help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (DictionaryBuildUnihanCli,),
        (DictionaryBuildCli, DictionaryBuildUnihanCli),
        (DictionaryCli, DictionaryBuildCli, DictionaryBuildUnihanCli),
        (ScinoephileCli, DictionaryCli, DictionaryBuildCli, DictionaryBuildUnihanCli),
    ],
)
def test_dictionary_build_unihan_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test Unihan build subcommand usage output on parse error.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    stdout = StringIO()
    stderr = StringIO()
    subcommands = build_subcommands(cli)

    with pytest.raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(
                    cli[0], f"{subcommands} --source-readings-path".strip()
                )

    assert excinfo.value.code == 2
    assert stdout.getvalue() == ""
    assert stderr.getvalue().startswith(get_usage_prefix(cli))


def test_dictionary_build_unihan_exits_cleanly_on_missing_archive_member(
    monkeypatch: pytest.MonkeyPatch,
):
    """Exit with status 1 when the service reports a missing archive member.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    stdout = StringIO()
    stderr = StringIO()

    def _mock_build(self, **kwargs) -> Path:
        """Simulate a service-level extraction failure.

        Arguments:
            self: mocked service instance
            **kwargs: unused build keyword arguments
        Returns:
            never returns
        """
        raise FileNotFoundError("Required file 'Unihan_Readings.txt' not found")

    monkeypatch.setattr(UnihanDictionaryService, "build", _mock_build)

    with pytest.raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(DictionaryBuildUnihanCli, "")

    assert excinfo.value.code == 1
    assert stdout.getvalue() == ""
