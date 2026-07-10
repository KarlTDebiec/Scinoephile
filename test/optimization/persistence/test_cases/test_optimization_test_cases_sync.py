#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for JSON to normalized SQLite synchronization."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import JsonValue
from pytest import raises

from scinoephile import common
from scinoephile.core import ScinoephileError
from scinoephile.llms.punctuation import PunctuationManager
from scinoephile.llms.review import ReviewManager, ReviewPrompt
from scinoephile.llms.translation import TranslationManager
from scinoephile.optimization.persistence.test_cases import (
    PersistedTestCase,
    TestCaseSqliteStore,
)
from scinoephile.optimization.persistence.test_cases.id import get_test_case_id
from scinoephile.optimization.persistence.test_cases.sync import (
    sync_test_cases,
)

_LOCALIZED_REVIEW_PROMPT = ReviewPrompt.from_attributes(
    attributes={
        "input_pfx": "zimu_",
        "output_pfx": "xiugai_",
        "note_pfx": "beizhu_",
    }
)
"""Review prompt using localized correspondence field names."""

_ALTERNATIVE_REVIEW_PROMPT = ReviewPrompt.from_attributes(
    attributes={
        "input_pfx": "source_",
        "output_pfx": "correction_",
        "note_pfx": "explanation_",
    }
)
"""Review prompt using an alternative correspondence schema."""


def test_normalization_makes_prompt_field_aliases_share_identity():
    """Equivalent field aliases should normalize to one SQL identity."""
    localized_cls = ReviewManager.get_test_case_cls(
        size=1,
        prompt=_LOCALIZED_REVIEW_PROMPT,
    )
    alternative_cls = ReviewManager.get_test_case_cls(
        size=1,
        prompt=_ALTERNATIVE_REVIEW_PROMPT,
    )
    localized = localized_cls.model_validate(
        {
            "query": {"zimu_1": "original"},
            "answer": {"xiugai_1": "corrected", "beizhu_1": "typo"},
        }
    )
    alternative = alternative_cls.model_validate(
        {
            "query": {"source_1": "original"},
            "answer": {
                "correction_1": "corrected",
                "explanation_1": "typo",
            },
        }
    )
    localized_persisted = PersistedTestCase.from_test_case(
        localized,
        ReviewManager,
    )
    alternative_persisted = PersistedTestCase.from_test_case(
        alternative,
        ReviewManager,
    )

    assert localized_persisted.query == {"subtitle_1": "original"}
    assert localized_persisted.answer == {
        "revised_1": "corrected",
        "note_1": "typo",
    }
    assert localized_persisted.test_case_id == alternative_persisted.test_case_id


def test_sync_rejects_fields_outside_test_case_schema(tmp_path: Path):
    """Unexpected test-case and payload fields should be rejected."""
    source_path = tmp_path / "source.json"
    invalid_test_cases = [
        {
            "query": {"input_1": "a"},
            "answer": {"output_1": "b"},
            "unexpected": True,
        },
        {
            "query": {"input_1": "a", "unexpected": True},
            "answer": {"output_1": "b"},
        },
    ]
    for test_case in invalid_test_cases:
        source_path.write_text(json.dumps([test_case]), encoding="utf-8")
        with raises(ScinoephileError, match="Extra inputs are not permitted"):
            sync_test_cases(
                [source_path],
                tmp_path / "test_cases.sqlite",
                TranslationManager,
                dry_run=False,
            )


def test_sync_inserts_and_removes_provenance_by_source_path(
    tmp_path: Path,
    monkeypatch,
):
    """Sync should insert and remove provenance links per source JSON."""
    monkeypatch.chdir(tmp_path)
    database_path = Path("test_cases.sqlite")
    source_path = Path("source.json")
    deleted_query: dict[str, JsonValue] = {"input_1": "c"}
    deleted_answer: dict[str, JsonValue] = {"output_1": "d"}
    first_data = [
        {
            "query": {"input_1": "a"},
            "answer": {"output_1": "b"},
            "verified": True,
        },
        {
            "query": deleted_query,
            "answer": deleted_answer,
        },
    ]
    source_path.write_text(json.dumps(first_data), encoding="utf-8")

    first_report = sync_test_cases(
        [source_path],
        database_path,
        TranslationManager,
        dry_run=False,
    )
    assert len(first_report.insert_ids) == 2
    deleted_id = get_test_case_id(
        deleted_query,
        deleted_answer,
        TranslationManager,
    )

    source_path.write_text(json.dumps(first_data[:1]), encoding="utf-8")
    second_report = sync_test_cases(
        [source_path],
        database_path,
        TranslationManager,
        dry_run=False,
    )

    assert second_report.delete_ids == (deleted_id,)
    retained = TestCaseSqliteStore(database_path).get_test_case(deleted_id)
    assert retained is not None
    assert retained.source_paths == ()


def test_sync_canonicalizes_source_paths(tmp_path: Path, monkeypatch):
    """Sync should treat relative and absolute paths as the same source."""
    monkeypatch.chdir(tmp_path)
    database_path = Path("test_cases.sqlite")
    source_path = Path("source.json")
    source_path.write_text(
        json.dumps([{"query": {"input_1": "a"}, "answer": {"output_1": "b"}}]),
        encoding="utf-8",
    )
    first_report = sync_test_cases(
        [source_path],
        database_path,
        TranslationManager,
        dry_run=False,
    )

    source_path.write_text("[]\n", encoding="utf-8")
    second_report = sync_test_cases(
        [source_path.resolve()],
        database_path,
        TranslationManager,
        dry_run=False,
    )

    assert second_report.delete_ids == first_report.insert_ids


def test_sync_does_not_overwrite_sql_owned_metadata(tmp_path: Path):
    """JSON synchronization should not overwrite SQL-owned metadata."""
    database_path = tmp_path / "test_cases.sqlite"
    source_path = tmp_path / "source.json"
    data = [
        {
            "query": {"input_1": "a"},
            "answer": {"output_1": "b"},
            "difficulty": 1,
        }
    ]
    source_path.write_text(json.dumps(data), encoding="utf-8")
    first_report = sync_test_cases(
        [source_path],
        database_path,
        TranslationManager,
        dry_run=False,
    )

    data[0]["difficulty"] = 2
    data[0]["prompt"] = True
    data[0]["verified"] = True
    source_path.write_text(json.dumps(data), encoding="utf-8")
    dry_run_report = sync_test_cases(
        [source_path],
        database_path,
        TranslationManager,
        dry_run=True,
    )

    assert dry_run_report.insert_ids == ()
    assert dry_run_report.delete_ids == ()
    loaded_before_write = TestCaseSqliteStore(database_path).get_test_case(
        first_report.insert_ids[0]
    )
    assert loaded_before_write is not None
    assert loaded_before_write.difficulty == 1

    sync_test_cases(
        [source_path],
        database_path,
        TranslationManager,
        dry_run=False,
    )
    loaded = TestCaseSqliteStore(database_path).get_test_case(
        first_report.insert_ids[0]
    )
    assert loaded is not None
    assert loaded.difficulty == 1
    assert not loaded.prompt
    assert not loaded.verified


def test_sync_validates_all_inputs_before_writing(tmp_path: Path):
    """An invalid later source should prevent all database writes."""
    database_path = tmp_path / "test_cases.sqlite"
    valid_path = tmp_path / "valid.json"
    invalid_path = tmp_path / "invalid.json"
    valid_path.write_text(
        json.dumps([{"query": {"input_1": "a"}, "answer": {"output_1": "b"}}]),
        encoding="utf-8",
    )
    invalid_path.write_text(
        json.dumps(
            [
                {
                    "query": {"input_1": "c"},
                    "answer": {"output_1": "d"},
                    "difficulty": "hard",
                }
            ]
        ),
        encoding="utf-8",
    )

    with raises(ScinoephileError, match="valid integer"):
        sync_test_cases(
            [valid_path, invalid_path],
            database_path,
            TranslationManager,
            dry_run=False,
        )

    assert not database_path.exists()


def test_sync_loads_canonical_repository_data(tmp_path: Path):
    """Canonical repository fields should be stored unchanged."""
    source_path = (
        common.package_root.parent
        / "test/data/kob/output/zho-Hant_ocr/lang/zho/review.json"
    )
    raw_data = json.loads(source_path.read_text(encoding="utf-8"))
    database_path = tmp_path / "test_cases.sqlite"

    sync_test_cases(
        [source_path],
        database_path,
        ReviewManager,
        dry_run=False,
    )
    loaded = TestCaseSqliteStore(database_path).get_test_cases_by_source_path(
        str(source_path.resolve()),
        manager_cls=ReviewManager,
    )

    assert len(loaded) == len(raw_data)
    assert all(
        all(field.startswith("subtitle_") for field in test_case.query)
        for test_case in loaded
    )
    assert all(
        all(field.startswith(("revised_", "note_")) for field in test_case.answer)
        for test_case in loaded
    )
    raw_subtitles = {item["query"]["subtitle_1"] for item in raw_data}
    assert {test_case.query["subtitle_1"] for test_case in loaded} == raw_subtitles


def test_sync_round_trips_unbounded_lists(tmp_path: Path):
    """JSON list payloads should not have a persistence width limit."""
    source_path = tmp_path / "source.json"
    source_path.write_text(
        json.dumps(
            [
                {
                    "query": {
                        "one": [f"line {idx}" for idx in range(36)],
                        "two": "reference",
                    },
                    "answer": {"output": "output"},
                }
            ]
        ),
        encoding="utf-8",
    )
    database_path = tmp_path / "test_cases.sqlite"

    sync_test_cases(
        [source_path],
        database_path,
        PunctuationManager,
        dry_run=False,
    )
    loaded = TestCaseSqliteStore(database_path).get_test_cases_by_source_path(
        str(source_path.resolve())
    )

    list_lengths: list[int] = []
    for test_case in loaded:
        value = test_case.query.get("one")
        if isinstance(value, list):
            list_lengths.append(len(value))
    assert max(list_lengths) >= 36
