#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Normalized SQLite persistence for zero-shot LLM prompts."""

from __future__ import annotations

from collections.abc import Mapping
from logging import getLogger
from typing import cast

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Table,
    Text,
    inspect,
    select,
)
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Connection, RowMapping

from scinoephile.core import Language
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.llms import Manager
from scinoephile.optimization.persistence.sqlite import (
    OptimizationSqliteStore,
    load_json_object,
    metadata,
    serialize_json_object,
)

from .id import get_prompt_id
from .persisted_prompt import PersistedPrompt

__all__ = ["PromptSqliteStore"]

logger = getLogger(__name__)


class PromptSqliteStore(OptimizationSqliteStore):
    """Normalized SQLite persistence and lookup for zero-shot prompts."""

    _prompts = Table(
        "prompts",
        metadata,
        Column("prompt_id", Text, primary_key=True),
        Column("operation", Text, nullable=False),
        Column("language", Text, nullable=False),
        Column("attributes_json", Text, nullable=False),
        CheckConstraint(
            "json_valid(attributes_json)",
            name="prompts_attributes_json_valid",
        ),
        CheckConstraint(
            "json_type(attributes_json) = 'object'",
            name="prompts_attributes_json_object",
        ),
        Index("prompts_operation", "operation"),
    )
    """Content-addressed zero-shot prompts."""

    _prompt_aliases = Table(
        "prompt_aliases",
        metadata,
        Column("alias", Text, primary_key=True),
        Column(
            "prompt_id",
            Text,
            ForeignKey("prompts.prompt_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        Index("prompt_aliases_prompt_id", "prompt_id"),
    )
    """Stable aliases pointing to current zero-shot prompts."""

    def get_prompt(self, prompt_id: str) -> PersistedPrompt | None:
        """Fetch a single prompt by ID.

        Arguments:
            prompt_id: prompt identifier
        Returns:
            persisted prompt, if present
        """
        if not self.database_path.exists():
            return None
        with self.engine.connect() as connection:
            version = self._get_schema_version(connection)
            if version == 0:
                return None
            self._require_current_schema(version)
            if not inspect(connection).has_table("prompts"):
                return None
            row = (
                connection.execute(
                    select(self._prompts).where(self._prompts.c.prompt_id == prompt_id)
                )
                .mappings()
                .first()
            )
            if row is None:
                return None
            return self._row_to_prompt(connection, row)

    def get_prompt_by_alias(self, alias: str) -> PersistedPrompt | None:
        """Fetch the prompt currently associated with an alias.

        Arguments:
            alias: stable prompt alias
        Returns:
            persisted prompt, if present
        """
        if not self.database_path.exists():
            return None
        with self.engine.connect() as connection:
            version = self._get_schema_version(connection)
            if version == 0:
                return None
            self._require_current_schema(version)
            if not inspect(connection).has_table("prompt_aliases"):
                return None
            row = (
                connection.execute(
                    select(self._prompts)
                    .join(self._prompt_aliases)
                    .where(self._prompt_aliases.c.alias == alias)
                )
                .mappings()
                .first()
            )
            if row is None:
                return None
            return self._row_to_prompt(connection, row)

    def list_prompts(
        self,
        *,
        manager_cls: type[Manager] | None = None,
    ) -> list[PersistedPrompt]:
        """List persisted prompts, optionally filtered by operation.

        Arguments:
            manager_cls: optional manager defining the operation filter
        Returns:
            persisted prompts ordered by ID
        """
        if not self.database_path.exists():
            return []
        with self.engine.connect() as connection:
            version = self._get_schema_version(connection)
            if version == 0:
                return []
            self._require_current_schema(version)
            if not inspect(connection).has_table("prompts"):
                return []
            statement = select(self._prompts)
            if manager_cls is not None:
                statement = statement.where(
                    self._prompts.c.operation == manager_cls.operation
                )
            rows = (
                connection.execute(statement.order_by(self._prompts.c.prompt_id))
                .mappings()
                .all()
            )
            return [self._row_to_prompt(connection, row) for row in rows]

    def sync_aliases(
        self,
        alias_prompts: Mapping[str, PersistedPrompt],
        *,
        dry_run: bool,
    ) -> tuple[set[str], set[str], set[str]]:
        """Synchronize stable aliases to immutable prompt rows.

        Arguments:
            alias_prompts: desired prompts keyed by stable alias
            dry_run: if True, compute changes without writing
        Returns:
            inserted prompt IDs, inserted aliases, and updated aliases
        """
        prompts_by_id: dict[str, PersistedPrompt] = {}
        for alias in sorted(alias_prompts):
            if not alias or alias != alias.strip():
                raise ScinoephileError(
                    "Prompt aliases must be nonempty and may not have outer whitespace."
                )
            prompt = alias_prompts[alias]
            invalid_attributes = sorted(
                name
                for name, value in prompt.attributes.items()
                if not name or not isinstance(value, str)
            )
            if invalid_attributes:
                raise ScinoephileError(
                    f"Prompt {prompt.prompt_id} has invalid attributes: "
                    f"{', '.join(invalid_attributes)}."
                )
            expected_id = get_prompt_id(
                prompt.attributes,
                prompt.operation,
                prompt.language,
            )
            if prompt.prompt_id != expected_id:
                raise ScinoephileError(
                    f"Prompt {prompt.prompt_id} does not match its "
                    "content-addressed ID."
                )
            existing = prompts_by_id.get(prompt.prompt_id)
            if existing is not None and (
                existing.operation != prompt.operation
                or existing.language != prompt.language
                or existing.attributes != prompt.attributes
            ):
                raise ScinoephileError(
                    f"Prompt ID {prompt.prompt_id} has conflicting content."
                )
            prompts_by_id[prompt.prompt_id] = prompt

        if dry_run and not self.database_path.exists():
            return (set(prompts_by_id), set(alias_prompts), set())

        if dry_run:
            with self.engine.connect() as connection:
                version = self._get_schema_version(connection)
                if version == 0:
                    return (set(prompts_by_id), set(alias_prompts), set())
                self._require_current_schema(version)
                if not inspect(connection).has_table("prompts"):
                    return (set(prompts_by_id), set(alias_prompts), set())
                return self._get_changes(connection, alias_prompts, prompts_by_id)

        self.create_schema()
        with self.engine.begin() as connection:
            changes = self._get_changes(connection, alias_prompts, prompts_by_id)
            for prompt in prompts_by_id.values():
                connection.execute(
                    sqlite_insert(self._prompts)
                    .values(
                        prompt_id=prompt.prompt_id,
                        operation=prompt.operation,
                        language=prompt.language.tag,
                        attributes_json=serialize_json_object(prompt.attributes),
                    )
                    .on_conflict_do_nothing(index_elements=[self._prompts.c.prompt_id])
                )
            for alias in sorted(alias_prompts):
                prompt = alias_prompts[alias]
                statement = sqlite_insert(self._prompt_aliases).values(
                    alias=alias,
                    prompt_id=prompt.prompt_id,
                )
                connection.execute(
                    statement.on_conflict_do_update(
                        index_elements=[self._prompt_aliases.c.alias],
                        set_={"prompt_id": statement.excluded.prompt_id},
                    )
                )
        logger.info(f"Synchronized {len(alias_prompts)} prompt aliases")
        return changes

    def _get_aliases(
        self,
        connection: Connection,
        prompt_id: str,
    ) -> tuple[str, ...]:
        """Get stable aliases for a prompt.

        Arguments:
            connection: SQLAlchemy connection
            prompt_id: prompt identifier
        Returns:
            ordered aliases
        """
        return tuple(
            str(alias)
            for alias in connection.execute(
                select(self._prompt_aliases.c.alias)
                .where(self._prompt_aliases.c.prompt_id == prompt_id)
                .order_by(self._prompt_aliases.c.alias)
            ).scalars()
        )

    def _get_changes(
        self,
        connection: Connection,
        alias_prompts: Mapping[str, PersistedPrompt],
        prompts_by_id: Mapping[str, PersistedPrompt],
    ) -> tuple[set[str], set[str], set[str]]:
        """Get changes required to synchronize aliases.

        Arguments:
            connection: SQLAlchemy connection
            alias_prompts: desired prompts keyed by stable alias
            prompts_by_id: desired prompts keyed by ID
        Returns:
            inserted prompt IDs, inserted aliases, and updated aliases
        Raises:
            ScinoephileError: if existing content conflicts with its prompt ID
        """
        existing_prompt_rows = {
            str(row["prompt_id"]): row
            for row in connection.execute(
                select(self._prompts).where(
                    self._prompts.c.prompt_id.in_(prompts_by_id)
                )
            )
            .mappings()
            .all()
        }
        for prompt_id, row in existing_prompt_rows.items():
            existing = self._row_to_prompt(connection, row)
            desired = prompts_by_id[prompt_id]
            if (
                existing.operation != desired.operation
                or existing.language != desired.language
                or existing.attributes != desired.attributes
            ):
                raise ScinoephileError(
                    f"Prompt ID {prompt_id} has conflicting persisted content."
                )

        existing_aliases = {
            str(alias): str(prompt_id)
            for alias, prompt_id in connection.execute(
                select(
                    self._prompt_aliases.c.alias,
                    self._prompt_aliases.c.prompt_id,
                ).where(self._prompt_aliases.c.alias.in_(alias_prompts))
            )
        }
        insert_ids = set(prompts_by_id) - existing_prompt_rows.keys()
        insert_aliases = set(alias_prompts) - existing_aliases.keys()
        update_aliases = {
            alias
            for alias, prompt in alias_prompts.items()
            if alias in existing_aliases and existing_aliases[alias] != prompt.prompt_id
        }
        return (insert_ids, insert_aliases, update_aliases)

    def _row_to_prompt(
        self,
        connection: Connection,
        row: RowMapping,
    ) -> PersistedPrompt:
        """Convert a prompt row to a model.

        Arguments:
            connection: SQLAlchemy connection
            row: prompt row
        Returns:
            persisted prompt
        Raises:
            ScinoephileError: if the attributes are not string-valued
        """
        prompt_id = str(row["prompt_id"])
        loaded_attributes = load_json_object(
            row["attributes_json"],
            "Persisted prompt attributes",
        )
        if not all(isinstance(value, str) for value in loaded_attributes.values()):
            raise ScinoephileError(
                f"Persisted prompt {prompt_id} attributes must be strings."
            )
        attributes = cast("dict[str, str]", loaded_attributes)
        try:
            language = Language(str(row["language"]))
        except ValueError as exc:
            raise ScinoephileError(
                f"Persisted prompt {prompt_id} has unsupported language "
                f"{row['language']}."
            ) from exc
        return PersistedPrompt(
            prompt_id=prompt_id,
            operation=str(row["operation"]),
            language=language,
            attributes=attributes,
            aliases=self._get_aliases(connection, prompt_id),
        )
