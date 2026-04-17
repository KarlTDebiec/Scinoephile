#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for ACOPTC."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from test.data.ocr import process_zho_hans_ocr, process_zho_hant_ocr
from test.data.synchronization import process_yue_hans_eng, process_zho_hans_eng
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
itunes_input_dir = input_dir / "itunes"
output_dir = title_root / "output"
output_dir.mkdir(parents=True, exist_ok=True)
set_logging_verbosity(2)

actions = {
    # "繁體中文 (OCR)",
    # "简体中文 (OCR)",
    # "Bilingual 简体中文 and English (iTunes)",
    # "Bilingual 简体粤文 and English (iTunes)",
}

if "繁體中文 (OCR)" in actions:
    process_zho_hant_ocr(title_root, overwrite_srt=True, force_validation=True)
if "简体中文 (OCR)" in actions:
    process_zho_hans_ocr(title_root, overwrite_srt=True, force_validation=True)
if "Bilingual 简体中文 and English (iTunes)" in actions:
    process_zho_hans_eng(
        title_root,
        zho_hans_path=output_dir / "zho-Hans_fuse_clean_validate_proofread_flatten.srt",
        eng_path=itunes_input_dir / "eng-6.srt",
        overwrite=True,
    )
if "Bilingual 简体粤文 and English (iTunes)" in actions:
    process_yue_hans_eng(
        title_root,
        yue_hans_path=input_dir / "yue-Hans_lens.srt",
        eng_path=itunes_input_dir / "eng-6.srt",
        overwrite=True,
    )
