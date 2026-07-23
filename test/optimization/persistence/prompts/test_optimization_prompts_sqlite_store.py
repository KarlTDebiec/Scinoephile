#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for SQLite prompt persistence."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from pydantic import JsonValue
from pytest import raises

from scinoephile.core import ScinoephileError
from scinoephile.lang.eng.review import ReviewPromptEng
from scinoephile.llms.review import ReviewManager
from scinoephile.llms.translation import TranslationManager
from scinoephile.optimization.persistence.prompts import (
    PersistedPrompt,
    PromptSqliteStore,
)
from scinoephile.optimization.persistence.test_cases import (
    PersistedTestCase,
    TestCaseSqliteStore,
)
from scinoephile.optimization.persistence.test_cases.id import get_test_case_id

_UPDATED_REVIEW_PROMPT = replace(
    ReviewPromptEng,
    base_system_prompt="Review subtitles with exceptional care.",
)
"""English review prompt with updated instructions."""


def test_store_round_trips_and_updates_alias(tmp_path: Path):
    """An alias should resolve to its current persisted prompt.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    store = PromptSqliteStore(database_path)
    original = PersistedPrompt.from_prompt(ReviewPromptEng, ReviewManager)
    updated = PersistedPrompt.from_prompt(_UPDATED_REVIEW_PROMPT, ReviewManager)

    first_changes = store.sync_aliases({"review-eng": original}, dry_run=False)
    second_changes = store.sync_aliases({"review-eng": updated}, dry_run=False)

    assert first_changes == ({"review-eng"}, set())
    assert second_changes == (set(), {"review-eng"})
    assert store.get_prompt_by_alias("review-eng") == updated


def test_store_shares_database_with_test_cases(tmp_path: Path):
    """Prompt and test-case stores should coexist in one SQLite database.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    prompt_store = PromptSqliteStore(database_path)
    test_case_store = TestCaseSqliteStore(database_path)
    prompt = PersistedPrompt.from_prompt(ReviewPromptEng, ReviewManager)
    query: dict[str, JsonValue] = {"subtitles": [{"index": 1, "text": "Hello"}]}
    answer: dict[str, JsonValue] = {"outputs": [{"index": 1, "text": "Hello"}]}
    test_case = PersistedTestCase(
        test_case_id=get_test_case_id(query, answer, TranslationManager),
        operation=TranslationManager.operation,
        difficulty=0,
        few_shot=False,
        verified=True,
        query=query,
        answer=answer,
        source_paths=(),
    )

    prompt_store.sync_aliases({"review-eng": prompt}, dry_run=False)
    test_case_store.sync_source_paths(
        {"cases.json": [test_case]},
        manager_cls=TranslationManager,
        dry_run=False,
    )

    assert prompt_store.get_prompt_by_alias("review-eng") == prompt
    assert test_case_store.get_test_case(test_case.test_case_id) is not None


def test_store_dry_run_does_not_create_database(tmp_path: Path):
    """Dry runs against a missing database should remain read-only.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    store = PromptSqliteStore(database_path)
    prompt = PersistedPrompt.from_prompt(ReviewPromptEng, ReviewManager)

    changes = store.sync_aliases({"review-eng": prompt}, dry_run=True)

    assert changes == ({"review-eng"}, set())
    assert not database_path.exists()


def test_store_rejects_invalid_content_addressed_id(tmp_path: Path):
    """Writes should reject a prompt ID that does not match its content.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    store = PromptSqliteStore(database_path)
    prompt = PersistedPrompt.from_prompt(ReviewPromptEng, ReviewManager)

    with raises(ScinoephileError, match="content-addressed ID"):
        store.sync_aliases(
            {"review-eng": replace(prompt, prompt_id="incorrect")},
            dry_run=False,
        )
    assert not database_path.exists()


def test_test_case_store_reads_prompt_only_database_as_empty(tmp_path: Path):
    """Component stores should treat absent peer tables as empty.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    PromptSqliteStore(database_path).create_schema()
    store = TestCaseSqliteStore(database_path)

    assert store.get_test_case("missing") is None
    assert store.get_test_cases_by_source_path("missing.json") == []
