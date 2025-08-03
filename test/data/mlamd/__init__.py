#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""

from __future__ import annotations

from logging import debug, info

import pytest
from PIL import Image

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import ScinoephileError
from scinoephile.image import ImageSeries
from scinoephile.testing import test_data_root
from test.data.mlamd.distribution import mlamd_distribute_test_cases
from test.data.mlamd.merging import mlamd_merge_test_cases
from test.data.mlamd.proofing import mlamd_proof_test_cases
from test.data.mlamd.review import mlamd_review_test_cases
from test.data.mlamd.shifting import mlamd_shift_test_cases
from test.data.mlamd.translation import mlamd_translate_test_cases

input_dir = test_data_root / "mlamd" / "input"
output_dir = test_data_root / "mlamd" / "output"


# region 简体中文
@pytest.fixture
def mlamd_zho_hans() -> ImageSeries:
    """MLAMD 简体中文 image series."""
    try:
        return ImageSeries.load(output_dir / "zho-Hans")
    except FileNotFoundError:
        return ImageSeries.load(input_dir / "zho-Hans.sup")


@pytest.fixture()
def mlamd_zho_hans_image() -> Image.Image:
    """MLAMD 简体中文 image."""
    return Image.open(output_dir / "zho-Hans" / "0001.png")


@pytest.fixture
def mlamd_zho_hans_validation_directory() -> str:
    """MLAMD 简体中文 validation directory."""
    return output_dir / "zho-Hans_validation"


# endregion


# region 繁体中文
@pytest.fixture
def mlamd_zho_hant() -> ImageSeries:
    """MLAMD 繁体中文 image series."""
    try:
        return ImageSeries.load(output_dir / "zho-Hant")
    except FileNotFoundError:
        return ImageSeries.load(input_dir / "zho-Hant.sup")


@pytest.fixture()
def mlamd_zho_hant_image() -> Image.Image:
    """MLAMD 繁体中文 image."""
    return Image.open(output_dir / "zho-Hant" / "0001.png")


@pytest.fixture
def mlamd_zho_hant_validation_directory() -> str:
    """MLAMD 繁体中文 validation directory."""
    return output_dir / "zho-Hant_validation"


# endregion


# region English
@pytest.fixture
def mlamd_eng() -> ImageSeries:
    """MLAMD English image series."""
    try:
        return ImageSeries.load(output_dir / "eng")
    except FileNotFoundError:
        return ImageSeries.load(input_dir / "eng.sup")


@pytest.fixture()
def mlamd_eng_image() -> Image.Image:
    """MLAMD English image."""
    return Image.open(output_dir / "eng" / "0001.png")


@pytest.fixture
def mlamd_eng_validation_directory() -> str:
    """MLAMD English validation directory."""
    return output_dir / "eng_validation"


# endregion


___all__ = [
    "mlamd_zho_hans",
    "mlamd_zho_hans_image",
    "mlamd_zho_hans_validation_directory",
    "mlamd_zho_hant",
    "mlamd_zho_hant_image",
    "mlamd_zho_hant_validation_directory",
    "mlamd_eng",
    "mlamd_eng_image",
    "mlamd_eng_validation_directory",
    "mlamd_distribute_test_cases",
    "mlamd_shift_test_cases",
    "mlamd_merge_test_cases",
    "mlamd_proof_test_cases",
    "mlamd_translate_test_cases",
    "mlamd_review_test_cases",
]

if __name__ == "__main__":
    set_logging_verbosity(1)

    test_case_lists = {
        "Distribute": mlamd_distribute_test_cases,
        "Shift": mlamd_shift_test_cases,
        "Merge": mlamd_merge_test_cases,
        "Proof": mlamd_proof_test_cases,
    }
    for test_case_type, test_cases in test_case_lists.items():
        info(f"Validating {test_case_type} test cases...")

        # Validate test cases
        test_case_dict = {}
        noops = 0
        for test_case in test_cases:
            if test_case.noop:
                debug(test_case.source_str)
                noops += 1
            else:
                info(test_case.source_str)
            if test_case.key in test_case_dict:
                raise ScinoephileError(f"Duplicate found:\n{test_case.source_str}")
            test_case_dict[test_case.key] = test_case
        info(
            f"{test_case_type} test cases validated: {len(test_case_dict)} "
            f"unique keys, of which {len(test_cases) - noops} direct changes."
        )

        # Validate queries
        query_dict = {}
        for test_case in test_cases:
            debug(test_case.source_str)
            if test_case.query.query_key in query_dict:
                raise ScinoephileError(
                    f"Duplicate query found:\n{test_case.source_str}"
                )
            query_dict[test_case.query.query_key] = test_case.query
        info(f"{test_case_type} queries validated: {len(query_dict)} unique keys.")
