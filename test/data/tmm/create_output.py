#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for TMM."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from test.data.ocr import process_eng_ocr, process_zho_hans_ocr, process_zho_hant_ocr
from test.data.synchronization import process_yue_hans_eng, process_zho_hans_eng
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"
output_dir.mkdir(parents=True, exist_ok=True)
set_logging_verbosity(2)

actions = {
    "繁體粵文 (OCR)",
    "简体粤文 (OCR)",
    "繁體中文 (OCR)",
    "简体中文 (OCR)",
    "English (OCR)",
    # "Bilingual 简体中文 and English",
    # "Bilingual 简体粤文 and English",
}

if "繁體粵文 (OCR)" in actions:
    process_zho_hant_ocr(
        title_root,
        sup_path=Path(
            "/Users/karldebiec/Code/ScinoephileProjects/scinoephile_projects/data/The Mad Monk (1993)/input/bd/zho-3.sup"
        ),
        lang="yue",
        overwrite_srt=True,
        force_validation=True,
    )
if "简体粤文 (OCR)" in actions:
    process_zho_hans_ocr(
        title_root,
        sup_path=Path(
            "/Users/karldebiec/Code/ScinoephileProjects/scinoephile_projects/data/The Mad Monk (1993)/input/bd/zho-4.sup"
        ),
        lang="yue",
        overwrite_srt=True,
        force_validation=True,
    )
if "繁體中文 (OCR)" in actions:
    process_zho_hant_ocr(
        title_root,
        sup_path=Path(
            "/Users/karldebiec/Code/ScinoephileProjects/scinoephile_projects/data/The Mad Monk (1993)/input/bd/zho-7.sup"
        ),
        overwrite_srt=True,
        force_validation=True,
    )
if "简体中文 (OCR)" in actions:
    process_zho_hans_ocr(
        title_root,
        sup_path=Path(
            "/Users/karldebiec/Code/ScinoephileProjects/scinoephile_projects/data/The Mad Monk (1993)/input/bd/zho-6.sup"
        ),
        overwrite_srt=True,
        force_validation=True,
    )
if "English (OCR)" in actions:
    process_eng_ocr(
        title_root,
        sup_path=Path(
            "/Users/karldebiec/Code/ScinoephileProjects/scinoephile_projects/data/The Mad Monk (1993)/input/bd/eng-5.sup"
        ),
        overwrite_srt=True,
        force_validation=True,
    )
if "Bilingual 简体中文 and English" in actions:
    process_zho_hans_eng(
        title_root,
        zho_hans_path=output_dir / "zho-Hans_fuse_clean_validate_proofread_flatten.srt",
        eng_path=output_dir / "eng_fuse_clean_validate_proofread_flatten.srt",
        overwrite=True,
    )
if "Bilingual 简体粤文 and English" in actions:
    process_yue_hans_eng(
        title_root,
        yue_hans_path=input_dir / "yue-Hans_lens.srt",
        eng_path=input_dir / "eng_lens.srt",
        overwrite=True,
    )
