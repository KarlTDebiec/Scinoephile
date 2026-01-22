#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for T."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core.testing import test_data_root
from test.data.ocr import process_eng_ocr, process_zho_hans_ocr, process_zho_hant_ocr
from test.data.synchronization import process_zho_hans_eng

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"
set_logging_verbosity(2)

actions = {
    "繁體中文 (OCR)",
}

if "繁體中文 (OCR)" in actions:
    process_zho_hant_ocr(title_root, overwrite_srt=True, force_validation=True)
if "简体中文 (OCR)" in actions:
    process_zho_hans_ocr(title_root, overwrite_srt=True, force_validation=True)
if "English (OCR)" in actions:
    process_eng_ocr(title_root, overwrite_srt=True, force_validation=True)
if "Bilingual 简体中文 and English" in actions:
    process_zho_hans_eng(
        title_root,
        zho_hans_path=output_dir / "zho-Hans_fuse_clean_validate_proofread_flatten.srt",
        eng_path=output_dir / "eng_fuse_clean_validate_proofread_flatten.srt",
        overwrite=True,
    )
