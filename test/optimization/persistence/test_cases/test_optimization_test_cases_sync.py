#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for JSON to normalized SQLite synchronization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import ClassVar

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

_BASE_REVIEW_PROMPT = ReviewPrompt(
    subtitles="base_subtitles",
    revisions="base_revisions",
    index="base_index",
    text="base_text",
    note="base_note",
)
"""Review prompt whose aliases intentionally differ from semantic field names."""

_LOCALIZED_REVIEW_PROMPT = ReviewPrompt(
    subtitles="zimu",
    revisions="xiugai",
    index="xuhao",
    text="wenben",
    note="beizhu",
)
"""Review prompt using localized correspondence field names."""

_ALTERNATIVE_REVIEW_PROMPT = ReviewPrompt(
    subtitles="sources",
    revisions="corrections",
    index="position",
    text="content",
    note="explanation",
)
"""Review prompt using an alternative correspondence schema."""


class _AliasedBaseReviewManager(ReviewManager):
    """Review manager with distinct semantic, base, and localized field names."""

    operation: ClassVar[str] = "aliased-base-review"
    """Stable operation identifier used in persistence."""
    base_prompt: ClassVar[ReviewPrompt] = _BASE_REVIEW_PROMPT
    """Prompt defining intentionally distinct persisted field names."""


def _get_translation_answer(text: str) -> dict[str, JsonValue]:
    """Get a canonical translation answer payload."""
    return {"outputs": [{"index": 1, "text": text}]}


def _get_translation_query(text: str) -> dict[str, JsonValue]:
    """Get a canonical translation query payload."""
    return {"subtitles": [{"index": 1, "text": text}]}


def test_normalization_makes_prompt_field_aliases_share_identity(tmp_path: Path):
    """Equivalent aliases should normalize to one base-aliased SQL identity."""
    localized_cls = _AliasedBaseReviewManager.get_test_case_cls(
        _LOCALIZED_REVIEW_PROMPT
    )
    alternative_cls = _AliasedBaseReviewManager.get_test_case_cls(
        _ALTERNATIVE_REVIEW_PROMPT
    )
    localized = localized_cls.model_validate(
        {
            "query": {"zimu": [{"xuhao": 1, "wenben": "original"}]},
            "answer": {
                "xiugai": [
                    {
                        "xuhao": 1,
                        "wenben": "corrected",
                        "beizhu": "typo",
                    }
                ]
            },
        }
    )
    alternative = alternative_cls.model_validate(
        {
            "query": {"sources": [{"position": 1, "content": "original"}]},
            "answer": {
                "corrections": [
                    {
                        "position": 1,
                        "content": "corrected",
                        "explanation": "typo",
                    }
                ]
            },
        }
    )
    localized_persisted = PersistedTestCase.from_test_case(
        localized,
        _AliasedBaseReviewManager,
    )
    alternative_persisted = PersistedTestCase.from_test_case(
        alternative,
        _AliasedBaseReviewManager,
    )

    assert localized_persisted.query == {
        "base_subtitles": [{"base_index": 1, "base_text": "original"}]
    }
    assert localized_persisted.answer == {
        "base_revisions": [
            {
                "base_index": 1,
                "base_text": "corrected",
                "base_note": "typo",
            }
        ]
    }
    assert localized_persisted.test_case_id == alternative_persisted.test_case_id

    store = TestCaseSqliteStore(tmp_path / "test_cases.sqlite")
    store.sync_source_paths(
        {"aliases.json": [localized_persisted]},
        manager_cls=_AliasedBaseReviewManager,
        dry_run=False,
    )
    loaded = store.get_test_case(localized_persisted.test_case_id)
    assert loaded is not None
    assert loaded.query == localized_persisted.query
    assert loaded.answer == localized_persisted.answer


def test_sync_rejects_fields_outside_test_case_schema(tmp_path: Path):
    """Unexpected test-case and payload fields should be rejected."""
    source_path = tmp_path / "source.json"
    invalid_test_cases = [
        {
            "query": _get_translation_query("a"),
            "answer": _get_translation_answer("b"),
            "unexpected": True,
        },
        {
            "query": {
                **_get_translation_query("a"),
                "unexpected": True,
            },
            "answer": _get_translation_answer("b"),
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


def test_sync_requires_base_prompt_aliases(tmp_path: Path):
    """Optimization sync should use the shared base-alias-only JSON boundary."""
    source_path = tmp_path / "source.json"
    source_path.write_text(
        json.dumps(
            [
                {
                    "query": {"subtitles": [{"index": 1, "text": "original"}]},
                    "answer": {
                        "revisions": [{"index": 1, "text": "corrected", "note": "typo"}]
                    },
                }
            ]
        ),
        encoding="utf-8",
    )

    with raises(ScinoephileError, match="JSON input must use field aliases"):
        sync_test_cases(
            [source_path],
            tmp_path / "test_cases.sqlite",
            _AliasedBaseReviewManager,
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
    deleted_query = _get_translation_query("c")
    deleted_answer = _get_translation_answer("d")
    first_data = [
        {
            "query": _get_translation_query("a"),
            "answer": _get_translation_answer("b"),
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
        json.dumps(
            [
                {
                    "query": _get_translation_query("a"),
                    "answer": _get_translation_answer("b"),
                }
            ]
        ),
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
            "query": _get_translation_query("a"),
            "answer": _get_translation_answer("b"),
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
    data[0]["few_shot"] = True
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
    assert not loaded.few_shot
    assert not loaded.verified


def test_sync_validates_all_inputs_before_writing(tmp_path: Path):
    """An invalid later source should prevent all database writes."""
    database_path = tmp_path / "test_cases.sqlite"
    valid_path = tmp_path / "valid.json"
    invalid_path = tmp_path / "invalid.json"
    valid_path.write_text(
        json.dumps(
            [
                {
                    "query": _get_translation_query("a"),
                    "answer": _get_translation_answer("b"),
                }
            ]
        ),
        encoding="utf-8",
    )
    invalid_path.write_text(
        json.dumps(
            [
                {
                    "query": _get_translation_query("c"),
                    "answer": _get_translation_answer("d"),
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
    assert all(set(test_case.query) == {"subtitles"} for test_case in loaded)
    assert all(set(test_case.answer) == {"revisions"} for test_case in loaded)
    raw_subtitles = {item["query"]["subtitles"][0]["text"] for item in raw_data}
    loaded_subtitles: set[str] = set()
    for test_case in loaded:
        subtitles = test_case.query["subtitles"]
        assert isinstance(subtitles, list)
        first_subtitle = subtitles[0]
        assert isinstance(first_subtitle, dict)
        text = first_subtitle["text"]
        assert isinstance(text, str)
        loaded_subtitles.add(text)
    assert loaded_subtitles == raw_subtitles


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
