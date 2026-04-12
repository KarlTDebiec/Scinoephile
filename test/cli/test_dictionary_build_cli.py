#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.DictionaryBuildCli."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import pytest

from scinoephile.cli import DictionaryBuildCli, DictionaryCli, ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_directory_path, get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from test.helpers import (
    assert_cli_help,
    build_subcommands,
    get_usage_prefix,
    skip_if_ci,
    skip_if_no_network,
)


@pytest.mark.parametrize(
    "cli",
    [
        (DictionaryBuildCli,),
        (DictionaryCli, DictionaryBuildCli),
        (ScinoephileCli, DictionaryCli, DictionaryBuildCli),
    ],
)
def test_dictionary_build_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test dictionary build CLI help output."""
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (DictionaryBuildCli,),
        (DictionaryCli, DictionaryBuildCli),
        (ScinoephileCli, DictionaryCli, DictionaryBuildCli),
    ],
)
def test_dictionary_build_usage(
    cli: tuple[type[CommandLineInterface], ...],
):
    """Test dictionary build CLI usage output on parse error."""
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
@skip_if_no_network()
def test_dictionary_build_cli():
    """Test CUHK dictionary build CLI performs a limited real scrape."""
    with get_temp_directory_path() as cache_dir_path:
        with get_temp_file_path(".db") as database_path:
            run_cli_with_args(
                ScinoephileCli,
                "dictionary build cuhk "
                f"--cache-dir {cache_dir_path} "
                f"--database-path {database_path} "
                "--max-words 10 "
                "--overwrite "
                "--min-delay-seconds 0 "
                "--max-delay-seconds 0 "
                "--max-retries 2 "
                "--request-timeout-seconds 10",
            )

            assert database_path.exists()
