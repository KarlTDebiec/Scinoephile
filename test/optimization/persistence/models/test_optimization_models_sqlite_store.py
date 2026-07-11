#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for SQLite model configuration persistence."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import replace
from pathlib import Path

from pytest import raises

from scinoephile.core import ScinoephileError
from scinoephile.lang.eng.review import ReviewPromptEng
from scinoephile.llms.review import ReviewManager
from scinoephile.optimization.persistence.models import (
    ModelSqliteStore,
    PersistedModel,
)
from scinoephile.optimization.persistence.prompts import (
    PersistedPrompt,
    PromptSqliteStore,
)
from scinoephile.optimization.persistence.test_cases import TestCaseSqliteStore


def test_store_round_trips_and_is_idempotent(tmp_path: Path):
    """Model configurations should round-trip and insert only once.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    store = ModelSqliteStore(database_path)
    model = PersistedModel.from_config(
        "deepseek",
        "deepseek-v4-flash",
        base_url="https://api.deepseek.com",
        settings={"reasoning": {"effort": "high"}},
    )

    assert store.add_model(model)
    assert not store.add_model(model)
    assert store.get_model(model.model_id) == model

    with closing(sqlite3.connect(database_path)) as connection:
        columns = {
            str(row[1]) for row in connection.execute("PRAGMA table_info(models)")
        }
    assert columns == {
        "base_url",
        "model",
        "model_id",
        "provider",
        "settings_json",
    }


def test_store_rejects_invalid_content_addressed_id(tmp_path: Path):
    """Writes should reject a model ID that does not match its configuration.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    store = ModelSqliteStore(database_path)
    model = PersistedModel.from_config("openai", "gpt-5.4-mini")

    with raises(ScinoephileError, match="content-addressed ID"):
        store.add_model(replace(model, model_id="incorrect"))
    assert not database_path.exists()


def test_store_rejects_corrupted_content(tmp_path: Path):
    """Reads should reject rows whose content no longer matches their ID.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    store = ModelSqliteStore(database_path)
    model = PersistedModel.from_config("openai", "gpt-5.4-mini")
    store.add_model(model)
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute(
            "UPDATE models SET base_url = ? WHERE model_id = ?",
            ("https://example.com/v1", model.model_id),
        )
        connection.commit()

    with raises(ScinoephileError, match="content-addressed ID"):
        store.get_model(model.model_id)


def test_store_shares_database_with_other_optimization_stores(tmp_path: Path):
    """Optimization stores should coexist in one SQLite database.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    model_store = ModelSqliteStore(database_path)
    prompt_store = PromptSqliteStore(database_path)
    test_case_store = TestCaseSqliteStore(database_path)
    model = PersistedModel.from_config("openai", "gpt-5.4-mini")
    prompt = PersistedPrompt.from_prompt(ReviewPromptEng, ReviewManager)

    model_store.add_model(model)
    prompt_store.sync_aliases({"review-eng": prompt}, dry_run=False)
    test_case_store.create_schema()

    assert model_store.get_model(model.model_id) == model
    assert prompt_store.get_prompt_by_alias("review-eng") == prompt
    assert test_case_store.get_test_case("missing") is None


def test_store_reads_prompt_only_database_as_empty(tmp_path: Path):
    """The model store should treat an absent peer table as empty.

    Arguments:
        tmp_path: temporary directory
    """
    database_path = tmp_path / "optimization.sqlite"
    PromptSqliteStore(database_path).create_schema()
    store = ModelSqliteStore(database_path)

    assert store.get_model("missing") is None
