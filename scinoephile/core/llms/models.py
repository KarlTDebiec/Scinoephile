#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to models."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationInfo, model_validator
from pydantic_core import PydanticCustomError

__all__ = [
    "LLMModel",
    "get_model_name",
    "make_hashable",
]


class LLMModel(BaseModel):
    """Base model for LLM queries, answers, and test cases."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any):
        """Validate serialized field aliases after model construction.

        Arguments:
            **kwargs: arguments passed through Pydantic subclass initialization
        """
        super().__pydantic_init_subclass__(**kwargs)

        fields_by_alias: dict[str, list[str]] = {}
        for field_name, field_info in cls.model_fields.items():
            alias = field_info.alias
            if alias is None:
                alias = field_name
            if not alias.strip():
                raise ValueError(
                    f"{cls.__name__} field {field_name!r} must have a nonblank alias."
                )
            fields_by_alias.setdefault(alias, []).append(field_name)

        duplicate_aliases = {
            alias: field_names
            for alias, field_names in fields_by_alias.items()
            if len(field_names) > 1
        }
        if duplicate_aliases:
            details = "; ".join(
                f"{alias!r} is used by {', '.join(field_names)}"
                for alias, field_names in duplicate_aliases.items()
            )
            raise ValueError(f"{cls.__name__} field aliases must be unique; {details}.")

    @model_validator(mode="before")
    @classmethod
    def require_aliases_at_json_boundaries(
        cls,
        value: object,
        info: ValidationInfo,
    ) -> object:
        """Reject semantic field names at alias-only JSON boundaries.

        Arguments:
            value: value to validate
            info: Pydantic validation context
        Returns:
            value after canonical field-name validation
        """
        if not info.context or not info.context.get("alias_only"):
            return value
        if not isinstance(value, Mapping):
            return value

        noncanonical_fields = [
            (field_name, field.alias)
            for field_name, field in cls.model_fields.items()
            if field.alias is not None
            and field.alias != field_name
            and field_name in value
        ]
        if noncanonical_fields:
            replacements = ", ".join(
                f"{field_name!r} (use {alias!r})"
                for field_name, alias in noncanonical_fields
            )
            raise PydanticCustomError(
                "llm_alias_only",
                "JSON input must use field aliases: {replacements}.",
                {"replacements": replacements},
            )

        return value


def get_model_name(base_name: str, suffix: str) -> str:
    """Build a Pydantic-valid class name from a base name and suffix.

    If the name exceeds the 64-character Pydantic limit, replace the suffix
    with a deterministic short hash.

    Arguments:
        base_name: name of base class
        suffix: descriptive suffix

    Returns:
        Valid class name string
    """
    # Base name and suffix are short enough to use directly
    if len(base_name) + 1 + len(suffix) <= 64:
        return f"{base_name}_{suffix}"

    # Base name is too long even for hash of suffix to be used
    if len(base_name) + 1 + 12 > 64:
        raise ValueError("Base name too long to create a valid Pydantic class name.")

    # Use base name and hash of suffix
    digest = hashlib.sha256(suffix.encode("utf-8")).hexdigest()[:12]
    return f"{base_name}_{digest}"


def make_hashable(value: Any) -> Any:
    """Make a value hashable for use in keys.

    Arguments:
        value: Value to make hashable
    Returns:
        Hashable representation of the value
    """
    if isinstance(value, list):
        return tuple(make_hashable(v) for v in value)
    elif isinstance(value, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in value.items()))
    return value
