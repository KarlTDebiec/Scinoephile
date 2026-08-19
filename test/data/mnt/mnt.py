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
from scinoephile.workflows.flatten import flatten_series
from scinoephile.workflows.translation import translate_series_guided
from test.data.aligned_transcription import process_transcription
from test.data.ocr import process_ocr
from test.data.prompts import EngZhoYueGuidedTranslationPrompt
from test.data.stacking import process_zho_hans_eng
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
input_path = title_root / "input"
output_path = title_root / "output"
eng_ocr_path = output_path / "eng_ocr"
zho_hans_ocr_path = output_path / "zho-Hans_ocr"

set_logging_verbosity(2)

transcription_additional_context = """
電影背景：
《龍貓》係一九八八年宮崎駿動畫電影嘅香港粵語配音版。大卷一家搬到鄉郊，
草子同妹妹次子喺媽媽留院養病期間遇到龍貓、煤炭屎鬼同貓巴士。對白以家庭日常、
兒童說話同溫暖奇幻場面為主。請按實際粵語語音用香港繁體粵語字詞轉錄，保留
語氣助詞、兒童口吻同角色稱呼。評估參考字幕係書面中文，雖然對應粵語音軌，
但經常意譯或將粵語口語改寫成標準中文；唔應照抄而令轉錄普通話化。

電影專有名稱及用語：
- 草子 / 姐姐：大卷家長女，英文名 Satsuki。
- 次子 / 妹妹：大卷家幼女，英文名 Mei。提及或者呼叫呢個角色時，ASR 可能誤寫成
  「自己」、「廁紙」、「廁子」、「赤子」、「智子」等；應按語境用「次子」。
- 大卷：兩姊妹嘅爸爸，亦係一家人嘅姓氏。
- 阿信：鄰居男孩。
- 八婆：照顧兩姊妹嘅鄰居長輩；對白亦會按稱呼講「八嬸」，應跟實際語音。
- 山吹老師：草子學校嘅老師。
- 七國山醫院：媽媽留院嘅醫院；優先用呢個寫法，唔好寫成「七角山醫院」。
- 天公公：向天空祈求停雨時嘅稱呼；唔好寫成「雨公公」。
- 龍貓：森林入面嘅神秘生物；按實際對白保留「龍貓」。
- 呲呲嗏、嘣嘣吧：兩隻較細嘅龍貓嘅叫聲。
- 貓巴士：貓形巴士。
- 煤炭屎鬼 / 煤屎：屋入面嘅黑色小精靈；按實際粵語講法轉錄。
- 樟樹、橡子 / 種子、粟米：故事中反覆出現嘅事物。
"""

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
- 草子 / 姐姐: Satsuki
- 次子 / 妹妹: Mei
- 大卷: Kusakabe or Dad, according to context
- 阿信: Kanta
- 婆婆 / 八婆 / 八婶: Granny
- 龙猫 / 龍貓: Totoro
- 呲呲嗏 / 嘣嘣吧: vocalizations made by the two smaller Totoros
- 樟树 / 樟樹: camphor tree
- 橡子 / 种子 / 種子: acorn
- 煤屎 / 煤炭屎鬼: soot sprites
- 粟米: corn
- 妈咪 / 媽咪: Mom
"""

actions = {
    # "eng_ocr",
    # "zho-Hans_ocr",
    # "zho-Hant_ocr",
    # "zho-Hans_eng",
    # "yue_eng",
    # "yue_zho-Hans_eng",
    "yue-Hant_transcribe"
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
if "yue-Hant_transcribe" in actions:
    process_transcription(
        title_root,
        reference_path=input_path / "yue_zho-Hant.srt",
        # stop_at_idx=5,
        exclude_blocks=[1, 2, 216],
        additional_context=transcription_additional_context,
        reference_name="zho-Hant",
        terminal_authority="merged",
        overwrite=True,
    )
if "yue_eng" in actions:
    yue_zho_hant = Series.load(input_path / "yue_zho-Hant.srt")
    jpn_eng = Series.load(input_path / "jpn_eng.srt")
    translator = get_guided_translator(
        Language.zho_hant,
        Language.eng,
        prompt=EngZhoYueGuidedTranslationPrompt,
        current_test_cases_path=(
            output_path / "yue_eng/lang/eng_zho/guided_translation.json"
        ),
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
    yue_zho_hant = flatten_series(yue_zho_hant, language=Language.yue_hant)
    yue_zho_hans = get_zho_converted(yue_zho_hant, OpenCCConfig.t2s)

    yue_eng = Series.load(output_path / "yue_eng/eng.srt")
    yue_eng = clean_series(yue_eng, language=Language.eng)
    yue_eng = flatten_series(yue_eng, language=Language.eng)

    yue_zho_hans_eng = get_stacked_series(yue_zho_hans, yue_eng)
    yue_zho_hans_eng.save(output_path / "yue_eng/zho-Hans_eng.srt")
