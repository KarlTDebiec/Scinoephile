#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for registered prompt synchronization."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core import Language
from scinoephile.lang.review import DEFAULT_PROMPTS
from scinoephile.llms.review import ReviewManager
from scinoephile.optimization.persistence.prompts import PromptSqliteStore
from scinoephile.optimization.persistence.prompts.sync import sync_prompts
from scinoephile.optimization.prompt_spec import PromptSpec

_PROMPT_SPECS = {
    "review-eng": PromptSpec(
        manager_cls=ReviewManager,
        prompt=DEFAULT_PROMPTS[Language.eng],
    )
}
"""Minimal prompt specifications for persistence unit tests."""


def test_sync_inserts_registered_prompt_and_becomes_noop(tmp_path: Path):
    """Repeated synchronization should become a no-op.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    first_report = sync_prompts(_PROMPT_SPECS, database_path, dry_run=False)
    second_report = sync_prompts(_PROMPT_SPECS, database_path, dry_run=False)

    assert first_report.prompt_count == 1
    assert first_report.insert_aliases == ("review-eng",)
    assert first_report.update_aliases == ()
    assert second_report.insert_aliases == ()
    assert second_report.update_aliases == ()
    assert PromptSqliteStore(database_path).get_prompt_by_alias("review-eng")
