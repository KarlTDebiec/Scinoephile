#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""SQLite persistence for LLM model configurations."""

from __future__ import annotations

from logging import getLogger

from sqlalchemy import (
    CheckConstraint,
    Column,
    Index,
    MetaData,
    Table,
    Text,
    inspect,
    select,
)
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import RowMapping

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.optimization.persistence.sqlite import (
    OptimizationSqliteStore,
    deserialize_json,
    serialize_json,
)

from .id import get_model_id
from .persisted_model import PersistedModel

__all__ = ["ModelSqliteStore"]

logger = getLogger(__name__)


class ModelSqliteStore(OptimizationSqliteStore):
    """SQLite persistence and lookup for model configurations."""

    _metadata = MetaData()
    """SQLAlchemy metadata owned by model persistence."""

    _models = Table(
        "models",
        _metadata,
        Column("model_id", Text, primary_key=True),
        Column("provider", Text, nullable=False),
        Column("model", Text, nullable=False),
        Column("base_url", Text),
        Column("settings_json", Text, nullable=False),
        CheckConstraint(
            "json_valid(settings_json)",
            name="models_settings_json_valid",
        ),
        CheckConstraint(
            "json_type(settings_json) = 'object'",
            name="models_settings_json_object",
        ),
        Index("models_provider_model", "provider", "model"),
    )
    """Content-addressed model configurations."""

    def add_model(self, model: PersistedModel) -> bool:
        """Add a model configuration if it is not already stored.

        Arguments:
            model: model configuration to store
        Returns:
            whether the model configuration was inserted
        Raises:
            ScinoephileError: if the model ID does not match its configuration
        """
        canonical_model = PersistedModel.from_config(
            model.provider_name,
            model.model_name,
            base_url=model.base_url,
            settings=model.settings,
        )
        if model.model_id != canonical_model.model_id:
            raise ScinoephileError(
                f"Model {model.model_id} does not match its content-addressed ID."
            )

        self.create_schema()
        with self.engine.begin() as connection:
            result = connection.execute(
                sqlite_insert(self._models)
                .values(
                    model_id=model.model_id,
                    provider=model.provider_name,
                    model=model.model_name,
                    base_url=model.base_url,
                    settings_json=serialize_json(model.settings),
                )
                .on_conflict_do_nothing(index_elements=[self._models.c.model_id])
            )
            if result.rowcount:
                logger.info(f"Stored model configuration {model.model_id}")
                return True

            row = (
                connection.execute(
                    select(self._models).where(
                        self._models.c.model_id == model.model_id
                    )
                )
                .mappings()
                .one()
            )
            if self._row_to_model(row) != canonical_model:
                raise ScinoephileError(
                    f"Stored model {model.model_id} does not match its configuration."
                )
            return False

    def get_model(self, model_id: str) -> PersistedModel | None:
        """Fetch a model configuration by ID.

        Arguments:
            model_id: model configuration identifier
        Returns:
            persisted model configuration, if present
        """
        if not self.database_path.exists():
            return None
        with self.engine.connect() as connection:
            if not inspect(connection).has_table("models"):
                return None
            row = (
                connection.execute(
                    select(self._models).where(self._models.c.model_id == model_id)
                )
                .mappings()
                .first()
            )
            if row is None:
                return None
            return self._row_to_model(row)

    @staticmethod
    def _row_to_model(row: RowMapping) -> PersistedModel:
        """Convert a model row to a model configuration.

        Arguments:
            row: model row
        Returns:
            persisted model configuration
        Raises:
            ScinoephileError: if persisted content is invalid
        """
        model_id = str(row["model_id"])
        base_url_value = row["base_url"]
        base_url = None
        if base_url_value is not None:
            base_url = str(base_url_value)
        model = PersistedModel.from_config(
            str(row["provider"]),
            str(row["model"]),
            base_url=base_url,
            settings=deserialize_json(
                row["settings_json"],
                f"Persisted model {model_id} settings",
            ),
        )
        expected_id = get_model_id(
            model.provider_name,
            model.model_name,
            model.base_url,
            model.settings,
        )
        if model_id != expected_id:
            raise ScinoephileError(
                f"Persisted model {model_id} does not match its content-addressed ID."
            )
        return model
