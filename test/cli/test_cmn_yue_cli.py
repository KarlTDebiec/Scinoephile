#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of 中文/粤文 CLI commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from scinoephile.cli import (
    CmnYueCli,
    CmnYueDictionaryBuildCli,
    CmnYueDictionaryCli,
    CmnYueDictionarySearchCli,
    ScinoephileCli,
)
from scinoephile.common.testing import (
    assert_cli_help,
    assert_cli_usage,
    run_cli_with_args,
)
from scinoephile.multilang.cmn_yue.dictionaries import (
    DictionaryDefinition,
    DictionaryEntry,
)


@pytest.mark.parametrize(
    "cli",
    [
        (CmnYueCli,),
        (ScinoephileCli, CmnYueCli),
        (ScinoephileCli, CmnYueCli, CmnYueDictionaryCli),
        (ScinoephileCli, CmnYueCli, CmnYueDictionaryCli, CmnYueDictionaryBuildCli),
        (ScinoephileCli, CmnYueCli, CmnYueDictionaryCli, CmnYueDictionarySearchCli),
    ],
)
def test_cmn_yue_help(cli):
    """Test 中文/粤文 CLI help output."""
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (CmnYueCli,),
        (ScinoephileCli, CmnYueCli),
        (ScinoephileCli, CmnYueCli, CmnYueDictionaryCli),
        (ScinoephileCli, CmnYueCli, CmnYueDictionaryCli, CmnYueDictionarySearchCli),
    ],
)
def test_cmn_yue_usage(cli):
    """Test 中文/粤文 CLI usage output."""
    assert_cli_usage(cli)


def test_cmn_yue_dictionary_build_cli(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    """Test CUHK dictionary build CLI forwards configuration."""
    database_path = tmp_path / "cache" / "cuhk.db"

    with patch(
        "scinoephile.cli.cmn_yue_dictionary_build_cli.CuhkDictionaryBuilder.build",
        return_value=database_path,
    ) as mock_build:
        run_cli_with_args(
            ScinoephileCli,
            "cmn_yue dictionary build "
            f"--cache-dir {tmp_path / 'cache'} "
            "--max-words 7 "
            "--force-rebuild "
            "--min-delay-seconds 0 "
            "--max-delay-seconds 0 "
            "--max-retries 2 "
            "--request-timeout-seconds 10",
        )

    mock_build.assert_called_once_with(force_rebuild=True, max_words=7)
    captured = capsys.readouterr()
    assert "Building at most 7 discovered CUHK words" in captured.err
    assert f"CUHK dictionary build complete: {database_path}" in captured.err


def test_cmn_yue_dictionary_search_cli(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    """Test CUHK dictionary search CLI formats entries for display."""
    entries = [
        DictionaryEntry(
            traditional="巴士",
            simplified="巴士",
            pinyin="ba1 shi4",
            jyutping="baa1 si6",
            definitions=[
                DictionaryDefinition(text="bus", label="名詞"),
                DictionaryDefinition(text="motor bus"),
            ],
        )
    ]

    with patch(
        "scinoephile.cli.cmn_yue_dictionary_search_cli.CuhkDictionaryService.lookup",
        return_value=entries,
    ) as mock_lookup:
        run_cli_with_args(
            ScinoephileCli,
            "cmn_yue dictionary search "
            f"--cache-dir {tmp_path / 'cache'} "
            "--direction cantonese_to_mandarin "
            "--limit 3 "
            "baa1",
        )

    mock_lookup.assert_called_once_with(
        query="baa1",
        direction="cantonese_to_mandarin",
        limit=3,
    )
    captured = capsys.readouterr()
    assert "Found 1 CUHK match(es) for 'baa1'" in captured.err
    assert "1. 巴士 | 巴士 | Jyutping: baa1 si6 | Pinyin: ba1 shi4" in captured.err
    assert "   - [名詞] bus" in captured.err
    assert "   - motor bus" in captured.err
