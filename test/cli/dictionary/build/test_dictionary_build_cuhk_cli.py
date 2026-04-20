#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.DictionaryBuildCuhkCli."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import pytest
import requests

from scinoephile.cli.dictionary.build.dictionary_build_cli import DictionaryBuildCli
from scinoephile.cli.dictionary.build.dictionary_build_cuhk_cli import (
    DictionaryBuildCuhkCli,
)
from scinoephile.cli.dictionary.dictionary_cli import DictionaryCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_directory_path, get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from test.helpers import (
    assert_cli_help,
    build_subcommands,
    get_usage_prefix,
    skip_if_ci,
)


@pytest.mark.parametrize(
    "cli",
    [
        (DictionaryBuildCuhkCli,),
        (DictionaryBuildCli, DictionaryBuildCuhkCli),
        (DictionaryCli, DictionaryBuildCli, DictionaryBuildCuhkCli),
        (ScinoephileCli, DictionaryCli, DictionaryBuildCli, DictionaryBuildCuhkCli),
    ],
)
def test_dictionary_build_cuhk_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test CUHK build subcommand help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (DictionaryBuildCuhkCli,),
        (DictionaryBuildCli, DictionaryBuildCuhkCli),
        (DictionaryCli, DictionaryBuildCli, DictionaryBuildCuhkCli),
        (ScinoephileCli, DictionaryCli, DictionaryBuildCli, DictionaryBuildCuhkCli),
    ],
)
def test_dictionary_build_cuhk_usage(
    cli: tuple[type[CommandLineInterface], ...],
):
    """Test CUHK build subcommand usage output on parse error.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    stdout = StringIO()
    stderr = StringIO()
    subcommands = build_subcommands(cli)

    with pytest.raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(cli[0], f"{subcommands} --max-words".strip())

    assert excinfo.value.code == 2
    assert stdout.getvalue() == ""
    assert stderr.getvalue().startswith(get_usage_prefix(cli))


@skip_if_ci()
def test_dictionary_build_cuhk_cli():
    """Test CUHK dictionary build CLI performs a limited real scrape."""
    with get_temp_directory_path() as cache_dir_path:
        with get_temp_file_path(".db") as database_path:
            try:
                run_cli_with_args(
                    DictionaryBuildCuhkCli,
                    f"--cache-dir {cache_dir_path} "
                    f"--database-path {database_path} "
                    "--max-words 10 "
                    "--overwrite "
                    "--min-delay-seconds 0 "
                    "--max-delay-seconds 0 "
                    "--max-retries 2 "
                    "--request-timeout-seconds 10",
                )
            except requests.RequestException as exc:
                pytest.skip(f"CUHK build test requires network access: {exc}")

            assert database_path.exists()
