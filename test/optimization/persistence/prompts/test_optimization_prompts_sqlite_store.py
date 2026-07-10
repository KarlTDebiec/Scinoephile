#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for normalized SQLite zero-shot prompt persistence."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import replace
from pathlib import Path

from pydantic import JsonValue
from pytest import raises

from scinoephile.core import Language, ScinoephileError
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

_UPDATED_REVIEW_PROMPT = ReviewPromptEng.with_attributes(
    {"base_system_prompt": "Review subtitles with exceptional care."}
)
"""English review prompt with updated zero-shot instructions."""


def test_store_round_trips_prompts_and_aliases(tmp_path: Path):
    """Prompt content and aliases should round-trip through normalized tables.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    store = PromptSqliteStore(database_path)
    prompt = PersistedPrompt.from_prompt(ReviewPromptEng, ReviewManager)

    changes = store.sync_aliases({"review-eng": prompt}, dry_run=False)
    loaded = store.get_prompt(prompt.prompt_id)

    assert changes == ({prompt.prompt_id}, {"review-eng"}, set())
    assert loaded is not None
    assert loaded.operation == ReviewManager.operation
    assert loaded.language == Language.eng
    assert loaded.attributes == prompt.attributes
    assert loaded.aliases == ("review-eng",)
    assert store.get_prompt_by_alias("review-eng") == loaded

    with closing(sqlite3.connect(database_path)) as connection:
        prompt_columns = {
            str(row[1]) for row in connection.execute("PRAGMA table_info(prompts)")
        }
        alias_columns = {
            str(row[1])
            for row in connection.execute("PRAGMA table_info(prompt_aliases)")
        }
    assert prompt_columns == {
        "attributes_json",
        "language",
        "operation",
        "prompt_id",
    }
    assert alias_columns == {"alias", "prompt_id"}


def test_store_shares_database_with_test_cases(tmp_path: Path):
    """Prompt and test-case tables should coexist in one SQLite database.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    prompt_store = PromptSqliteStore(database_path)
    test_case_store = TestCaseSqliteStore(database_path)
    prompt = PersistedPrompt.from_prompt(ReviewPromptEng, ReviewManager)
    query: dict[str, JsonValue] = {"input_1": "Hello"}
    answer: dict[str, JsonValue] = {"output_1": "Hello"}
    test_case = PersistedTestCase(
        test_case_id=get_test_case_id(query, answer, TranslationManager),
        operation=TranslationManager.operation,
        difficulty=0,
        prompt=False,
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

    assert prompt_store.get_prompt_by_alias("review-eng") is not None
    assert test_case_store.get_test_case(test_case.test_case_id) is not None
    with closing(sqlite3.connect(database_path)) as connection:
        tables = {
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
    assert {"prompts", "prompt_aliases", "test_cases", "test_case_sources"} <= tables


def test_store_deduplicates_content_across_aliases(tmp_path: Path):
    """Multiple aliases should share one identical prompt row.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    store = PromptSqliteStore(database_path)
    prompt = PersistedPrompt.from_prompt(ReviewPromptEng, ReviewManager)

    store.sync_aliases(
        {
            "first": prompt,
            "second": prompt,
        },
        dry_run=False,
    )

    assert len(store.list_prompts()) == 1
    loaded = store.get_prompt(prompt.prompt_id)
    assert loaded is not None
    assert loaded.aliases == ("first", "second")


def test_store_filters_prompts_by_operation(tmp_path: Path):
    """Prompt listing should support an operation filter.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    store = PromptSqliteStore(database_path)
    prompt = PersistedPrompt.from_prompt(ReviewPromptEng, ReviewManager)
    store.sync_aliases({"review-eng": prompt}, dry_run=False)

    assert store.list_prompts(manager_cls=ReviewManager)
    assert store.list_prompts(manager_cls=TranslationManager) == []


def test_store_moves_alias_without_deleting_history(tmp_path: Path):
    """Moving an alias should retain the prior immutable prompt.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    store = PromptSqliteStore(database_path)
    original = PersistedPrompt.from_prompt(ReviewPromptEng, ReviewManager)
    updated = PersistedPrompt.from_prompt(_UPDATED_REVIEW_PROMPT, ReviewManager)
    store.sync_aliases({"review-eng": original}, dry_run=False)

    changes = store.sync_aliases({"review-eng": updated}, dry_run=False)

    assert changes == ({updated.prompt_id}, set(), {"review-eng"})
    loaded_original = store.get_prompt(original.prompt_id)
    loaded_updated = store.get_prompt(updated.prompt_id)
    assert loaded_original is not None
    assert loaded_original.aliases == ()
    assert loaded_updated is not None
    assert loaded_updated.aliases == ("review-eng",)


def test_store_dry_run_does_not_create_database(tmp_path: Path):
    """Dry runs against a missing database should remain read-only.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    store = PromptSqliteStore(database_path)
    prompt = PersistedPrompt.from_prompt(ReviewPromptEng, ReviewManager)

    changes = store.sync_aliases({"review-eng": prompt}, dry_run=True)

    assert changes == ({prompt.prompt_id}, {"review-eng"}, set())
    assert not database_path.exists()


def test_store_rejects_invalid_alias_and_id(tmp_path: Path):
    """Writes should reject invalid aliases and content-addressed IDs.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    store = PromptSqliteStore(database_path)
    prompt = PersistedPrompt.from_prompt(ReviewPromptEng, ReviewManager)

    with raises(ScinoephileError, match="outer whitespace"):
        store.sync_aliases({" review-eng": prompt}, dry_run=False)
    with raises(ScinoephileError, match="content-addressed ID"):
        store.sync_aliases(
            {"review-eng": replace(prompt, prompt_id="incorrect")},
            dry_run=False,
        )
    assert not database_path.exists()


def test_store_rejects_non_string_persisted_attributes(tmp_path: Path):
    """Reads should reject corrupted non-string prompt attributes.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    store = PromptSqliteStore(database_path)
    store.create_schema()
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute(
            "INSERT INTO prompts(prompt_id, operation, language, attributes_json) "
            "VALUES (?, ?, ?, ?)",
            ("corrupted", "review", "eng", '{"base_system_prompt": 1}'),
        )
        connection.commit()

    with raises(ScinoephileError, match="attributes must be strings"):
        store.get_prompt("corrupted")


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
