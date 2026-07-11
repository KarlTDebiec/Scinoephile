#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for registered prompt synchronization."""

from __future__ import annotations

from pathlib import Path

from scinoephile.optimization.persistence.prompts import PromptSqliteStore
from scinoephile.optimization.persistence.prompts.sync import sync_prompts
from scinoephile.optimization.prompt_specs import PROMPT_SPECS


def test_sync_inserts_registered_prompt_and_becomes_noop(tmp_path: Path):
    """Repeated synchronization should become a no-op.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    prompt_specs = {"review-eng": PROMPT_SPECS["review-eng"]}

    first_report = sync_prompts(prompt_specs, database_path, dry_run=False)
    second_report = sync_prompts(prompt_specs, database_path, dry_run=False)

    assert first_report.prompt_count == 1
    assert first_report.insert_aliases == ("review-eng",)
    assert first_report.update_aliases == ()
    assert second_report.insert_aliases == ()
    assert second_report.update_aliases == ()
    assert PromptSqliteStore(database_path).get_prompt_by_alias("review-eng")


def test_sync_all_registered_prompts(tmp_path: Path):
    """All registered workflow prompt aliases should synchronize.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"

    report = sync_prompts(PROMPT_SPECS, database_path, dry_run=False)
    store = PromptSqliteStore(database_path)

    assert report.prompt_count == len(PROMPT_SPECS)
    assert report.insert_aliases == tuple(sorted(PROMPT_SPECS))
    assert store.get_prompt_by_alias("review-eng")
    assert store.get_prompt_by_alias("translation-yue-hans-to-eng")
