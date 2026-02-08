#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Helpers for loading default test cases from repository test data."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path

from scinoephile.common import package_root

from .manager import Manager
from .test_case import TestCase
from .utils import load_test_cases_from_json

__all__ = [
    "get_repo_test_data_root",
    "load_default_test_cases_from_repo_data",
]

logger = getLogger(__name__)


def get_repo_test_data_root() -> Path | None:
    """Get repository test data root if available.

    Returns:
        path to repository test data root if available
    """
    test_data_root = package_root.parent / "test" / "data"
    if not test_data_root.is_dir():
        logger.warning(
            "Repository test data directory is not available at %s; "
            "default test cases were not loaded.",
            test_data_root,
        )
        return None
    return test_data_root


def load_default_test_cases_from_repo_data(
    manager_cls: type[Manager],
    prompt_cls: type,
    relative_paths: list[Path],
) -> list[TestCase]:
    """Load default test cases from repository JSON files.

    Arguments:
        manager_cls: manager class used to construct test case models
        prompt_cls: text for LLM correspondence
        relative_paths: paths relative to repository test data root
    Returns:
        loaded test cases
    Raises:
        FileNotFoundError: if a configured test case file is not found
    """
    test_data_root = get_repo_test_data_root()
    if test_data_root is None:
        return []

    loaded_test_cases: list[TestCase] = []
    for relative_path in relative_paths:
        path = test_data_root / relative_path
        if not path.is_file():
            raise FileNotFoundError(
                f"Configured default test case file is missing: {path}"
            )
        loaded_test_cases.extend(
            load_test_cases_from_json(path, manager_cls, prompt_cls=prompt_cls)
        )
    return loaded_test_cases
