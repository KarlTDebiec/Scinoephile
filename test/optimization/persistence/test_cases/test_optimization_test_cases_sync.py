#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for JSON → SQLite sync helpers."""

from __future__ import annotations

import json
from pathlib import Path

from scinoephile.core.llms import OperationSpec
from scinoephile.llms.mono_block.manager import MonoBlockManager
from scinoephile.llms.mono_block.prompt import MonoBlockPrompt
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YueVsZhoYueHansPunctuationPrompt,
    YueZhoPunctuationManager,
)
from scinoephile.optimization.persistence.test_cases import TestCaseSqliteStore
from scinoephile.optimization.persistence.test_cases.sync import (
    sync_test_cases_from_json_paths,
)


def test_sync_inserts_and_deletes_by_source_path(tmp_path: Path, monkeypatch):
    """Sync should insert new IDs and delete obsolete IDs per source JSON."""
    monkeypatch.chdir(tmp_path)

    db_path = Path("test_cases.sqlite")
    operation_spec = OperationSpec(
        operation="unit-mono-block",
        test_case_table_name="test_cases__unit__mono_block",
        manager_cls=MonoBlockManager,
        prompt_cls=MonoBlockPrompt,
    )

    src1 = Path("src1.json")
    data1_v1 = [
        {
            "query": {"input_1": "a"},
            "answer": {"output_1": "b", "note_1": "changed"},
            "verified": True,
        },
        {
            "query": {"input_1": "c"},
            "answer": {"output_1": "d", "note_1": "changed"},
            "verified": False,
        },
    ]
    src1.write_text(
        json.dumps(data1_v1, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    report1 = sync_test_cases_from_json_paths(
        database_path=db_path,
        operation_spec=operation_spec,
        input_paths=[src1],
        dry_run=False,
    )
    assert len(report1.insert_ids) == 2
    assert report1.delete_ids == ()

    # Now remove one test case from src1; sync should delete that ID for this source.
    data1_v2 = [
        {
            "query": {"input_1": "a"},
            "answer": {"output_1": "b", "note_1": "changed"},
            "verified": True,
        }
    ]
    src1.write_text(
        json.dumps(data1_v2, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    report2 = sync_test_cases_from_json_paths(
        database_path=db_path,
        operation_spec=operation_spec,
        input_paths=[src1],
        dry_run=False,
    )
    assert report2.delete_ids != ()


def test_sync_canonicalizes_source_paths(tmp_path: Path, monkeypatch):
    """Sync should treat relative and absolute paths as the same source."""
    monkeypatch.chdir(tmp_path)

    db_path = Path("test_cases.sqlite")
    operation_spec = OperationSpec(
        operation="unit-mono-block",
        test_case_table_name="test_cases__unit__mono_block",
        manager_cls=MonoBlockManager,
        prompt_cls=MonoBlockPrompt,
    )

    src1 = Path("src1.json")
    data1_v1 = [
        {
            "query": {"input_1": "a"},
            "answer": {"output_1": "b", "note_1": "changed"},
            "verified": True,
        }
    ]
    src1.write_text(
        json.dumps(data1_v1, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report1 = sync_test_cases_from_json_paths(
        database_path=db_path,
        operation_spec=operation_spec,
        input_paths=[src1],
        dry_run=False,
    )
    assert len(report1.insert_ids) == 1

    src1.write_text("[]\n", encoding="utf-8")
    report2 = sync_test_cases_from_json_paths(
        database_path=db_path,
        operation_spec=operation_spec,
        input_paths=[src1.resolve()],
        dry_run=False,
    )
    assert report2.delete_ids == report1.insert_ids


def test_sync_dry_run_reports_metadata_updates(tmp_path: Path, monkeypatch):
    """Dry-run sync should report metadata-only updates."""
    monkeypatch.chdir(tmp_path)

    db_path = Path("test_cases.sqlite")
    operation_spec = OperationSpec(
        operation="unit-mono-block",
        test_case_table_name="test_cases__unit__mono_block",
        manager_cls=MonoBlockManager,
        prompt_cls=MonoBlockPrompt,
    )

    src1 = Path("src1.json")
    data1_v1 = [
        {
            "query": {"input_1": "a"},
            "answer": {"output_1": "b", "note_1": "changed"},
            "difficulty": 1,
            "prompt": False,
            "verified": False,
        }
    ]
    src1.write_text(
        json.dumps(data1_v1, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report1 = sync_test_cases_from_json_paths(
        database_path=db_path,
        operation_spec=operation_spec,
        input_paths=[src1],
        dry_run=False,
    )
    assert len(report1.insert_ids) == 1

    data1_v2 = [
        {
            "query": {"input_1": "a"},
            "answer": {"output_1": "b", "note_1": "changed"},
            "difficulty": 2,
            "prompt": True,
            "verified": True,
        }
    ]
    src1.write_text(
        json.dumps(data1_v2, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    dry_run_report = sync_test_cases_from_json_paths(
        database_path=db_path,
        operation_spec=operation_spec,
        input_paths=[src1],
        dry_run=True,
    )
    assert dry_run_report.insert_ids == ()
    assert dry_run_report.update_ids == report1.insert_ids
    assert dry_run_report.delete_ids == ()

    sync_test_cases_from_json_paths(
        database_path=db_path,
        operation_spec=operation_spec,
        input_paths=[src1],
        dry_run=False,
    )
    store = TestCaseSqliteStore(db_path)
    loaded = store.get_test_case(
        operation_spec.test_case_table_name, report1.insert_ids[0]
    )
    assert loaded is not None
    assert loaded.difficulty == 2
    assert loaded.prompt
    assert loaded.verified


def test_sync_uses_operation_list_fields(tmp_path: Path, monkeypatch):
    """Sync should split list fields configured on the operation spec."""
    monkeypatch.chdir(tmp_path)

    db_path = Path("test_cases.sqlite")
    operation_spec = OperationSpec(
        operation="unit-punctuation",
        test_case_table_name="test_cases__unit__punctuation",
        manager_cls=YueZhoPunctuationManager,
        prompt_cls=YueVsZhoYueHansPunctuationPrompt,
        list_fields={"query.yuewen_to_punctuate": 10},
    )

    src1 = Path("src1.json")
    data = [
        {
            "query": {
                "yuewen_to_punctuate": ["噉我哋", "而家开始"],
                "zhongwen": "那我们现在开始。",
            },
            "answer": {"yuewen_punctuated": "噉我哋，而家开始。"},
            "verified": True,
        }
    ]
    src1.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    report = sync_test_cases_from_json_paths(
        database_path=db_path,
        operation_spec=operation_spec,
        input_paths=[src1],
        dry_run=False,
    )
    store = TestCaseSqliteStore(db_path, operation_spec=operation_spec)
    loaded = store.get_test_case(
        operation_spec.test_case_table_name,
        report.insert_ids[0],
    )

    assert loaded is not None
    assert loaded.query["yuewen_to_punctuate"] == ["噉我哋", "而家开始"]
