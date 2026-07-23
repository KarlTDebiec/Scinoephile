#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""SQLite persistence for LLM prompts."""

from __future__ import annotations

from collections.abc import Mapping
from logging import getLogger
from typing import cast

from sqlalchemy import CheckConstraint, Column, MetaData, Table, Text, inspect, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Connection, RowMapping

from scinoephile.core import Language
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.optimization.persistence.sqlite import (
    OptimizationSqliteStore,
    deserialize_json,
    serialize_json,
)

from .id import get_prompt_id
from .persisted_prompt import PersistedPrompt

__all__ = ["PromptSqliteStore"]

logger = getLogger(__name__)


class PromptSqliteStore(OptimizationSqliteStore):
    """SQLite persistence and lookup for prompts by alias."""

    _metadata = MetaData()
    """SQLAlchemy metadata owned by prompt persistence."""

    _prompts = Table(
        "prompts",
        _metadata,
        Column("alias", Text, primary_key=True),
        Column("prompt_id", Text, nullable=False),
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
    )
    """Current prompt content keyed by stable alias."""

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
            if not inspect(connection).has_table("prompts"):
                return None
            row = (
                connection.execute(
                    select(self._prompts).where(self._prompts.c.alias == alias)
                )
                .mappings()
                .first()
            )
            if row is None:
                return None
            return self._row_to_prompt(row)

    def sync_aliases(
        self,
        alias_prompts: Mapping[str, PersistedPrompt],
        *,
        dry_run: bool,
    ) -> tuple[set[str], set[str]]:
        """Synchronize current prompt content by stable alias.

        Arguments:
            alias_prompts: desired prompts keyed by stable alias
            dry_run: if True, compute changes without writing
        Returns:
            inserted and updated aliases
        Raises:
            ScinoephileError: if a prompt ID does not match its content
        """
        for prompt in alias_prompts.values():
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

        if dry_run and not self.database_path.exists():
            return (set(alias_prompts), set())

        if dry_run:
            with self.engine.connect() as connection:
                if not inspect(connection).has_table("prompts"):
                    return (set(alias_prompts), set())
                return self._get_changes(connection, alias_prompts)

        self.create_schema()
        with self.engine.begin() as connection:
            changes = self._get_changes(connection, alias_prompts)
            for alias, prompt in sorted(alias_prompts.items()):
                statement = sqlite_insert(self._prompts).values(
                    alias=alias,
                    prompt_id=prompt.prompt_id,
                    operation=prompt.operation,
                    language=prompt.language.code,
                    attributes_json=serialize_json(dict(prompt.attributes)),
                )
                connection.execute(
                    statement.on_conflict_do_update(
                        index_elements=[self._prompts.c.alias],
                        set_={
                            "prompt_id": statement.excluded.prompt_id,
                            "operation": statement.excluded.operation,
                            "language": statement.excluded.language,
                            "attributes_json": statement.excluded.attributes_json,
                        },
                    )
                )
        logger.info(f"Synchronized {len(alias_prompts)} prompt aliases")
        return changes

    def _get_changes(
        self,
        connection: Connection,
        alias_prompts: Mapping[str, PersistedPrompt],
    ) -> tuple[set[str], set[str]]:
        """Get changes required to synchronize prompt aliases.

        Arguments:
            connection: SQLAlchemy connection
            alias_prompts: desired prompts keyed by stable alias
        Returns:
            inserted and updated aliases
        """
        existing_ids = {
            str(alias): str(prompt_id)
            for alias, prompt_id in connection.execute(
                select(self._prompts.c.alias, self._prompts.c.prompt_id).where(
                    self._prompts.c.alias.in_(alias_prompts)
                )
            )
        }
        insert_aliases = set(alias_prompts) - existing_ids.keys()
        update_aliases = {
            alias
            for alias, prompt in alias_prompts.items()
            if alias in existing_ids and existing_ids[alias] != prompt.prompt_id
        }
        return (insert_aliases, update_aliases)

    @staticmethod
    def _row_to_prompt(row: RowMapping) -> PersistedPrompt:
        """Convert a prompt row to a model.

        Arguments:
            row: prompt row
        Returns:
            persisted prompt
        Raises:
            ScinoephileError: if persisted content is invalid
        """
        prompt_id = str(row["prompt_id"])
        loaded_attributes = deserialize_json(
            row["attributes_json"],
            "Persisted prompt attributes",
        )
        if not all(isinstance(value, str) for value in loaded_attributes.values()):
            raise ScinoephileError(
                f"Persisted prompt {prompt_id} attributes must be strings."
            )
        attributes = tuple(sorted(cast("dict[str, str]", loaded_attributes).items()))
        try:
            language = Language(str(row["language"]))
        except ValueError as exc:
            raise ScinoephileError(
                f"Persisted prompt {prompt_id} has unsupported language "
                f"{row['language']}."
            ) from exc
        prompt = PersistedPrompt(
            prompt_id=prompt_id,
            operation=str(row["operation"]),
            language=language,
            attributes=attributes,
        )
        if prompt.prompt_id != get_prompt_id(
            prompt.attributes,
            prompt.operation,
            prompt.language,
        ):
            raise ScinoephileError(
                f"Persisted prompt {prompt_id} does not match its content-addressed ID."
            )
        return prompt
