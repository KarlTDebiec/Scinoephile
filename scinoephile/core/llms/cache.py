#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM response cache."""

from __future__ import annotations

import hashlib
import json
from logging import getLogger
from pathlib import Path

from scinoephile.common.file import open_atomic_text_file
from scinoephile.common.validation import val_output_dir_path

__all__ = ["LlmCache"]

logger = getLogger(__name__)


class LlmCache:
    """Cache of LLM response payloads."""

    def __init__(
        self,
        cache_root_path: Path | str | None,
        overwrite: bool = False,
    ):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache, or None to disable
            overwrite: whether to replace matching cache files
        """
        self.cache_dir_path = None
        """Directory in which cached LLM responses are stored."""
        if cache_root_path is not None:
            self.cache_dir_path = val_output_dir_path(Path(cache_root_path) / "llm")

        self.overwrite = overwrite
        """Whether matching cache files should be replaced."""

    def discard(self, cache_path: Path):
        """Delete an invalid cache file.

        Arguments:
            cache_path: cache file to delete
        """
        cache_path.unlink()
        logger.info(f"Deleted invalid cache file: {cache_path}")

    def get_path(
        self,
        identity: object,
        system_prompt: str,
        tools_json: str,
        query_json: str,
    ) -> Path | None:
        """Get a cache path based on query identity and prompts.

        Arguments:
            identity: provider and test-case identity
            system_prompt: system prompt used for the query
            tools_json: JSON representation of configured tools
            query_json: JSON representation of the query
        Returns:
            path to cache file, or None when caching is disabled
        """
        if self.cache_dir_path is None:
            return None

        identity_json = json.dumps(
            identity,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        content = identity_json + system_prompt + tools_json + query_json
        sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return self.cache_dir_path / f"{sha256}.json"

    def load(self, cache_path: Path | None) -> str | None:
        """Load a cached response payload.

        Arguments:
            cache_path: cache file path, or None when caching is disabled
        Returns:
            cached response payload, or None when unavailable
        """
        if cache_path is None:
            return None
        if self.overwrite and cache_path.exists():
            cache_path.unlink()
            logger.info(f"Removed LLM response cache: {cache_path}")
        if not cache_path.exists():
            return None

        return cache_path.read_text(encoding="utf-8")

    def mark_used(self, cache_path: Path):
        """Update the access marker for a successfully loaded cache file.

        Arguments:
            cache_path: cache file that was successfully loaded
        """
        cache_path.touch()

    def save(self, cache_path: Path | None, contents: str):
        """Save an LLM response payload.

        Arguments:
            cache_path: cache file path, or None when caching is disabled
            contents: serialized response payload
        """
        if cache_path is None:
            return
        with open_atomic_text_file(cache_path) as cache_file:
            cache_file.write(contents)
        logger.debug(f"Saved to cache: {cache_path}")
