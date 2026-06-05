#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for T."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from test.data.ocr import process_eng_ocr, process_zho_hans_ocr, process_zho_hant_ocr
from test.data.stacking import process_zho_hans_eng
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
output_path = title_root / "output"
set_logging_verbosity(2)

eng_ocr_path = output_path / "eng_ocr"
zho_hans_ocr_path = output_path / "zho-Hans_ocr"

actions = {
    "eng_ocr",
    "zho-Hans_ocr",
    "zho-Hant_ocr",
    "zho-Hans_eng",
}

if "eng_ocr" in actions:
    process_eng_ocr(title_root, overwrite=False)
if "zho-Hans_ocr" in actions:
    process_zho_hans_ocr(title_root, overwrite=False)
if "zho-Hant_ocr" in actions:
    process_zho_hant_ocr(title_root, overwrite=False)
if "zho-Hans_eng" in actions:
    zho_hans_path = zho_hans_ocr_path / "fuse_clean_validate_review_flatten.srt"
    eng_path = eng_ocr_path / "fuse_clean_validate_review_flatten.srt"
    process_zho_hans_eng(title_root, zho_hans_path, eng_path, overwrite=False)
