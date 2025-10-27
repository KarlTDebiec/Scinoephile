#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Cantonese audio alignment testing."""

from __future__ import annotations

import asyncio
from pathlib import Path

from scinoephile.audio.cantonese.alignment import Aligner
from scinoephile.common.validation import val_input_dir_path
from scinoephile.testing import update_dynamic_test_cases, update_test_cases


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


__all__ = [
    "update_all_test_cases",
]
