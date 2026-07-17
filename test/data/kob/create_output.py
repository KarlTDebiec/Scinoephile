#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for KOB."""

from __future__ import annotations

from pathlib import Path

from scinoephile.analysis.character_error_rate import SeriesCER
from scinoephile.analysis.diff import SeriesDiff
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Language
from scinoephile.core.subtitles import Series
from test.data.ocr import process_ocr
from test.data.srt import process_srt
from test.data.stacking import process_yue_hans_eng, process_zho_hans_eng
from test.data.transcription import (
    get_reference_for_guide_blocks,
    process_transcription,
)
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
output_path = title_root / "output"
set_logging_verbosity(2)

eng_ocr_path = output_path / "eng_ocr"
eng_path = output_path / "eng"
zho_hant_ocr_path = output_path / "zho-Hant_ocr"
yue_hant_path = output_path / "yue-Hant"
yue_hans_path = output_path / "yue-Hans"
yue_hant_transcribe_path = output_path / "yue-Hant_transcribe"
zho_hant_guide_path = zho_hant_ocr_path / "fuse_clean_validate_review_flatten.srt"

transcription_additional_context = """
電影背景：
呢套係1992年嘅香港粵語武俠喜劇《武狀元蘇乞兒》（King of Beggars），故事發生
喺清朝。紈絝子弟蘇察哈爾燦目不識丁，為咗如霜上京考武狀元，後來被貶做
乞兒，加入丐幫，最後對抗天理教教主趙無極。對白會喺通俗粵語喜劇、仿古
朝廷用語同武俠術語之間轉換；要保留呢啲語域差異同既定嘅繁體人名。
zho-Hant字幕只係語義指引；如果佢嘅字眼同實際粵語對白唔同，應該保留粵語
講法。

電影特定人名同術語：
- 蘇察哈爾燦 / 蘇燦 / 阿燦 / 蘇乞兒：都係主角嘅稱呼；按實際對白保留所講
  嘅稱呼，包括暱稱「阿燦」
- 如霜 / 如霜姑娘：女主角，亦係丐幫中人
- 小翠：如霜個妹
- 趙無極 / 趙大人 / 趙先生：天理教教主；寫「無極」，唔係「無忌」
- 僧格林沁：蒙古王爺，亦係博達爾多嘅叔父；寫「沁」，唔係「慶」
- 博達爾多：蘇燦喺武科舉嘅對手
- 洪日新 / 老鬼新 / 新師叔：都係同一個老乞兒，係洪七公嘅傳人；寫「日新」，
  唔係「日慶」
- 莫老三 / 莫大叔：都係同一位丐幫長老
- 丐幫 / 乞兒幫：同一個幫會；按實際對白保留所講嘅叫法
- 天理教：趙無極領導嘅教派
- 怡紅院：如霜以清倌人身份出現嘅妓院
- 武狀元：武科舉第一名
- 打狗棒 / 打狗棒法：zho-Hant指引嘅寫法；粵語對白寫「打狗棍 / 打狗棍法」
- 醉回夢生法 / 睡夢羅漢拳：洪日新傳畀蘇燦嘅睡眠武功
- 降龍十八掌：丐幫絕學
- 大還丹：恢復功力嘅丹藥
- 蓮花落陣：用嚟考驗蘇燦能否統領丐幫嘅陣法
- 麒麟煙：天理教使用嘅煙霧武器
"""

actions = {
    # "eng_ocr",
    # "zho-Hant_ocr",
    # "eng",
    # "yue-Hans",
    # "yue-Hant",
    # "zho-Hans_eng",
    # "yue-Hans_eng",
    "yue-Hant_transcribe",
    "yue-Hant_diff",
}

if "eng_ocr" in actions:
    process_ocr(title_root, Language.eng, overwrite=False, interactive=True)
if "zho-Hant_ocr" in actions:
    process_ocr(title_root, Language.zho_hant, overwrite=False, interactive=True)
if "zho-Hans_eng" in actions:
    zho_hans_srt_path = (
        zho_hant_ocr_path / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )
    eng_srt_path = eng_ocr_path / "fuse_clean_validate_review_flatten.srt"
    process_zho_hans_eng(title_root, zho_hans_srt_path, eng_srt_path, overwrite=False)
if "eng" in actions:
    process_srt(
        title_root,
        Language.eng,
        reference_path=eng_ocr_path / "fuse_clean_validate_review.srt",
        one_end_idx=1421,
        overwrite=True,
    )
if "yue-Hans" in actions:
    process_srt(
        title_root,
        Language.yue_hans,
        reference_path=zho_hant_ocr_path / "fuse_clean_validate_review.srt",
        one_end_idx=1421,
        two_end_idx=1461,
        overwrite=True,
    )
if "yue-Hant" in actions:
    process_srt(
        title_root,
        Language.yue_hant,
        reference_path=zho_hant_ocr_path / "fuse_clean_validate_review.srt",
        one_end_idx=1421,
        two_end_idx=1461,
        overwrite=True,
    )
if "yue-Hans_eng" in actions:
    yue_hans_srt_path = yue_hans_path / "clean_review_flatten_timewarp.srt"
    eng_srt_path = eng_path / "clean_review_flatten_timewarp.srt"
    process_yue_hans_eng(title_root, yue_hans_srt_path, eng_srt_path, overwrite=True)
if "yue-Hant_transcribe" in actions:
    process_transcription(
        title_root,
        zho_hant_guide_path,
        reference_path=yue_hant_path / "clean_review_flatten_timewarp.srt",
        output_dir_path=yue_hant_transcribe_path,
        # stop_at_idx=8,
        additional_context=transcription_additional_context,
        overwrite=True,
    )
if "yue-Hant_diff" in actions:
    yue_hant_transcribe = Series.load(
        yue_hant_transcribe_path / "transcribe_clean_review_translate.srt"
    )
    zho_hant_guide = Series.load(zho_hant_guide_path)
    yue_hant_reference = Series.load(
        yue_hant_path / "clean_review_flatten_timewarp.srt"
    )
    yue_hant_reference = get_reference_for_guide_blocks(
        yue_hant_reference,
        zho_hant_guide,
        200,
    )
    zho_hant_guide_by_timing = {
        (subtitle.start, subtitle.end): subtitle for subtitle in zho_hant_guide
    }
    aligned_zho_hant_guide = Series(
        events=[
            zho_hant_guide_by_timing[(subtitle.start, subtitle.end)]
            for subtitle in yue_hant_transcribe
        ]
    )
    diff = SeriesDiff(
        yue_hant_transcribe,
        yue_hant_reference,
        one_lbl="GAP TRANSLATION",
        two_lbl="REFERENCE",
    )
    print(
        diff.get_stacked_str(
            three=aligned_zho_hant_guide,
            include_equal=True,
        )
    )
    print(SeriesCER(yue_hant_reference, yue_hant_transcribe))
