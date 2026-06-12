#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for ACOPOPB."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from test.data.ocr import process_ocr
from test.data.stacking import process_yue_hans_eng, process_zho_hans_eng
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
input_path = title_root / "input"
output_path = title_root / "output"
eng_ocr_path = output_path / "eng_ocr"
yue_hans_ocr_path = output_path / "yue-Hans_ocr"
zho_hans_ocr_path = output_path / "zho-Hans_ocr"

set_logging_verbosity(2)

actions = {
    "eng_ocr",
    "yue-Hans_ocr",
    "yue-Hant_ocr",
    "zho-Hans_ocr",
    "zho-Hant_ocr",
    "yue-Hans_eng",
    "zho-Hans_eng",
}

if "eng_ocr" in actions:
    process_ocr(title_root, "eng", overwrite=False, interactive=False)
if "yue-Hans_ocr" in actions:
    process_ocr(title_root, "yue-Hans", overwrite=False, interactive=False)
if "yue-Hant_ocr" in actions:
    process_ocr(title_root, "yue-Hant", overwrite=False, interactive=False)
if "zho-Hans_ocr" in actions:
    process_ocr(title_root, "zho-Hans", overwrite=False, interactive=False)
if "zho-Hant_ocr" in actions:
    process_ocr(title_root, "zho-Hant", overwrite=False, interactive=False)
if "yue-Hans_eng" in actions:
    yue_hans_path = yue_hans_ocr_path / "fuse_clean_validate_review_flatten.srt"
    eng_path = eng_ocr_path / "fuse_clean_validate_review_flatten.srt"
    process_yue_hans_eng(title_root, yue_hans_path, eng_path, overwrite=False)
if "zho-Hans_eng" in actions:
    zho_hans_path = zho_hans_ocr_path / "fuse_clean_validate_review_flatten.srt"
    eng_path = eng_ocr_path / "fuse_clean_validate_review_flatten.srt"
    process_zho_hans_eng(title_root, zho_hans_path, eng_path, overwrite=False)
