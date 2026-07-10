#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for registered zero-shot prompt synchronization."""

from __future__ import annotations

from pathlib import Path

from pytest import raises

from scinoephile.core import ScinoephileError
from scinoephile.optimization.persistence.prompts import PromptSqliteStore
from scinoephile.optimization.persistence.prompts.sync import sync_prompts
from scinoephile.optimization.prompt_specs import PROMPT_SPECS


def test_sync_inserts_registered_prompt_and_becomes_noop(tmp_path: Path):
    """Repeated synchronization should become a no-op.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    prompt_spec = PROMPT_SPECS["review-eng"]

    first_report = sync_prompts([prompt_spec], database_path, dry_run=False)
    second_report = sync_prompts([prompt_spec], database_path, dry_run=False)

    assert first_report.aliases == ("review-eng",)
    assert len(first_report.insert_ids) == 1
    assert first_report.insert_aliases == ("review-eng",)
    assert first_report.update_aliases == ()
    assert second_report.insert_ids == ()
    assert second_report.insert_aliases == ()
    assert second_report.update_aliases == ()
    assert PromptSqliteStore(database_path).get_prompt_by_alias("review-eng")


def test_sync_rejects_duplicate_alias(tmp_path: Path):
    """One synchronization run should reject a repeated alias.

    Arguments:
        tmp_path: temporary directory
    """
    prompt_spec = PROMPT_SPECS["review-eng"]

    with raises(ScinoephileError, match="provided more than once"):
        sync_prompts(
            [prompt_spec, prompt_spec],
            tmp_path / "optimization.sqlite",
            dry_run=False,
        )


def test_sync_all_registered_prompts_deduplicates_content(tmp_path: Path):
    """All workflow aliases should collapse identical prompt definitions.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"

    report = sync_prompts(
        PROMPT_SPECS.values(),
        database_path,
        dry_run=False,
    )

    assert report.aliases == tuple(PROMPT_SPECS)
    assert len(report.insert_ids) < len(report.aliases)
    assert len(PromptSqliteStore(database_path).list_prompts()) == len(
        report.insert_ids
    )
