#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.DictionaryBuildGzzjCli."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import pytest

from scinoephile.cli.dictionary.build.dictionary_build_cli import DictionaryBuildCli
from scinoephile.cli.dictionary.build.dictionary_build_gzzj_cli import (
    DictionaryBuildGzzjCli,
)
from scinoephile.cli.dictionary.dictionary_cli import DictionaryCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args
from test.helpers import assert_cli_help, build_subcommands, get_usage_prefix


@pytest.mark.parametrize(
    "cli",
    [
        (DictionaryBuildGzzjCli,),
        (DictionaryBuildCli, DictionaryBuildGzzjCli),
        (DictionaryCli, DictionaryBuildCli, DictionaryBuildGzzjCli),
        (ScinoephileCli, DictionaryCli, DictionaryBuildCli, DictionaryBuildGzzjCli),
    ],
)
def test_dictionary_build_gzzj_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test GZZJ build subcommand help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (DictionaryBuildGzzjCli,),
        (DictionaryBuildCli, DictionaryBuildGzzjCli),
        (DictionaryCli, DictionaryBuildCli, DictionaryBuildGzzjCli),
        (ScinoephileCli, DictionaryCli, DictionaryBuildCli, DictionaryBuildGzzjCli),
    ],
)
def test_dictionary_build_gzzj_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test GZZJ build subcommand usage output on parse error.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    stdout = StringIO()
    stderr = StringIO()
    subcommands = build_subcommands(cli)

    with pytest.raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(cli[0], f"{subcommands} --source-json-path".strip())

    assert excinfo.value.code == 2
    assert stdout.getvalue() == ""
    assert stderr.getvalue().startswith(get_usage_prefix(cli))
