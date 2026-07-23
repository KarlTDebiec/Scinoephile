#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for TMM."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Language
from test.data.ocr import process_ocr
from test.data.stacking import process_yue_hans_eng, process_zho_hans_eng
from test.data.transcription import process_transcription
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
input_path = title_root / "input"
output_path = title_root / "output"
eng_ocr_path = output_path / "eng_ocr"
yue_hans_ocr_path = output_path / "yue-Hans_ocr"
yue_hant_ocr_path = output_path / "yue-Hant_ocr"
yue_hant_transcribe_path = output_path / "yue-Hant_transcribe"
zho_hans_ocr_path = output_path / "zho-Hans_ocr"
zho_hant_ocr_path = output_path / "zho-Hant_ocr"
zho_hant_guide_path = zho_hant_ocr_path / "fuse_clean_validate_review_flatten.srt"

transcription_additional_context = """
電影背景：
《濟公》係一九九三年香港粵語無厘頭奇幻喜劇。降龍羅漢喺天庭同眾仙打賭，
落凡要改變三個注定受苦嘅人；佢投胎成李修緣，出家後因行為癲喪而得名濟癲，
亦被稱為濟公。故事喺天庭、寺院、怡香院同市井之間轉換，對白夾雜佛教稱謂、
仿古用語、急口粵語、粗口、諧音同誇張重複。請按實際粵語語音用香港繁體粵語
字詞轉錄，保留語氣助詞、俗語同人物身份轉換。參考字幕只提供語意同時間提示，
部分句子係書面中文或普通話式改寫，唔應照抄而令粵語普通話化。

電影專有名稱及用語：
- 降龍羅漢 / 李修緣 / 濟癲 / 濟癲和尚 / 濟公：同一主角喺天界、凡間同出家後
  嘅稱呼，按實際對白保留。
- 伏虎羅漢：降龍羅漢好友，亦會落凡幫佢。
- 觀世音 / 觀音、玉皇大帝 / 玉帝、如來佛祖：天庭同佛門人物，保留正式稱謂
  同口語簡稱。
- 朱大常 / 大種 / 九世乞丐：降龍要點化嘅乞丐；「朱大常」唔好誤寫成近音
  人名。
- 白小玉 / 小玉 / 九世「野雞」：怡香院女子，係降龍要點化嘅第二人；引號內
  稱呼帶貶義，按實際對白保留。
- 袁霸天 / 九世惡人：兇惡大盜，係降龍要點化嘅第三人。
- 怡香院：小玉所在嘅妓院。
- 金身：降龍羅漢留喺天界或法術情節所指嘅羅漢真身，唔係普通金像。
"""

set_logging_verbosity(2)

actions = {
    # "eng_ocr",
    # "yue-Hans_ocr",
    # "yue-Hant_ocr",
    "zho-Hans_ocr",
    "zho-Hant_ocr",
    # "yue-Hans_eng",
    "zho-Hans_eng",
    "yue-Hant_transcribe",
}
if "eng_ocr" in actions:
    process_ocr(title_root, Language.eng, overwrite=False, interactive=True)
if "yue-Hans_ocr" in actions:
    process_ocr(title_root, Language.yue_hans, overwrite=False, interactive=True)
if "yue-Hant_ocr" in actions:
    process_ocr(title_root, Language.yue_hant, overwrite=False, interactive=True)
if "zho-Hans_ocr" in actions:
    process_ocr(title_root, Language.zho_hans, overwrite=False, interactive=True)
if "zho-Hant_ocr" in actions:
    process_ocr(title_root, Language.zho_hant, overwrite=False, interactive=True)
if "yue-Hans_eng" in actions:
    yue_hans_path = yue_hans_ocr_path / "fuse_clean_validate_review_flatten.srt"
    eng_path = eng_ocr_path / "fuse_clean_validate_review_flatten.srt"
    process_yue_hans_eng(title_root, yue_hans_path, eng_path, overwrite=False)
if "zho-Hans_eng" in actions:
    zho_hans_path = zho_hans_ocr_path / "fuse_clean_validate_review_flatten.srt"
    eng_path = eng_ocr_path / "fuse_clean_validate_review_flatten.srt"
    process_zho_hans_eng(title_root, zho_hans_path, eng_path, overwrite=False)
if "yue-Hant_transcribe" in actions:
    process_transcription(
        title_root,
        zho_hant_guide_path,
        reference_path=yue_hant_ocr_path / "fuse_clean_validate_review_flatten.srt",
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        output_dir_path=yue_hant_transcribe_path,
        audio_source_path=yue_hant_transcribe_path / "audio" / "audio.wav",
        media_path=input_path / "source.mkv",
        additional_context=transcription_additional_context,
        transcription_kw={
            "delineation_json_path": yue_hant_transcribe_path
            / "lang/yue_zho/transcription/delineation/mps.json",
            "punctuation_json_path": yue_hant_transcribe_path
            / "lang/yue_zho/transcription/punctuation/mps.json",
        },
        run_cleaning=False,
        run_review_and_translation=False,
        overwrite=True,
    )
