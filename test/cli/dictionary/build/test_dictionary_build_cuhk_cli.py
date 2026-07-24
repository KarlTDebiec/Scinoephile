#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.DictionaryBuildCuhkCli."""

from __future__ import annotations

from pathlib import Path

import requests
from pytest import MonkeyPatch, skip

from scinoephile.cli.dictionary.build.dictionary_build_cuhk_cli import (
    DictionaryBuildCuhkCli,
)
from scinoephile.common.file import get_temp_directory_path, get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from test.helpers import skip_if_ci


def test_dictionary_build_cuhk_cli_passes_cache_dir_to_service(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
):
    """Test CUHK CLI forwards parsed cache dirs without parser-time creation.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    init_calls: list[dict[str, object]] = []
    build_calls: list[dict[str, object]] = []
    cache_dir_path = tmp_path / "cache"
    database_path = tmp_path / "cuhk.db"

    class FakeCuhkDictionaryService:
        """Fake CUHK dictionary service."""

        def __init__(
            self,
            database_path: Path | None = None,
            *,
            scraper_kwargs: dict[str, object] | None = None,
        ):
            """Initialize."""
            init_calls.append(
                {
                    "database_path": database_path,
                    "scraper_kwargs": scraper_kwargs,
                }
            )
            self.cache_dir_path = cache_dir_path.resolve() / "dictionaries" / "cuhk"
            self.database_path = database_path

        def build(
            self,
            *,
            overwrite: bool = False,
            max_words: int | None = None,
        ) -> Path:
            """Build the dictionary."""
            build_calls.append({"overwrite": overwrite, "max_words": max_words})
            return database_path

    monkeypatch.setattr(
        "scinoephile.cli.dictionary.build.dictionary_build_cuhk_cli."
        "CuhkDictionaryService",
        FakeCuhkDictionaryService,
    )

    run_cli_with_args(
        DictionaryBuildCuhkCli,
        f"--cache-dir {cache_dir_path} --database-path {database_path} "
        "--max-words 3 --overwrite --cache-overwrite",
    )

    assert init_calls == [
        {
            "database_path": database_path.resolve(),
            "scraper_kwargs": {
                "cache_dir_path": (cache_dir_path.resolve() / "dictionaries" / "cuhk"),
                "min_delay_seconds": 1.0,
                "max_delay_seconds": 5.0,
                "max_retries": 5,
                "overwrite_cache": True,
                "request_timeout_seconds": 30.0,
            },
        }
    ]
    assert build_calls == [{"overwrite": True, "max_words": 3}]
    assert not cache_dir_path.exists()


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
                skip(f"CUHK build test requires network access: {exc}")

            assert database_path.exists()
