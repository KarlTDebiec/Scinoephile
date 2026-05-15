#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.DictionaryBuildCuhkCli."""

from __future__ import annotations

import pytest
import requests

from scinoephile.cli.dictionary.build.dictionary_build_cuhk_cli import (
    DictionaryBuildCuhkCli,
)
from scinoephile.common.file import get_temp_directory_path, get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from test.helpers import skip_if_ci


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
