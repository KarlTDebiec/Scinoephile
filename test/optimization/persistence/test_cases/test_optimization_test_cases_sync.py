#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for JSON to normalized SQLite synchronization."""

from __future__ import annotations

import json
from pathlib import Path

from pytest import raises

from scinoephile import common
from scinoephile.core import ScinoephileError
from scinoephile.optimization.persistence.test_cases import TestCaseSqliteStore
from scinoephile.optimization.persistence.test_cases.id import get_test_case_id
from scinoephile.optimization.persistence.test_cases.sync import (
    sync_test_cases_from_json_paths,
)


def test_sync_inserts_and_deletes_by_source_path(tmp_path: Path, monkeypatch):
    """Sync should insert new IDs and delete obsolete IDs per source JSON."""
    monkeypatch.chdir(tmp_path)
    database_path = Path("test_cases.sqlite")
    source_path = Path("source.json")
    first_data = [
        {
            "query": {"input_1": "a"},
            "answer": {"output_1": "b"},
            "verified": True,
        },
        {
            "query": {"input_1": "c"},
            "answer": {"output_1": "d"},
        },
    ]
    source_path.write_text(json.dumps(first_data), encoding="utf-8")

    first_report = sync_test_cases_from_json_paths(
        database_path=database_path,
        operation="translation",
        variant="unit",
        input_paths=[source_path],
        dry_run=False,
    )
    assert len(first_report.insert_ids) == 2
    deleted_id = get_test_case_id(
        first_data[1]["query"],
        first_data[1]["answer"],
        operation="translation",
        variant="unit",
    )

    source_path.write_text(json.dumps(first_data[:1]), encoding="utf-8")
    second_report = sync_test_cases_from_json_paths(
        database_path=database_path,
        operation="translation",
        variant="unit",
        input_paths=[source_path],
        dry_run=False,
    )

    assert second_report.delete_ids == (deleted_id,)
    assert TestCaseSqliteStore(database_path).get_test_case(deleted_id) is None


def test_sync_canonicalizes_source_paths(tmp_path: Path, monkeypatch):
    """Sync should treat relative and absolute paths as the same source."""
    monkeypatch.chdir(tmp_path)
    database_path = Path("test_cases.sqlite")
    source_path = Path("source.json")
    source_path.write_text(
        json.dumps([{"query": {"q": "a"}, "answer": {"a": "b"}}]),
        encoding="utf-8",
    )
    first_report = sync_test_cases_from_json_paths(
        database_path=database_path,
        operation="unit",
        variant="basic",
        input_paths=[source_path],
        dry_run=False,
    )

    source_path.write_text("[]\n", encoding="utf-8")
    second_report = sync_test_cases_from_json_paths(
        database_path=database_path,
        operation="unit",
        variant="basic",
        input_paths=[source_path.resolve()],
        dry_run=False,
    )

    assert second_report.delete_ids == first_report.insert_ids


def test_sync_dry_run_reports_source_metadata_updates(tmp_path: Path):
    """Dry-run sync should report source-specific metadata updates."""
    database_path = tmp_path / "test_cases.sqlite"
    source_path = tmp_path / "source.json"
    data = [
        {
            "query": {"q": "a"},
            "answer": {"a": "b"},
            "difficulty": 1,
        }
    ]
    source_path.write_text(json.dumps(data), encoding="utf-8")
    first_report = sync_test_cases_from_json_paths(
        database_path=database_path,
        operation="unit",
        variant="basic",
        input_paths=[source_path],
        dry_run=False,
    )

    data[0]["difficulty"] = 2
    data[0]["prompt"] = True
    data[0]["verified"] = True
    source_path.write_text(json.dumps(data), encoding="utf-8")
    dry_run_report = sync_test_cases_from_json_paths(
        database_path=database_path,
        operation="unit",
        variant="basic",
        input_paths=[source_path],
        dry_run=True,
    )

    assert dry_run_report.insert_ids == ()
    assert dry_run_report.update_ids == first_report.insert_ids
    loaded_before_write = TestCaseSqliteStore(database_path).get_test_case(
        first_report.insert_ids[0]
    )
    assert loaded_before_write is not None
    assert loaded_before_write.difficulty == 1

    sync_test_cases_from_json_paths(
        database_path=database_path,
        operation="unit",
        variant="basic",
        input_paths=[source_path],
        dry_run=False,
    )
    loaded = TestCaseSqliteStore(database_path).get_test_case(
        first_report.insert_ids[0]
    )
    assert loaded is not None
    assert loaded.difficulty == 2
    assert loaded.prompt
    assert loaded.verified


def test_sync_validates_all_inputs_before_writing(tmp_path: Path):
    """An invalid later source should prevent all database writes."""
    database_path = tmp_path / "test_cases.sqlite"
    valid_path = tmp_path / "valid.json"
    invalid_path = tmp_path / "invalid.json"
    valid_path.write_text(
        json.dumps([{"query": {"q": "a"}, "answer": {"a": "b"}}]),
        encoding="utf-8",
    )
    invalid_path.write_text(
        json.dumps(
            [
                {
                    "query": {"q": "c"},
                    "answer": {"a": "d"},
                    "difficulty": "hard",
                }
            ]
        ),
        encoding="utf-8",
    )

    with raises(ScinoephileError, match="difficulty must be an integer"):
        sync_test_cases_from_json_paths(
            database_path=database_path,
            operation="unit",
            variant="basic",
            input_paths=[valid_path, invalid_path],
            dry_run=False,
        )

    assert not database_path.exists()


def test_sync_round_trips_localized_repository_data(tmp_path: Path):
    """Localized fields should survive SQL persistence without prompt parsing."""
    source_path = (
        common.package_root.parent
        / "test/data/kob/output/zho-Hant_ocr/lang/zho/review.json"
    )
    raw_data = json.loads(source_path.read_text(encoding="utf-8"))
    database_path = tmp_path / "test_cases.sqlite"

    sync_test_cases_from_json_paths(
        database_path=database_path,
        operation="review",
        variant="zho-hant",
        input_paths=[source_path],
        dry_run=False,
    )
    loaded = TestCaseSqliteStore(database_path).get_test_cases_by_source_path(
        str(source_path.resolve()),
        operation="review",
        variant="zho-hant",
    )

    raw_payloads = {
        json.dumps(
            {"query": item["query"], "answer": item["answer"]},
            ensure_ascii=False,
            sort_keys=True,
        )
        for item in raw_data
    }
    loaded_payloads = {
        json.dumps(
            {"query": test_case.query, "answer": test_case.answer},
            ensure_ascii=False,
            sort_keys=True,
        )
        for test_case in loaded
    }
    assert loaded_payloads == raw_payloads


def test_sync_round_trips_unbounded_lists(tmp_path: Path):
    """JSON list payloads should not have a persistence width limit."""
    source_path = (
        common.package_root.parent
        / "test/data/kob/output/yue-Hans_transcribe/test_simplified/"
        "multilang/yue_zho/transcription/punctuation/mps.json"
    )
    database_path = tmp_path / "test_cases.sqlite"

    sync_test_cases_from_json_paths(
        database_path=database_path,
        operation="yue-zho-transcription-punctuation",
        variant="yue-hans",
        input_paths=[source_path],
        dry_run=False,
    )
    loaded = TestCaseSqliteStore(database_path).get_test_cases_by_source_path(
        str(source_path.resolve())
    )

    list_lengths: list[int] = []
    for test_case in loaded:
        value = test_case.query.get("yuewen_to_punctuate")
        if isinstance(value, list):
            list_lengths.append(len(value))
    assert max(list_lengths) >= 36
