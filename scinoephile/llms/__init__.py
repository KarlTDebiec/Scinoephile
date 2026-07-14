#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to interactions with LLMs.

Package hierarchy (modules may import from any above):
* delineation / gap_translation / guided_review / guided_translation / ocr_fusion
  / pairwise_review / providers / punctuation / review / translation

LLM shapes:

| Tracks | T1    | T2 | Name               | Prefix            |
| ------ | ----- | -- | ------------------ | ----------------- |
| 1      | n     |    | review             | Review            |
| 1      | n     |    | translation        | Translation       |
| 2      | 1     | 1  | pairwise_review    | PairwiseReview    |
| 2      | n     | m  | guided_review      | GuidedReview      |
| 2      | 1     | 1  | ocr_fusion         | OcrFusion         |
| 2      | n     | 1  | punctuation        | Punctuation       |
| 2      | 2     | 2  | delineation        | Delineation       |
| 2      | n - m | n  | gap_translation    | GapTranslation    |
| 2      | n     | m  | guided_translation | GuidedTranslation |
"""

from __future__ import annotations

import functools
import logging
from pathlib import Path

import scinoephile.core.llms.utils as llm_utils
from scinoephile import common
from scinoephile.core.llms import Manager, Prompt, TestCase

__all__ = ["load_default_test_cases"]

logger = logging.getLogger(__name__)


@functools.cache
def load_default_test_cases(
    manager_cls: type[Manager],
    prompt: Prompt,
    relative_paths: tuple[Path, ...],
) -> tuple[TestCase, ...]:
    """Load default test cases from repository JSON files and cache the result.

    Arguments:
        manager_cls: manager class used to construct test case models
        prompt: text for LLM correspondence
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
            llm_utils.load_test_cases_from_json(path, manager_cls, prompt=prompt)
        )
        logger.info(f"Loaded {len(loaded_test_cases)} test cases from {path}.")
    return tuple(loaded_test_cases)
