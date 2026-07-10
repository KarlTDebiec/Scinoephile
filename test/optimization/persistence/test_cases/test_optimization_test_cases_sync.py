#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for JSON to normalized SQLite synchronization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import ClassVar

from pytest import raises

from scinoephile import common
from scinoephile.core import ScinoephileError
from scinoephile.lang.zho.review import ReviewPromptZhoHant
from scinoephile.llms.punctuation import PUNCTUATION_OPERATION_SPEC
from scinoephile.llms.review import (
    REVIEW_OPERATION_SPEC,
    ReviewManager,
    ReviewPrompt,
)
from scinoephile.llms.translation import TRANSLATION_OPERATION_SPEC, TranslationPrompt
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YuePunctuationVsZhoPromptYueHans,
)
from scinoephile.optimization.persistence.test_cases import (
    PersistedTestCase,
    TestCaseSqliteStore,
)
from scinoephile.optimization.persistence.test_cases.id import get_test_case_id
from scinoephile.optimization.persistence.test_cases.sync import (
    sync_test_cases_from_json_paths,
)


class _LocalizedReviewPrompt(ReviewPrompt):
    """Review prompt using localized correspondence field names."""

    input_pfx: ClassVar[str] = "zimu_"
    output_pfx: ClassVar[str] = "xiugai_"
    note_pfx: ClassVar[str] = "beizhu_"


class _AlternativeReviewPrompt(ReviewPrompt):
    """Review prompt using an alternative correspondence schema."""

    input_pfx: ClassVar[str] = "source_"
    output_pfx: ClassVar[str] = "correction_"
    note_pfx: ClassVar[str] = "explanation_"


def test_normalization_makes_prompt_field_aliases_share_identity():
    """Equivalent field aliases should normalize to one SQL identity."""
    localized_cls = ReviewManager.get_test_case_cls(
        size=1,
        prompt_cls=_LocalizedReviewPrompt,
    )
    alternative_cls = ReviewManager.get_test_case_cls(
        size=1,
        prompt_cls=_AlternativeReviewPrompt,
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
    base_cls = ReviewManager.get_test_case_cls(size=1, prompt_cls=ReviewPrompt)

    localized_persisted = PersistedTestCase.from_test_case(
        localized,
        operation_spec=REVIEW_OPERATION_SPEC,
        base_test_case_cls=base_cls,
    )
    alternative_persisted = PersistedTestCase.from_test_case(
        alternative,
        operation_spec=REVIEW_OPERATION_SPEC,
        base_test_case_cls=base_cls,
    )

    assert localized_persisted.query == {"subtitle_1": "original"}
    assert localized_persisted.answer == {
        "revised_1": "corrected",
        "note_1": "typo",
    }
    assert localized_persisted.test_case_id == alternative_persisted.test_case_id


def test_sync_rejects_source_prompt_from_another_operation(tmp_path: Path):
    """Source prompts should belong to the selected operation's base prompt."""
    with raises(ScinoephileError, match="is not a subclass"):
        sync_test_cases_from_json_paths(
            database_path=tmp_path / "test_cases.sqlite",
            operation_spec=TRANSLATION_OPERATION_SPEC,
            source_prompt_cls=ReviewPrompt,
            input_paths=[],
            dry_run=False,
        )


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
            sync_test_cases_from_json_paths(
                database_path=tmp_path / "test_cases.sqlite",
                operation_spec=TRANSLATION_OPERATION_SPEC,
                source_prompt_cls=TranslationPrompt,
                input_paths=[source_path],
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
        operation_spec=TRANSLATION_OPERATION_SPEC,
        source_prompt_cls=TranslationPrompt,
        input_paths=[source_path],
        dry_run=False,
    )
    assert len(first_report.insert_ids) == 2
    deleted_id = get_test_case_id(
        first_data[1]["query"],
        first_data[1]["answer"],
        TRANSLATION_OPERATION_SPEC,
    )

    source_path.write_text(json.dumps(first_data[:1]), encoding="utf-8")
    second_report = sync_test_cases_from_json_paths(
        database_path=database_path,
        operation_spec=TRANSLATION_OPERATION_SPEC,
        source_prompt_cls=TranslationPrompt,
        input_paths=[source_path],
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
    first_report = sync_test_cases_from_json_paths(
        database_path=database_path,
        operation_spec=TRANSLATION_OPERATION_SPEC,
        source_prompt_cls=TranslationPrompt,
        input_paths=[source_path],
        dry_run=False,
    )

    source_path.write_text("[]\n", encoding="utf-8")
    second_report = sync_test_cases_from_json_paths(
        database_path=database_path,
        operation_spec=TRANSLATION_OPERATION_SPEC,
        source_prompt_cls=TranslationPrompt,
        input_paths=[source_path.resolve()],
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
    first_report = sync_test_cases_from_json_paths(
        database_path=database_path,
        operation_spec=TRANSLATION_OPERATION_SPEC,
        source_prompt_cls=TranslationPrompt,
        input_paths=[source_path],
        dry_run=False,
    )

    data[0]["difficulty"] = 2
    data[0]["prompt"] = True
    data[0]["verified"] = True
    source_path.write_text(json.dumps(data), encoding="utf-8")
    dry_run_report = sync_test_cases_from_json_paths(
        database_path=database_path,
        operation_spec=TRANSLATION_OPERATION_SPEC,
        source_prompt_cls=TranslationPrompt,
        input_paths=[source_path],
        dry_run=True,
    )

    assert dry_run_report.insert_ids == ()
    assert dry_run_report.delete_ids == ()
    loaded_before_write = TestCaseSqliteStore(database_path).get_test_case(
        first_report.insert_ids[0]
    )
    assert loaded_before_write is not None
    assert loaded_before_write.difficulty == 1

    sync_test_cases_from_json_paths(
        database_path=database_path,
        operation_spec=TRANSLATION_OPERATION_SPEC,
        source_prompt_cls=TranslationPrompt,
        input_paths=[source_path],
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
        sync_test_cases_from_json_paths(
            database_path=database_path,
            operation_spec=TRANSLATION_OPERATION_SPEC,
            source_prompt_cls=TranslationPrompt,
            input_paths=[valid_path, invalid_path],
            dry_run=False,
        )

    assert not database_path.exists()


def test_sync_normalizes_localized_repository_data(tmp_path: Path):
    """Localized fields should be stored using base prompt English field names."""
    source_path = (
        common.package_root.parent
        / "test/data/kob/output/zho-Hant_ocr/lang/zho/review.json"
    )
    raw_data = json.loads(source_path.read_text(encoding="utf-8"))
    database_path = tmp_path / "test_cases.sqlite"

    sync_test_cases_from_json_paths(
        database_path=database_path,
        operation_spec=REVIEW_OPERATION_SPEC,
        source_prompt_cls=ReviewPromptZhoHant,
        input_paths=[source_path],
        dry_run=False,
    )
    loaded = TestCaseSqliteStore(database_path).get_test_cases_by_source_path(
        str(source_path.resolve()),
        operation_spec=REVIEW_OPERATION_SPEC,
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
    raw_subtitles = {item["query"]["zimu_1"] for item in raw_data}
    assert {test_case.query["subtitle_1"] for test_case in loaded} == raw_subtitles


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
        operation_spec=PUNCTUATION_OPERATION_SPEC,
        source_prompt_cls=YuePunctuationVsZhoPromptYueHans,
        input_paths=[source_path],
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
