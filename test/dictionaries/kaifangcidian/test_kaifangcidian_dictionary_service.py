#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.dictionaries.kaifangcidian.KaifangcidianDictionaryService."""

from __future__ import annotations

import csv
from collections.abc import Generator
from pathlib import Path

import pytest

from scinoephile.common.file import get_temp_directory_path, get_temp_file_path
from scinoephile.dictionaries.kaifangcidian import KaifangcidianDictionaryService


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


def _write_fixture_csv(csv_path: Path):
    """Write a deterministic Kaifangcidian canonical CSV fixture.

    Arguments:
        csv_path: output canonical CSV path
    """
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=[
                "kind",
                "traditional",
                "simplified",
                "pinyin",
                "jyutping",
                "definition",
                "note",
                "variants",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "kind": "ci",
                "traditional": "山坑",
                "simplified": "山坑",
                "pinyin": "shan1 keng1",
                "jyutping": "saan1 haang1",
                "definition": "gully",
                "note": "",
                "variants": "",
            }
        )
        writer.writerow(
            {
                "kind": "ci",
                "traditional": "共享",
                "simplified": "共享",
                "pinyin": "gong4 xiang3",
                "jyutping": "gung6 hoeng2",
                "definition": "share",
                "note": "test note",
                "variants": "共用",
            }
        )


def test_build_uses_local_csv_data(
    database_path: Path,
    local_data_dir_path: Path,
    runtime_data_dir_path: Path,
):
    """Build Kaifangcidian DB from local canonical CSV when available.

    Arguments:
        database_path: temporary SQLite database path
        local_data_dir_path: local canonical data directory
        runtime_data_dir_path: runtime canonical data directory
    """
    _write_fixture_csv(local_data_dir_path / "entries.csv")
    service = KaifangcidianDictionaryService(
        database_path=database_path,
        local_data_dir_path=local_data_dir_path,
        runtime_data_dir_path=runtime_data_dir_path,
    )

    service.build(overwrite=True)

    entries = service.lookup("共享", limit=5)
    assert [entry.traditional for entry in entries] == ["共享"]
    assert entries[0].definitions


def test_build_downloads_when_local_csv_missing(
    database_path: Path,
    local_data_dir_path: Path,
    runtime_data_dir_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Build Kaifangcidian DB by downloading when local CSV is missing.

    Arguments:
        database_path: temporary SQLite database path
        local_data_dir_path: local canonical data directory
        runtime_data_dir_path: runtime canonical data directory
        monkeypatch: pytest monkeypatch fixture
    """
    service = KaifangcidianDictionaryService(
        database_path=database_path,
        local_data_dir_path=local_data_dir_path,
        runtime_data_dir_path=runtime_data_dir_path,
    )

    def _download_to_csv(csv_path: Path) -> Path:
        """Mock downloader by writing fixture canonical CSV.

        Arguments:
            csv_path: canonical CSV output path
        Returns:
            canonical CSV path
        """
        _write_fixture_csv(csv_path)
        return csv_path

    monkeypatch.setattr(service.downloader, "download_to_csv", _download_to_csv)

    service.build(overwrite=True)

    entries = service.lookup("山坑", limit=5)
    assert [entry.traditional for entry in entries] == ["山坑"]


def test_build_updates_local_data_from_existing_runtime_csv(
    database_path: Path,
    local_data_dir_path: Path,
    runtime_data_dir_path: Path,
):
    """Update local canonical CSV from an existing runtime CSV.

    Arguments:
        database_path: temporary SQLite database path
        local_data_dir_path: local canonical data directory
        runtime_data_dir_path: runtime canonical data directory
    """
    runtime_csv_path = runtime_data_dir_path / "entries.csv"
    local_csv_path = local_data_dir_path / "entries.csv"
    _write_fixture_csv(runtime_csv_path)

    service = KaifangcidianDictionaryService(
        database_path=database_path,
        local_data_dir_path=local_data_dir_path,
        runtime_data_dir_path=runtime_data_dir_path,
    )

    service.build(overwrite=True, update_local_data=True)

    assert local_csv_path.exists()
    assert local_csv_path.read_text(encoding="utf-8") == runtime_csv_path.read_text(
        encoding="utf-8"
    )
