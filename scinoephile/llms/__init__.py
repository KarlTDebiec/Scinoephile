#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to interactions with LLMs.

This module may import from: common, core

Hierarchy within module, where lower entries may import from higher entries:
* block_review / dual_1_to_1 / dual_2_to_2 / dual_n_to_1 / dual_n_to_m
  / dual_n_to_n / gap_translation / providers / translation

LLM shapes:

| Tracks | T1    | T2   | Name                  | Prefix         | Description         |
| ------ | ----- | ---- | --------------------- | -------------- | ------------------- |
| 1      | n     |      | block_review          | BlockReview    | Changes with note.  |
| 1      | n     |      | translation           | Translation    | Translation.        |
| 2      | 1     | 1    | dual_1_to_1           | Dual1To1       | Paired subs.        |
| 2      | n     | 1    | dual_n_to_1           | DualNTo1       | n to one.           |
| 2      | 2     | 2    | dual_2_to_2           | Dual2To2       | Two pairs.          |
| 2      | n     | n    | dual_n_to_n           | DualNToN       | Matched blocks.     |
| 2      | n - m | n    | gap_translation       | GapTranslation | Fill gaps.          |
| 2      | n     | m    | dual_n_to_m           | DualNToM       | Independent sizes.  |
"""

from __future__ import annotations

import functools
import logging
from pathlib import Path

import scinoephile.core.llms.utils as llm_utils
from scinoephile import common
from scinoephile.core.llms import Manager, TestCase

__all__ = ["load_default_test_cases"]

logger = logging.getLogger(__name__)


@functools.cache
def load_default_test_cases(
    manager_cls: type[Manager],
    prompt_cls: type,
    relative_paths: tuple[Path, ...],
) -> tuple[TestCase, ...]:
    """Load default test cases from repository JSON files and cache the result.

    Arguments:
        manager_cls: manager class used to construct test case models
        prompt_cls: text for LLM correspondence
        relative_paths: paths relative to repository test data root
    Returns:
        loaded test cases
    """
    test_data_root = common.package_root.parent / "test/data"
    if not test_data_root.is_dir():
        logger.info(f"Test data root {test_data_root} does not exist.")
        return tuple()

    loaded_test_cases: list[TestCase] = []
    for relative_path in relative_paths:
        path = test_data_root / relative_path
        if not path.is_file():
            continue
        loaded_test_cases.extend(
            llm_utils.load_test_cases_from_json(
                path, manager_cls, prompt_cls=prompt_cls
            )
        )
        logger.info(f"Loaded {len(loaded_test_cases)} test cases from {path}.")
    return tuple(loaded_test_cases)
