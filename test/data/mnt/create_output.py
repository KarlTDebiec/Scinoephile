#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MNT."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core.stacking import get_stacked_series
from scinoephile.core.subtitles import Series
from scinoephile.lang.eng.cleaning import get_eng_cleaned
from scinoephile.lang.eng.flattening import get_eng_flattened
from scinoephile.lang.zho.cleaning import get_zho_cleaned
from scinoephile.lang.zho.flattening import get_zho_flattened
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_converted
from scinoephile.multilang.eng_zho.guided_translation import (
    get_eng_translated_from_zho_with_eng_guidance,
    get_eng_zho_guided_translator,
)
from test.data.ocr import process_eng_ocr, process_zho_hans_ocr, process_zho_hant_ocr
from test.data.prompts import EngGuidedTranslationVsZhoOfYuePrompt
from test.data.synchronization import process_zho_hans_eng
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
input_path = title_root / "input"
output_path = title_root / "output"
set_logging_verbosity(2)

eng_ocr_path = output_path / "eng_ocr"
zho_hans_ocr_path = output_path / "zho-Hans_ocr"

additional_context = """
Movie context:
This is My Neighbor Totoro. The dialogue is from a family-friendly Studio Ghibli
film about two young sisters, Satsuki and Mei, moving with their father to the
countryside while their mother is in the hospital. Keep the English natural,
warm, and child-friendly. Prefer established English Totoro terminology from the
reference subtitles. Do not translate Cantonese idioms, teasing, or playful
insults literally when they would sound crude, offensive, or out of tone in
English. Translate the intended tone, not just the literal wording.

Movie-specific names and terminology:
- 小月 / 姐姐: Satsuki
- 小美 / 次子: Mei
- 草壁: Kusakabe
- 勘太: Kanta
- 婆婆 / 八婆 / 八婶: Granny
- 龙猫 / 龍貓: Totoro
- 樟树 / 樟樹: camphor tree
- 橡果子 / 种子 / 種子: acorn
- 煤屎 / 煤煤虫 / 煤煤蟲: soot sprites
- 粟米: corn
- 妈咪 / 媽咪: Mom
"""

actions = {
    # "繁體中文 (OCR)",
    # "简体中文 (OCR)",
    # "English (OCR)",
    # "Bilingual 简体中文 and English",
    "Guided English from 粤语",
    "Bilingual 简体中文 and guided English from 粤语",
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
        zho_hans_path=zho_hans_ocr_path / "fuse_clean_validate_review_flatten.srt",
        eng_path=eng_ocr_path / "fuse_clean_validate_review_flatten.srt",
        overwrite=True,
    )
if "Guided English from 粤语" in actions:
    yue_zho_hant = Series.load(input_path / "yue_zho-Hant.srt")
    jpn_eng = Series.load(input_path / "jpn_eng.srt")
    translator = get_eng_zho_guided_translator(
        prompt_cls=EngGuidedTranslationVsZhoOfYuePrompt,
        test_case_path=(
            output_path / "yue_eng/multilang/eng_zho/guided_translation.json"
        ),
        additional_context=additional_context,
        auto_verify=True,
    )
    yue_eng = get_eng_translated_from_zho_with_eng_guidance(
        yue_zho_hant,
        jpn_eng,
        translator=translator,
    )
    yue_eng.save(output_path / "yue_eng/eng.srt")
if "Bilingual 简体中文 and guided English from 粤语" in actions:
    yue_zho_hant = Series.load(input_path / "yue_zho-Hant.srt")
    yue_zho_hant = get_zho_cleaned(yue_zho_hant)
    yue_zho_hant = get_zho_flattened(yue_zho_hant)
    yue_zho_hans = get_zho_converted(yue_zho_hant, OpenCCConfig.t2s)

    yue_eng = Series.load(output_path / "yue_eng/eng.srt")
    yue_eng = get_eng_cleaned(yue_eng)
    yue_eng = get_eng_flattened(yue_eng)

    yue_zho_hans_eng = get_stacked_series(yue_zho_hans, yue_eng)
    yue_zho_hans_eng.save(output_path / "yue_eng/zho-Hans_eng.srt")
