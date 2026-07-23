#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.DictionaryBuildWiktionaryCli."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any

import requests
from pytest import MonkeyPatch, raises

from scinoephile.cli.dictionary.build.dictionary_build_wiktionary_cli import (
    DictionaryBuildWiktionaryCli,
)
from scinoephile.common.testing import run_cli_with_args
from scinoephile.dictionaries.wiktionary import WiktionaryDictionaryService


def test_dictionary_build_wiktionary_exits_cleanly_on_missing_source(
    monkeypatch: MonkeyPatch,
):
    """Exit with status 1 when the service reports a missing source file.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    stdout = StringIO()
    stderr = StringIO()

    def _mock_build(self, **kwargs: Any) -> Path:
        """Simulate a service-level missing-source failure.

        Arguments:
            self: mocked service instance
            **kwargs: unused build keyword arguments
        Returns:
            never returns
        """
        raise FileNotFoundError("Wiktionary source JSONL not found")

    monkeypatch.setattr(WiktionaryDictionaryService, "build", _mock_build)

    with raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(DictionaryBuildWiktionaryCli, "")

    assert excinfo.value.code == 1
    assert stdout.getvalue() == ""


def test_dictionary_build_wiktionary_exits_cleanly_on_download_error(
    monkeypatch: MonkeyPatch,
):
    """Exit with status 1 when the service reports a download error.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    stdout = StringIO()
    stderr = StringIO()

    def _mock_build(self, **kwargs: Any) -> Path:
        """Simulate a service-level download failure.

        Arguments:
            self: mocked service instance
            **kwargs: unused build keyword arguments
        Returns:
            never returns
        """
        raise requests.RequestException("download failed")

    monkeypatch.setattr(WiktionaryDictionaryService, "build", _mock_build)

    with raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(DictionaryBuildWiktionaryCli, "")

    assert excinfo.value.code == 1
    assert stdout.getvalue() == ""
