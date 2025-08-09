#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Cantonese audio alignment testing."""

from __future__ import annotations

import asyncio
import re
from logging import info
from pathlib import Path

from scinoephile.audio.cantonese.alignment import Aligner
from scinoephile.common.validation import val_input_dir_path
from scinoephile.core.abcs import DynamicLLMQueryer, FixedLLMQueryer


async def _replace(
    path: Path, varible: str, pattern: re.Pattern[str], replacement: str
):
    contents = await asyncio.to_thread(path.read_text, encoding="utf-8")
    replacement = f"{varible} = {replacement}  # {varible}"
    new_contents = pattern.sub(replacement, contents)
    await asyncio.to_thread(path.write_text, new_contents, encoding="utf-8")
    info(f"Replaced test cases {varible} in {path.name}.")


async def update_all_test_cases(
    test_root: Path | str, block_idx: int, aligner: Aligner
):
    """Update all test cases for the specified block.

    Arguments:
        test_root: Path to root directory of test cases
        block_idx: Index of block for which to update test cases
        aligner: Aligner containing queryers for test cases
    """
    test_root = val_input_dir_path(test_root)

    tasks = [
        update_test_cases(
            test_root / "distribution.py",
            f"distribute_test_cases_block_{block_idx}",
            aligner.distributor,
        ),
        update_test_cases(
            test_root / "shifting.py",
            f"shift_test_cases_block_{block_idx}",
            aligner.shifter,
        ),
        update_test_cases(
            test_root / "merging.py",
            f"merge_test_cases_block_{block_idx}",
            aligner.merger,
        ),
        update_test_cases(
            test_root / "proofing.py",
            f"proof_test_cases_block_{block_idx}",
            aligner.proofer,
        ),
        update_dynamic_test_cases(
            test_root / "translation.py",
            f"translate_test_case_block_{block_idx}",
            aligner.translator,
        ),
        update_dynamic_test_cases(
            test_root / "review.py",
            f"review_test_case_block_{block_idx}",
            aligner.reviewer,
        ),
    ]

    await asyncio.gather(*tasks)


async def update_test_cases(path: Path, variable: str, queryer: FixedLLMQueryer):
    """Update test cases.

    Arguments:
        path: Path to file containing test cases
        variable: Name of the variable containing test cases
        queryer: LLMQueryer instance to query for test cases
    """
    pattern = re.compile(rf"{variable}\s*=\s*\[(.*?)\]  # {variable}", re.DOTALL)
    replacement = queryer.encountered_test_cases_source_str
    await _replace(path, variable, pattern, replacement)
    await asyncio.to_thread(queryer.clear_encountered_test_cases)


async def update_dynamic_test_cases(
    path: Path, variable: str, queryer: DynamicLLMQueryer
):
    """Update dynamic test cases.

    Arguments:
        path: Path to file containing test cases
        variable: Name of the variable containing test case
        queryer: DynamicLLMQueryer instance to query for test cases
    """
    pattern = re.compile(rf"{variable}\s*=(.*?)# {variable}", re.DOTALL)
    replacement = queryer.encountered_test_cases_source_str
    await _replace(path, variable, pattern, replacement)
    await asyncio.to_thread(queryer.clear_encountered_test_cases)


__all__ = [
    "update_dynamic_test_cases",
    "update_all_test_cases",
    "update_test_cases",
]
