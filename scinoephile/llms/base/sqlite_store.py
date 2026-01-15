#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""SQLite persistence for prompts, test cases, models, and results."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from logging import getLogger
from pathlib import Path
from typing import Any

from scinoephile.core import ScinoephileError
from scinoephile.lang.eng.ocr_fusion.prompts import EngOcrFusionPrompt
from scinoephile.lang.eng.proofreading.prompts import EngProofreadingPrompt
from scinoephile.lang.zho.ocr_fusion.prompts import (
    ZhoHansOcrFusionPrompt,
    ZhoHantOcrFusionPrompt,
)
from scinoephile.lang.zho.proofreading.prompts import (
    ZhoHansProofreadingPrompt,
    ZhoHantProofreadingPrompt,
)
from scinoephile.llms.dual_block import DualBlockManager, DualBlockPrompt
from scinoephile.llms.dual_block_gapped import (
    DualBlockGappedManager,
    DualBlockGappedPrompt,
)
from scinoephile.llms.dual_single import DualSinglePrompt
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionManager
from scinoephile.llms.mono_block import MonoBlockManager, MonoBlockPrompt
from scinoephile.multilang.yue_zho.proofreading import YueZhoProofreadingManager
from scinoephile.multilang.yue_zho.proofreading.prompts import (
    YueZhoHansProofreadingPrompt,
    YueZhoHantProofreadingPrompt,
)
from scinoephile.multilang.yue_zho.review.prompts import (
    YueHansReviewPrompt,
    YueHantReviewPrompt,
)
from scinoephile.multilang.yue_zho.translation.prompts import (
    YueHansFromZhoTranslationPrompt,
    YueHantFromZhoTranslationPrompt,
)

from .manager import Manager
from .prompt import Prompt
from .test_case import TestCase

__all__ = [
    "PromptConfig",
    "PromptVersion",
    "SqliteStore",
    "get_default_prompt_configs",
]

LOGGER = getLogger(__name__)

_KIND_DUAL_SINGLE = "dual_single"
_KIND_MONO_BLOCK = "mono_block"
_KIND_DUAL_BLOCK = "dual_block"
_KIND_DUAL_BLOCK_GAPPED = "dual_block_gapped"


@dataclass(frozen=True)
class PromptConfig:
    """Configuration for a prompt and its associated tables."""

    slug: str
    """Prompt slug used in table names."""
    prompt_cls: type[Prompt]
    """Prompt class."""
    manager_cls: type[Manager]
    """Manager class used to construct test cases."""


@dataclass(frozen=True)
class PromptVersion:
    """Prompt version record."""

    prompt_version_id: int
    """Database id for the prompt version."""
    slug: str
    """Prompt slug."""
    content: dict[str, str]
    """Prompt text fields stored for the version."""
    content_hash: str
    """Stable hash of prompt contents."""
    created_at: str
    """Timestamp when the prompt version was stored."""
    version_label: str | None
    """Optional version label."""


def get_default_prompt_configs() -> list[PromptConfig]:
    """Get prompt configurations used by processors.

    Returns:
        list of prompt configurations
    """
    return [
        PromptConfig(
            slug="lang.eng.ocr_fusion",
            prompt_cls=EngOcrFusionPrompt,
            manager_cls=OcrFusionManager,
        ),
        PromptConfig(
            slug="lang.zho.ocr_fusion.hans",
            prompt_cls=ZhoHansOcrFusionPrompt,
            manager_cls=OcrFusionManager,
        ),
        PromptConfig(
            slug="lang.zho.ocr_fusion.hant",
            prompt_cls=ZhoHantOcrFusionPrompt,
            manager_cls=OcrFusionManager,
        ),
        PromptConfig(
            slug="lang.eng.proofreading",
            prompt_cls=EngProofreadingPrompt,
            manager_cls=MonoBlockManager,
        ),
        PromptConfig(
            slug="lang.zho.proofreading.hans",
            prompt_cls=ZhoHansProofreadingPrompt,
            manager_cls=MonoBlockManager,
        ),
        PromptConfig(
            slug="lang.zho.proofreading.hant",
            prompt_cls=ZhoHantProofreadingPrompt,
            manager_cls=MonoBlockManager,
        ),
        PromptConfig(
            slug="multilang.yue_zho.translation.hans",
            prompt_cls=YueHansFromZhoTranslationPrompt,
            manager_cls=DualBlockGappedManager,
        ),
        PromptConfig(
            slug="multilang.yue_zho.translation.hant",
            prompt_cls=YueHantFromZhoTranslationPrompt,
            manager_cls=DualBlockGappedManager,
        ),
        PromptConfig(
            slug="multilang.yue_zho.review.hans",
            prompt_cls=YueHansReviewPrompt,
            manager_cls=DualBlockManager,
        ),
        PromptConfig(
            slug="multilang.yue_zho.review.hant",
            prompt_cls=YueHantReviewPrompt,
            manager_cls=DualBlockManager,
        ),
        PromptConfig(
            slug="multilang.yue_zho.proofreading.hans",
            prompt_cls=YueZhoHansProofreadingPrompt,
            manager_cls=YueZhoProofreadingManager,
        ),
        PromptConfig(
            slug="multilang.yue_zho.proofreading.hant",
            prompt_cls=YueZhoHantProofreadingPrompt,
            manager_cls=YueZhoProofreadingManager,
        ),
    ]


class SqliteStore:
    """SQLite-backed persistence for prompt optimization tracking."""

    def __init__(
        self,
        db_path: Path | str,
        *,
        prompt_configs: list[PromptConfig] | None = None,
        max_block_size: int = 100,
    ):
        """Initialize.

        Arguments:
            db_path: path to SQLite database file
            prompt_configs: prompt configurations to create tables for
            max_block_size: maximum block size for variable-size prompts
        """
        self.db_path = Path(db_path)
        self._connection = sqlite3.connect(self.db_path)
        self._connection.row_factory = sqlite3.Row
        self._configure_connection()

        self.max_block_size = max_block_size
        self.prompt_configs = prompt_configs or get_default_prompt_configs()
        self._prompt_config_by_cls = {
            config.prompt_cls: config for config in self.prompt_configs
        }
        self._prompt_config_by_slug = {
            config.slug: config for config in self.prompt_configs
        }

    def __enter__(self) -> SqliteStore:
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc, traceback):
        """Exit context manager."""
        self.close()

    def close(self):
        """Close the database connection."""
        self._connection.close()

    def initialize_schema(self):
        """Create tables if they do not exist."""
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS llm_models (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                provider TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY,
                prompt_slug TEXT NOT NULL,
                test_case_id INTEGER NOT NULL,
                prompt_version_id INTEGER NOT NULL,
                model_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_test_results_case_id ON test_results(test_case_id)"  # noqa: E501
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_test_results_prompt_slug ON test_results(prompt_slug)"  # noqa: E501
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_test_results_model_id ON test_results(model_id)"  # noqa: E501
        )
        for config in self.prompt_configs:
            self._create_prompt_table(config)
            self._create_test_case_table(config)
        self._connection.commit()

    def get_or_create_prompt_version(
        self,
        prompt_cls: type[Prompt],
        *,
        version_label: str | None = None,
    ) -> PromptVersion:
        """Get or insert a prompt version for the provided prompt class.

        Arguments:
            prompt_cls: prompt class
            version_label: optional label for version
        Returns:
            prompt version record
        """
        config = self._get_prompt_config(prompt_cls)
        table_name = self._prompt_table_name(config.slug)
        fields = _collect_prompt_text_fields(prompt_cls)
        field_names = sorted(fields.keys())
        content_hash = _hash_prompt_content(fields, field_names)
        now = _utc_now_iso()

        row = self._connection.execute(
            f"""
            SELECT id, created_at, version_label
            FROM {table_name}
            WHERE content_hash = ?
            """,
            (content_hash,),
        ).fetchone()
        if row:
            return PromptVersion(
                prompt_version_id=int(row["id"]),
                slug=config.slug,
                content=fields,
                content_hash=content_hash,
                created_at=str(row["created_at"]),
                version_label=row["version_label"],
            )

        columns = ["created_at", "content_hash", "version_label", *field_names]
        placeholders = ", ".join(["?"] * len(columns))
        values = [now, content_hash, version_label]
        values.extend(fields[name] for name in field_names)
        column_list = ", ".join(_quote_ident(col) for col in columns)
        cursor = self._connection.execute(
            f"""
            INSERT INTO {table_name} ({column_list})
            VALUES ({placeholders})
            """,
            values,
        )
        self._connection.commit()
        return PromptVersion(
            prompt_version_id=int(cursor.lastrowid),
            slug=config.slug,
            content=fields,
            content_hash=content_hash,
            created_at=now,
            version_label=version_label,
        )

    def load_prompt_version(
        self,
        prompt_cls: type[Prompt],
        prompt_version_id: int,
    ) -> PromptVersion:
        """Load a prompt version by id.

        Arguments:
            prompt_cls: prompt class
            prompt_version_id: prompt version id to load
        Returns:
            prompt version record
        Raises:
            ScinoephileError: if the prompt version does not exist
        """
        config = self._get_prompt_config(prompt_cls)
        table_name = self._prompt_table_name(config.slug)
        row = self._connection.execute(
            f"""
            SELECT *
            FROM {table_name}
            WHERE id = ?
            """,
            (prompt_version_id,),
        ).fetchone()
        if not row:
            raise ScinoephileError(
                f"Prompt version id {prompt_version_id} does not exist."
            )
        fields = {
            key: row[key]
            for key in row.keys()
            if key
            not in {
                "id",
                "created_at",
                "content_hash",
                "version_label",
            }
        }
        return PromptVersion(
            prompt_version_id=int(row["id"]),
            slug=config.slug,
            content=fields,
            content_hash=str(row["content_hash"]),
            created_at=str(row["created_at"]),
            version_label=row["version_label"],
        )

    def get_or_create_model(
        self,
        name: str,
        *,
        provider: str | None = None,
    ) -> int:
        """Get or insert an LLM model record.

        Arguments:
            name: model name
            provider: provider name
        Returns:
            model id
        """
        row = self._connection.execute(
            "SELECT id FROM llm_models WHERE name = ?",
            (name,),
        ).fetchone()
        if row:
            return int(row["id"])

        now = _utc_now_iso()
        cursor = self._connection.execute(
            """
            INSERT INTO llm_models (name, provider, created_at)
            VALUES (?, ?, ?)
            """,
            (name, provider, now),
        )
        self._connection.commit()
        return int(cursor.lastrowid)

    def upsert_test_case(
        self,
        test_case: TestCase,
        manager_cls: type[Manager] | None = None,
    ) -> int:
        """Insert or update a test case row.

        Arguments:
            test_case: test case to persist
            manager_cls: manager class used to construct the test case
        Returns:
            test case id
        """
        prompt_cls = type(test_case).prompt_cls
        config = self._get_prompt_config(prompt_cls)
        table_name = self._test_case_table_name(config.slug)
        kind = _get_prompt_kind(prompt_cls)
        query_data = test_case.query.model_dump()
        answer_data = (
            test_case.answer.model_dump() if test_case.answer is not None else {}
        )
        size = _get_test_case_size(test_case, kind)
        query_fields, answer_fields = _get_prompt_fields(
            prompt_cls, kind, size or self.max_block_size
        )

        column_values: dict[str, Any] = {
            "query_key": test_case.query.key_str,
            "size": size,
            "difficulty": test_case.difficulty,
            "prompt": int(test_case.prompt),
            "verified": int(test_case.verified),
            "created_at": _utc_now_iso(),
        }
        for field in query_fields:
            column_values[f"query_{field}"] = query_data.get(field)
        for field in answer_fields:
            column_values[f"answer_{field}"] = answer_data.get(field)

        columns = list(column_values.keys())
        placeholders = ", ".join(["?"] * len(columns))
        column_list = ", ".join(_quote_ident(col) for col in columns)
        update_columns = [col for col in columns if col != "query_key"]
        update_clause = ", ".join(
            f"{_quote_ident(col)} = excluded.{_quote_ident(col)}"
            for col in update_columns
        )
        cursor = self._connection.execute(
            f"""
            INSERT INTO {table_name} ({column_list})
            VALUES ({placeholders})
            ON CONFLICT (query_key) DO UPDATE SET
                {update_clause}
            """,
            [column_values[col] for col in columns],
        )
        self._connection.commit()
        test_case_id = cursor.lastrowid
        if test_case_id:
            return int(test_case_id)

        row = self._connection.execute(
            f"""
            SELECT id
            FROM {table_name}
            WHERE query_key = ?
            """,
            (test_case.query.key_str,),
        ).fetchone()
        if not row:
            raise ScinoephileError("Failed to upsert test case.")
        return int(row["id"])

    def load_test_cases(self, prompt_cls: type[Prompt]) -> list[TestCase]:
        """Load all test cases for a prompt.

        Arguments:
            prompt_cls: prompt class to use for reconstruction
        Returns:
            list of test cases
        """
        config = self._get_prompt_config(prompt_cls)
        table_name = self._test_case_table_name(config.slug)
        kind = _get_prompt_kind(prompt_cls)
        rows = self._connection.execute(
            f"""
            SELECT *
            FROM {table_name}
            ORDER BY id
            """
        ).fetchall()
        test_cases: list[TestCase] = []
        for row in rows:
            size = row["size"]
            query_fields, answer_fields = _get_prompt_fields(
                prompt_cls, kind, size or self.max_block_size
            )
            query_data: dict[str, Any] = {}
            answer_data: dict[str, Any] = {}
            for field in query_fields:
                value = row[f"query_{field}"]
                if value is not None:
                    query_data[field] = value
            for field in answer_fields:
                value = row[f"answer_{field}"]
                if value is not None:
                    answer_data[field] = value

            test_case_cls = _get_test_case_cls(
                config.manager_cls,
                prompt_cls,
                kind,
                size,
                query_data,
            )
            payload: dict[str, Any] = {
                "query": query_data,
                "difficulty": int(row["difficulty"]),
                "prompt": bool(row["prompt"]),
                "verified": bool(row["verified"]),
            }
            if answer_data:
                payload["answer"] = answer_data
            test_cases.append(test_case_cls.model_validate(payload))
        return test_cases

    def insert_test_result(
        self,
        *,
        prompt_cls: type[Prompt],
        test_case_id: int,
        prompt_version_id: int,
        model_id: int,
        status: str,
    ) -> int:
        """Insert a test result row.

        Arguments:
            prompt_cls: prompt class used for the run
            test_case_id: test case id
            prompt_version_id: prompt version id used in the run
            model_id: model id used in the run
            status: outcome status (e.g., success, error)
        Returns:
            test result id
        """
        config = self._get_prompt_config(prompt_cls)
        now = _utc_now_iso()
        cursor = self._connection.execute(
            """
            INSERT INTO test_results (
                prompt_slug,
                test_case_id,
                prompt_version_id,
                model_id,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                config.slug,
                test_case_id,
                prompt_version_id,
                model_id,
                status,
                now,
            ),
        )
        self._connection.commit()
        return int(cursor.lastrowid)

    def _create_prompt_table(self, config: PromptConfig):
        """Create a prompt table for a prompt configuration.

        Arguments:
            config: prompt configuration
        """
        fields = _collect_prompt_text_fields(config.prompt_cls)
        if not fields:
            raise ScinoephileError(
                f"No prompt fields found for {config.prompt_cls.__name__}."
            )
        columns = [
            "id INTEGER PRIMARY KEY",
            "created_at TEXT NOT NULL",
            "content_hash TEXT NOT NULL",
            "version_label TEXT",
        ]
        columns.extend(
            f"{_quote_ident(name)} TEXT NOT NULL" for name in sorted(fields.keys())
        )
        table_name = self._prompt_table_name(config.slug)
        column_list = ",\n                ".join(columns)
        self._connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {column_list}
            )
            """
        )
        self._connection.execute(
            f"""
            CREATE UNIQUE INDEX IF NOT EXISTS
                {self._index_name(f"prompt_{config.slug}_content_hash")}
            ON {table_name} (content_hash)
            """
        )

    def _create_test_case_table(self, config: PromptConfig):
        """Create a test case table for a prompt configuration.

        Arguments:
            config: prompt configuration
        """
        kind = _get_prompt_kind(config.prompt_cls)
        query_fields, answer_fields = _get_prompt_fields(
            config.prompt_cls, kind, self.max_block_size
        )
        columns = [
            "id INTEGER PRIMARY KEY",
            "query_key TEXT NOT NULL",
            "size INTEGER",
            "difficulty INTEGER NOT NULL",
            "prompt INTEGER NOT NULL",
            "verified INTEGER NOT NULL",
            "created_at TEXT NOT NULL",
        ]
        columns.extend(
            f"{_quote_ident(f'query_{field}')} TEXT" for field in query_fields
        )
        columns.extend(
            f"{_quote_ident(f'answer_{field}')} TEXT" for field in answer_fields
        )
        table_name = self._test_case_table_name(config.slug)
        column_list = ",\n                ".join(columns)
        self._connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {column_list},
                UNIQUE (query_key)
            )
            """
        )
        self._connection.execute(
            f"""
            CREATE INDEX IF NOT EXISTS
                {self._index_name(f"test_case_{config.slug}_query_key")}
            ON {table_name} (query_key)
            """
        )

    def _configure_connection(self):
        """Configure SQLite connection settings."""
        self._connection.execute("PRAGMA foreign_keys = ON")

    def _get_prompt_config(self, prompt_cls: type[Prompt]) -> PromptConfig:
        """Get prompt config for a prompt class.

        Arguments:
            prompt_cls: prompt class
        Returns:
            prompt configuration
        Raises:
            ScinoephileError: if prompt is not registered
        """
        config = self._prompt_config_by_cls.get(prompt_cls)
        if config is None:
            raise ScinoephileError(
                f"Prompt class {prompt_cls.__name__} is not registered."
            )
        return config

    @staticmethod
    def _prompt_table_name(slug: str) -> str:
        """Return quoted prompt table name."""
        return _quote_ident(f"prompt.{slug}")

    @staticmethod
    def _test_case_table_name(slug: str) -> str:
        """Return quoted test case table name."""
        return _quote_ident(f"test_case.{slug}")

    @staticmethod
    def _index_name(base_name: str) -> str:
        """Return a safe quoted index name."""
        return _quote_ident(base_name.replace(".", "_"))


def _collect_prompt_text_fields(prompt_cls: type[Prompt]) -> dict[str, str]:
    """Collect all text fields defined on the prompt class and its bases.

    Arguments:
        prompt_cls: prompt class to inspect
    Returns:
        mapping of prompt field names to text values
    """
    fields: dict[str, str] = {}
    for cls in prompt_cls.mro():
        if not issubclass(cls, Prompt):
            continue
        for name, value in cls.__dict__.items():
            if name.startswith("_"):
                continue
            if isinstance(value, str):
                fields.setdefault(name, value)
    if not fields:
        LOGGER.warning("No text fields found for prompt %s.", prompt_cls.__name__)
    return fields


def _get_prompt_kind(prompt_cls: type[Prompt]) -> str:
    """Determine prompt kind based on base classes.

    Arguments:
        prompt_cls: prompt class
    Returns:
        prompt kind string
    """
    if issubclass(prompt_cls, DualBlockGappedPrompt):
        return _KIND_DUAL_BLOCK_GAPPED
    if issubclass(prompt_cls, DualBlockPrompt):
        return _KIND_DUAL_BLOCK
    if issubclass(prompt_cls, MonoBlockPrompt):
        return _KIND_MONO_BLOCK
    if issubclass(prompt_cls, DualSinglePrompt):
        return _KIND_DUAL_SINGLE
    raise ScinoephileError(f"Unknown prompt kind for {prompt_cls.__name__}.")


def _get_prompt_fields(
    prompt_cls: type[Prompt],
    kind: str,
    size: int,
) -> tuple[list[str], list[str]]:
    """Get query and answer field names for prompt kind and size.

    Arguments:
        prompt_cls: prompt class
        kind: prompt kind
        size: block size for variable-size prompts
    Returns:
        query field names, answer field names
    """
    if kind == _KIND_DUAL_SINGLE:
        query_fields = [prompt_cls.src_1, prompt_cls.src_2]
        answer_fields = [prompt_cls.output, prompt_cls.note]
        return query_fields, answer_fields

    if kind == _KIND_MONO_BLOCK:
        query_fields = [prompt_cls.input(idx) for idx in range(1, size + 1)]
        answer_fields = [
            field
            for idx in range(1, size + 1)
            for field in (prompt_cls.output(idx), prompt_cls.note(idx))
        ]
        return query_fields, answer_fields

    if kind == _KIND_DUAL_BLOCK:
        query_fields = [
            field
            for idx in range(1, size + 1)
            for field in (prompt_cls.src_1(idx), prompt_cls.src_2(idx))
        ]
        answer_fields = [
            field
            for idx in range(1, size + 1)
            for field in (prompt_cls.output(idx), prompt_cls.note(idx))
        ]
        return query_fields, answer_fields

    if kind == _KIND_DUAL_BLOCK_GAPPED:
        query_fields = [
            field
            for idx in range(1, size + 1)
            for field in (prompt_cls.src_1(idx), prompt_cls.src_2(idx))
        ]
        answer_fields = [prompt_cls.src_1(idx) for idx in range(1, size + 1)]
        return query_fields, answer_fields

    raise ScinoephileError(f"Unknown prompt kind: {kind}")


def _get_test_case_cls(
    manager_cls: type[Manager],
    prompt_cls: type[Prompt],
    kind: str,
    size: int | None,
    query_data: dict[str, Any],
) -> type[TestCase]:
    """Get test case class for provided data.

    Arguments:
        manager_cls: manager class used to construct test case models
        prompt_cls: prompt class
        kind: prompt kind
        size: block size, if applicable
        query_data: query data for determining gaps
    Returns:
        test case class
    """
    if kind == _KIND_DUAL_SINGLE:
        return manager_cls.get_test_case_cls(prompt_cls=prompt_cls)
    if size is None:
        raise ScinoephileError("Size is required for block-based test cases.")
    if kind == _KIND_MONO_BLOCK:
        return manager_cls.get_test_case_cls(size=size, prompt_cls=prompt_cls)
    if kind == _KIND_DUAL_BLOCK:
        return manager_cls.get_test_case_cls(size=size, prompt_cls=prompt_cls)
    if kind == _KIND_DUAL_BLOCK_GAPPED:
        gaps = _get_gaps(prompt_cls, size, query_data)
        return manager_cls.get_test_case_cls(
            size=size, gaps=gaps, prompt_cls=prompt_cls
        )
    raise ScinoephileError(f"Unknown prompt kind: {kind}")


def _get_gaps(
    prompt_cls: type[Prompt],
    size: int,
    query_data: dict[str, Any],
) -> tuple[int, ...]:
    """Determine gaps based on missing source-one fields.

    Arguments:
        prompt_cls: prompt class
        size: block size
        query_data: query data
    Returns:
        tuple of gap indices
    """
    gaps = []
    for idx in range(1, size + 1):
        key = prompt_cls.src_1(idx)
        if key not in query_data:
            gaps.append(idx - 1)
    return tuple(gaps)


def _get_test_case_size(test_case: TestCase, kind: str) -> int | None:
    """Get size for block-based test cases.

    Arguments:
        test_case: test case
        kind: prompt kind
    Returns:
        size, if applicable
    """
    if kind == _KIND_DUAL_SINGLE:
        return None
    size = getattr(test_case, "size", None)
    if size is None:
        raise ScinoephileError("Block-based test case missing size.")
    return int(size)


def _hash_prompt_content(fields: dict[str, str], field_names: list[str]) -> str:
    """Compute a stable hash of prompt contents.

    Arguments:
        fields: prompt field values
        field_names: ordered prompt field names
    Returns:
        hex-encoded hash string
    """
    joined = "\n".join(f"{name}\0{fields[name]}" for name in field_names)
    return sha256(joined.encode("utf-8")).hexdigest()


def _quote_ident(name: str) -> str:
    """Quote a SQLite identifier.

    Arguments:
        name: identifier to quote
    Returns:
        quoted identifier
    """
    escaped = name.replace('"', '""')
    return f'"{escaped}"'


def _utc_now_iso() -> str:
    """Get current UTC time in ISO format.

    Returns:
        ISO timestamp string
    """
    return datetime.now(UTC).isoformat()
