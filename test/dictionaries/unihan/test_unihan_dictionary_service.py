#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.dictionaries.unihan.UnihanDictionaryService."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
import requests

from scinoephile.common.file import get_temp_directory_path, get_temp_file_path
from scinoephile.dictionaries.unihan import UnihanDictionaryService


@pytest.fixture
def local_data_dir_path() -> Generator[Path]:
    """Provide a temporary canonical local data directory."""
    with get_temp_directory_path() as dir_path:
        yield dir_path


@pytest.fixture
def runtime_data_dir_path() -> Generator[Path]:
    """Provide a temporary runtime canonical data directory."""
    with get_temp_directory_path() as dir_path:
        yield dir_path


@pytest.fixture
def database_path() -> Generator[Path]:
    """Provide a temporary SQLite database path."""
    with get_temp_file_path(".db") as temp_path:
        yield temp_path


def _write_fixture_sources(base_dir_path: Path):
    """Write deterministic Unihan source fixture files.

    Arguments:
        base_dir_path: output directory path
    """
    base_dir_path.mkdir(parents=True, exist_ok=True)
    (base_dir_path / "Unihan_Variants.txt").write_text(
        "U+4E07\tkTraditionalVariant\tU+842C\n",
        encoding="utf-8",
    )
    (base_dir_path / "Unihan_Readings.txt").write_text(
        (
            "U+4E00\tkCantonese\tjat1\n"
            "U+4E00\tkMandarin\tyī\n"
            "U+4E00\tkDefinition\tone\n"
            "U+842C\tkCantonese\tmaan6\n"
            "U+842C\tkMandarin\twàn\n"
            "U+842C\tkDefinition\tten thousand\n"
        ),
        encoding="utf-8",
    )
    (base_dir_path / "Unihan_DictionaryLikeData.txt").write_text(
        ("U+4E00\tkCangjie\tM\nU+842C\tkCangjie\tDQ\n"),
        encoding="utf-8",
    )


def test_build_uses_local_source_data(
    database_path: Path,
    local_data_dir_path: Path,
    runtime_data_dir_path: Path,
):
    """Build Unihan DB from local source files when available.

    Arguments:
        database_path: temporary SQLite database path
        local_data_dir_path: local canonical data directory
        runtime_data_dir_path: runtime canonical data directory
    """
    _write_fixture_sources(local_data_dir_path)
    service = UnihanDictionaryService(
        database_path=database_path,
        local_data_dir_path=local_data_dir_path,
        runtime_data_dir_path=runtime_data_dir_path,
    )

    service.build(overwrite=True)

    entries = service.lookup("萬", limit=5)
    assert [entry.simplified for entry in entries] == ["万"]


def test_build_downloads_when_local_sources_missing(
    database_path: Path,
    local_data_dir_path: Path,
    runtime_data_dir_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Build Unihan DB by downloading when local source files are missing.

    Arguments:
        database_path: temporary SQLite database path
        local_data_dir_path: local canonical data directory
        runtime_data_dir_path: runtime canonical data directory
        monkeypatch: pytest monkeypatch fixture
    """
    service = UnihanDictionaryService(
        database_path=database_path,
        local_data_dir_path=local_data_dir_path,
        runtime_data_dir_path=runtime_data_dir_path,
    )

    def _download_and_extract_to_runtime() -> dict[str, Path]:
        """Mock download by writing fixture sources.

        Returns:
            runtime source paths
        """
        _write_fixture_sources(runtime_data_dir_path)
        return {
            "Unihan_DictionaryLikeData.txt": runtime_data_dir_path
            / "Unihan_DictionaryLikeData.txt",
            "Unihan_Readings.txt": runtime_data_dir_path / "Unihan_Readings.txt",
            "Unihan_Variants.txt": runtime_data_dir_path / "Unihan_Variants.txt",
        }

    monkeypatch.setattr(
        service,
        "_download_and_extract_to_runtime",
        _download_and_extract_to_runtime,
    )

    service.build(overwrite=True)

    entries = service.lookup("yi1", limit=5)
    assert [entry.traditional for entry in entries] == ["一"]


def test_build_updates_local_data_from_existing_runtime_files(
    database_path: Path,
    local_data_dir_path: Path,
    runtime_data_dir_path: Path,
):
    """Update local source files from existing runtime source files.

    Arguments:
        database_path: temporary SQLite database path
        local_data_dir_path: local canonical data directory
        runtime_data_dir_path: runtime canonical data directory
    """
    _write_fixture_sources(runtime_data_dir_path)

    service = UnihanDictionaryService(
        database_path=database_path,
        local_data_dir_path=local_data_dir_path,
        runtime_data_dir_path=runtime_data_dir_path,
    )

    service.build(overwrite=True, update_local_data=True)

    for filename in (
        "Unihan_DictionaryLikeData.txt",
        "Unihan_Readings.txt",
        "Unihan_Variants.txt",
    ):
        assert (local_data_dir_path / filename).exists()
        assert (local_data_dir_path / filename).read_text(encoding="utf-8") == (
            runtime_data_dir_path / filename
        ).read_text(encoding="utf-8")


def test_download_and_extract_raises_file_not_found_for_missing_archive_member(
    runtime_data_dir_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Raise FileNotFoundError when Unihan.zip is missing a required source file.

    Arguments:
        runtime_data_dir_path: runtime canonical data directory
        monkeypatch: pytest monkeypatch fixture
    """

    class _Response:
        """Mock requests response."""

        content = b"placeholder zip bytes"

        @staticmethod
        def raise_for_status():
            """Succeed without error."""

    class _ArchiveSource:
        """Mock zip member reader."""

        def __enter__(self) -> _ArchiveSource:
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        @staticmethod
        def read() -> bytes:
            """Return deterministic source content."""
            return b"U+4E00\tkDefinition\tone\n"

    class _Archive:
        """Mock zip archive with one missing member."""

        def __enter__(self) -> _Archive:
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        @staticmethod
        def open(filename: str, mode: str = "r") -> _ArchiveSource:
            """Open one archive member or simulate a missing file.

            Arguments:
                filename: archive member filename
                mode: zipfile open mode
            Returns:
                source reader
            """
            if filename == "Unihan_Readings.txt":
                raise KeyError(filename)
            return _ArchiveSource()

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: _Response())
    monkeypatch.setattr("zipfile.ZipFile", lambda *args, **kwargs: _Archive())

    service = UnihanDictionaryService(runtime_data_dir_path=runtime_data_dir_path)

    with pytest.raises(FileNotFoundError, match="Unihan_Readings.txt"):
        service._download_and_extract_to_runtime()
