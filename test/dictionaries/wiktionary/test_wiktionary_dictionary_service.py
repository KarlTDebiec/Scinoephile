#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.dictionaries.wiktionary.WiktionaryDictionaryService."""

from __future__ import annotations

import json
from collections.abc import Generator
from pathlib import Path

import pytest
import requests

from scinoephile.common.file import get_temp_directory_path, get_temp_file_path
from scinoephile.dictionaries.wiktionary import WiktionaryDictionaryService


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


def _write_fixture_jsonl(jsonl_path: Path):
    """Write a deterministic Kaikki JSONL fixture.

    Arguments:
        jsonl_path: output JSONL path
    """
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        {
            "word": "學生",
            "pos": "noun",
            "sounds": [
                {
                    "tags": ["Mandarin", "Pinyin", "standard"],
                    "zh-pron": "xuéshēng",
                },
                {
                    "tags": ["Cantonese", "Guangzhou", "Jyutping"],
                    "zh-pron": "hok⁶ saang¹",
                },
            ],
            "senses": [{"glosses": ["student"]}],
        },
        {
            "word": "行",
            "pos": "verb",
            "sounds": [
                {
                    "tags": ["Mandarin", "Pinyin", "standard"],
                    "zh-pron": "háng",
                },
                {
                    "tags": ["Cantonese", "Guangzhou", "Jyutping"],
                    "zh-pron": "ha⁴ng",
                },
            ],
            "senses": [{"glosses": ["to go"]}],
        },
    ]
    jsonl_path.write_text(
        "".join(f"{json.dumps(line, ensure_ascii=False)}\n" for line in lines),
        encoding="utf-8",
    )


def test_build_uses_local_jsonl_data(
    database_path: Path,
    local_data_dir_path: Path,
    runtime_data_dir_path: Path,
):
    """Build Wiktionary DB from local canonical JSONL when available.

    Arguments:
        database_path: temporary SQLite database path
        local_data_dir_path: local canonical data directory
        runtime_data_dir_path: runtime canonical data directory
    """
    _write_fixture_jsonl(local_data_dir_path / "entries.jsonl")
    service = WiktionaryDictionaryService(
        database_path=database_path,
        local_data_dir_path=local_data_dir_path,
        runtime_data_dir_path=runtime_data_dir_path,
    )

    service.build(overwrite=True)

    entries = service.lookup("學生", limit=5)
    assert [entry.simplified for entry in entries] == ["学生"]


def test_build_uses_explicit_source_jsonl_path(
    database_path: Path,
    local_data_dir_path: Path,
    runtime_data_dir_path: Path,
):
    """Build Wiktionary DB from an explicit Kaikki JSONL source path.

    Arguments:
        database_path: temporary SQLite database path
        local_data_dir_path: local canonical data directory
        runtime_data_dir_path: runtime canonical data directory
    """
    source_jsonl_path = runtime_data_dir_path / "input.jsonl"
    _write_fixture_jsonl(source_jsonl_path)
    service = WiktionaryDictionaryService(
        database_path=database_path,
        local_data_dir_path=local_data_dir_path,
        runtime_data_dir_path=runtime_data_dir_path / "runtime",
    )

    service.build(overwrite=True, source_jsonl_path=source_jsonl_path)

    entries = service.lookup("hang2", limit=5)
    assert [entry.traditional for entry in entries] == ["行"]


def test_build_updates_local_data_from_existing_runtime_jsonl(
    database_path: Path,
    local_data_dir_path: Path,
    runtime_data_dir_path: Path,
):
    """Update local canonical JSONL from an existing runtime canonical JSONL.

    Arguments:
        database_path: temporary SQLite database path
        local_data_dir_path: local canonical data directory
        runtime_data_dir_path: runtime canonical data directory
    """
    runtime_jsonl_path = runtime_data_dir_path / "entries.jsonl"
    local_jsonl_path = local_data_dir_path / "entries.jsonl"
    _write_fixture_jsonl(runtime_jsonl_path)

    service = WiktionaryDictionaryService(
        database_path=database_path,
        local_data_dir_path=local_data_dir_path,
        runtime_data_dir_path=runtime_data_dir_path,
    )

    service.build(overwrite=True, update_local_data=True)

    assert local_jsonl_path.exists()
    assert local_jsonl_path.read_text(encoding="utf-8") == runtime_jsonl_path.read_text(
        encoding="utf-8"
    )


def test_build_downloads_when_no_source_jsonl_available(
    database_path: Path,
    local_data_dir_path: Path,
    runtime_data_dir_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Build Wiktionary DB by downloading when no source JSONL is available.

    Arguments:
        database_path: temporary SQLite database path
        local_data_dir_path: local canonical data directory
        runtime_data_dir_path: runtime canonical data directory
        monkeypatch: pytest monkeypatch fixture
    """
    service = WiktionaryDictionaryService(
        database_path=database_path,
        local_data_dir_path=local_data_dir_path,
        runtime_data_dir_path=runtime_data_dir_path,
    )

    def _download_to_runtime_jsonl() -> Path:
        """Mock download by writing fixture canonical JSONL.

        Returns:
            runtime canonical JSONL path
        """
        runtime_jsonl_path = runtime_data_dir_path / "entries.jsonl"
        _write_fixture_jsonl(runtime_jsonl_path)
        return runtime_jsonl_path

    monkeypatch.setattr(
        service, "_download_to_runtime_jsonl", _download_to_runtime_jsonl
    )

    service.build(overwrite=True)

    entries = service.lookup("學生", limit=5)
    assert [entry.traditional for entry in entries] == ["學生"]


def test_build_raises_on_download_error(
    database_path: Path,
    local_data_dir_path: Path,
    runtime_data_dir_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Raise RequestException when Kaikki download fails.

    Arguments:
        database_path: temporary SQLite database path
        local_data_dir_path: local canonical data directory
        runtime_data_dir_path: runtime canonical data directory
        monkeypatch: pytest monkeypatch fixture
    """
    service = WiktionaryDictionaryService(
        database_path=database_path,
        local_data_dir_path=local_data_dir_path,
        runtime_data_dir_path=runtime_data_dir_path,
    )

    def _download_to_runtime_jsonl() -> Path:
        """Mock download failure.

        Returns:
            never returns
        """
        raise requests.RequestException("network down")

    monkeypatch.setattr(
        service, "_download_to_runtime_jsonl", _download_to_runtime_jsonl
    )

    with pytest.raises(requests.RequestException, match="network down"):
        service.build(overwrite=True)
