#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MNT."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Language
from scinoephile.core.stacking import get_stacked_series
from scinoephile.core.subtitles import Series
from scinoephile.lang.translation.guided import get_guided_translator
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_converted
from scinoephile.workflows.clean import clean_series
from scinoephile.workflows.flatten import flatten
from scinoephile.workflows.translation import translate_series_guided
from test.data.ocr import process_ocr
from test.data.prompts import EngZhoYueGuidedTranslationPrompt
from test.data.stacking import process_zho_hans_eng
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
    "eng_ocr",
    "zho-Hans_ocr",
    "zho-Hant_ocr",
    "zho-Hans_eng",
    # "yue_eng",
    # "yue_zho-Hans_eng",
}

if "eng_ocr" in actions:
    process_ocr(title_root, Language.eng, overwrite=False, interactive=True)
if "zho-Hans_ocr" in actions:
    process_ocr(title_root, Language.zho_hans, overwrite=False, interactive=True)
if "zho-Hant_ocr" in actions:
    process_ocr(title_root, Language.zho_hant, overwrite=False, interactive=True)
if "zho-Hans_eng" in actions:
    zho_hans_path = zho_hans_ocr_path / "fuse_clean_validate_review_flatten.srt"
    eng_path = eng_ocr_path / "fuse_clean_validate_review_flatten.srt"
    process_zho_hans_eng(title_root, zho_hans_path, eng_path, overwrite=False)
if "yue_eng" in actions:
    yue_zho_hant = Series.load(input_path / "yue_zho-Hant.srt")
    jpn_eng = Series.load(input_path / "jpn_eng.srt")
    translator = get_guided_translator(
        Language.zho_hant,
        Language.eng,
        prompt=EngZhoYueGuidedTranslationPrompt,
        test_case_path=(output_path / "yue_eng/lang/eng_zho/guided_translation.json"),
        additional_context=additional_context,
        auto_verify=True,
    )
    yue_eng = translate_series_guided(
        yue_zho_hant,
        jpn_eng,
        source_language=Language.zho_hant,
        target_language=Language.eng,
        translator=translator,
    )
    yue_eng.save(output_path / "yue_eng/eng.srt")
if "yue_zho-Hans_eng" in actions:
    yue_zho_hant = Series.load(input_path / "yue_zho-Hant.srt")
    yue_zho_hant = clean_series(yue_zho_hant, language=Language.yue_hant)
    yue_zho_hant = flatten(yue_zho_hant, language=Language.yue_hant)
    yue_zho_hans = get_zho_converted(yue_zho_hant, OpenCCConfig.t2s)

    yue_eng = Series.load(output_path / "yue_eng/eng.srt")
    yue_eng = clean_series(yue_eng, language=Language.eng)
    yue_eng = flatten(yue_eng, language=Language.eng)

    yue_zho_hans_eng = get_stacked_series(yue_zho_hans, yue_eng)
    yue_zho_hans_eng.save(output_path / "yue_eng/zho-Hans_eng.srt")
