#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Cantonese audio alignment testing."""

from __future__ import annotations

import re
from logging import info
from pathlib import Path

from scinoephile.audio.cantonese.distribution import DistributeTestCase  # noqa: F401
from scinoephile.audio.cantonese.merging import MergeTestCase  # noqa: F401
from scinoephile.audio.cantonese.proofing import ProofTestCase  # noqa: F401
from scinoephile.audio.cantonese.shifting import ShiftTestCase  # noqa: F401
from scinoephile.audio.cantonese.translation import Translator
from scinoephile.core.abcs import LLMQueryer


def _replace(path: Path, varible: str, pattern: re.Pattern[str], replacement: str):
    contents = path.read_text(encoding="utf-8")
    replacement = f"{varible} = {replacement}  # {varible}"
    new_contents = pattern.sub(replacement, contents)
    path.write_text(new_contents, encoding="utf-8")
    info(f"Replaced test cases {varible} in {path.name}.")


def update_test_cases(path: Path, variable: str, queryer: LLMQueryer):
    """Update test cases.

    Arguments:
        path: Path to file containing test cases
        variable: Name of the variable containing test cases
        queryer: LLMQueryer instance to query for test cases
    """
    pattern = re.compile(rf"{variable}\s*=\s*\[(.*?)\]  # {variable}", re.DOTALL)
    replacement = queryer.test_case_log_str
    _replace(path, variable, pattern, replacement)
    queryer.clear_test_case_log()


def update_translation_test_cases(path: Path, variable: str, queryer: Translator):
    """Update translation test cases.

    Arguments:
        path: Path to file containing test cases
        variable: Name of the variable containing test case
        queryer: Translator instance to query for test cases
    """
    pattern = re.compile(rf"{variable}\s*=(.*?)# {variable}", re.DOTALL)
    replacement = queryer.test_case_log_str
    _replace(path, variable, pattern, replacement)
    queryer.clear_test_case_log()


__all__ = [
    "update_test_cases",
    "update_translation_test_cases",
]
