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
from scinoephile.core.abcs import LLMQueryer


def _replace_test_cases_in_file(file_path: Path, list_name: str, new_cases_str: str):
    pattern = re.compile(
        rf"{list_name}\s*=\s*\[(.*?)\]  # {list_name}",
        re.DOTALL,
    )
    contents = file_path.read_text(encoding="utf-8")
    replacement = f"{list_name} = {new_cases_str}  # {list_name}"
    new_contents = pattern.sub(replacement, contents)
    file_path.write_text(new_contents, encoding="utf-8")
    info(f"Replaced test cases {list_name} in {file_path.name}.")


def update_test_cases(path: Path, case_list_name: str, queryer: LLMQueryer) -> None:
    """Update test cases."""
    test_case_log_str = queryer.test_case_log_str

    _replace_test_cases_in_file(
        path,
        case_list_name,
        test_case_log_str,
    )
    queryer.clear_test_case_log()


__all__ = [
    "update_test_cases",
]
