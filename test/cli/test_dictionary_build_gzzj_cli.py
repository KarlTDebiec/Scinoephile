#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.DictionaryBuildGzzjCli."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from os import environ
from unittest.mock import patch

import pytest

from scinoephile.cli import (
    DictionaryBuildCli,
    DictionaryBuildGzzjCli,
    DictionaryCli,
    ScinoephileCli,
)
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_directory_path
from scinoephile.common.testing import run_cli_with_args
from test.helpers import assert_cli_help


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
    """Test GZZJ build subcommand help output."""
    assert_cli_help(cli)


def test_dictionary_build_gzzj_usage_missing_source():
    """Test GZZJ build requires a source JSON file."""
    stdout = StringIO()
    stderr = StringIO()

    with get_temp_directory_path() as cache_dir_path:
        with pytest.raises(SystemExit) as excinfo:
            with redirect_stdout(stdout):
                with redirect_stderr(stderr):
                    with patch.dict(
                        environ, {"SCINOEPHILE_CACHE_DIR": str(cache_dir_path)}
                    ):
                        run_cli_with_args(
                            DictionaryBuildCli,
                            "gzzj --overwrite",
                        )

    assert excinfo.value.code == 1
    assert stdout.getvalue() == ""
    assert "GZZJ source JSON not found" in stderr.getvalue()
