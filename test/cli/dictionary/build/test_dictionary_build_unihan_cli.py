#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.DictionaryBuildUnihanCli."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any

from pytest import MonkeyPatch, raises

from scinoephile.cli.dictionary.build.dictionary_build_unihan_cli import (
    DictionaryBuildUnihanCli,
)
from scinoephile.common.testing import run_cli_with_args
from scinoephile.dictionaries.unihan import UnihanDictionaryService


def test_dictionary_build_unihan_exits_cleanly_on_missing_archive_member(
    monkeypatch: MonkeyPatch,
):
    """Exit with status 1 when the service reports a missing archive member.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    stdout = StringIO()
    stderr = StringIO()

    def _mock_build(self, **kwargs: Any) -> Path:
        """Simulate a service-level extraction failure.

        Arguments:
            self: mocked service instance
            **kwargs: unused build keyword arguments
        Returns:
            never returns
        """
        raise FileNotFoundError("Required file 'Unihan_Readings.txt' not found")

    monkeypatch.setattr(UnihanDictionaryService, "build", _mock_build)

    with raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(DictionaryBuildUnihanCli, "")

    assert excinfo.value.code == 1
    assert stdout.getvalue() == ""
