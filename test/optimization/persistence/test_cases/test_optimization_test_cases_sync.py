#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for JSON → SQLite sync helpers."""

from __future__ import annotations

import json
from pathlib import Path

from scinoephile.llms.mono_block.manager import MonoBlockManager
from scinoephile.llms.mono_block.prompt import MonoBlockPrompt
from scinoephile.optimization.persistence.test_cases.sync import (
    sync_test_cases_from_json_paths,
)


def test_sync_inserts_and_deletes_by_source_path(tmp_path: Path, monkeypatch):
    """Sync should insert new IDs and delete obsolete IDs per source JSON."""
    monkeypatch.chdir(tmp_path)

    db_path = Path("test_cases.sqlite")
    table_name = "test_cases__unit__mono_block"

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
        table_name=table_name,
        input_paths=[src1],
        manager_cls=MonoBlockManager,
        prompt_cls=MonoBlockPrompt,
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
        table_name=table_name,
        input_paths=[src1],
        manager_cls=MonoBlockManager,
        prompt_cls=MonoBlockPrompt,
        dry_run=False,
    )
    assert report2.delete_ids != ()
