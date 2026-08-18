#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for T."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Language
from test.data.aligned_transcription import process_transcription
from test.data.ocr import process_ocr
from test.data.stacking import process_zho_hans_eng
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
output_path = title_root / "output"
set_logging_verbosity(2)

transcription_additional_context = """
電影背景：
《樹大招風》係一套以一九九七年香港回歸前夕為背景嘅香港犯罪片，三條故事線
分別跟住季正雄、葉國歡同卓子強。江湖誤傳三個互不相識嘅「賊王」準備聯手做
一單驚天大案，傳聞逐漸推動佢哋互相尋找。電影穿插械劫、綁架、走私、香港警方
同內地官場情節，對白包括地道香港粵語、江湖黑話、粗口，同少量普通話、英語及
泰語。請按實際粵語語音用香港繁體粵語字詞轉錄，保留稱呼、語氣助詞、粗口同
口語節奏。評估參考字幕係書面中文，可能意譯、省略粵語助詞，或者將口語改成
標準中文；唔應照抄而令轉錄普通話化。

電影專有名稱及用語：
- 季正雄 / 潮哥：行事低調嘅通緝犯；「潮哥」係佢招募同黨時用嘅化名。
- 葉國歡 / 歡哥 / 張大寶：持械行劫出名嘅賊王；到內地走私電器時化名張大寶。
- 卓子強 / 卓先生：靠綁架富商致富、想策劃更大案件嘅賊王。
- 大輝：季正雄物色嘅同黨，其他人亦會叫佢「輝哥」。
- 阿金 / 阿忠：葉國歡身邊嘅手下，按實際稱呼轉錄。
- 方老闆：葉國歡走私生意接觸嘅內地商人。
- 陳科：工商局官員；「科」係職銜稱呼，唔係姓名嘅一部分。
- 易發：番禺一間走私電器舖頭，葉國歡以張大寶身份接手。
- 飛虎隊：香港警察特別任務連。
- 物華街：觀塘珠寶金行集中嘅街道，葉國歡一夥喺當地連環械劫。
"""

actions = {
    # "eng_ocr",
    # "zho-Hans_ocr",
    # "zho-Hant_ocr",
    # "zho-Hans_eng",
    "yue-Hant_transcribe"
}

if "eng_ocr" in actions:
    process_ocr(title_root, Language.eng, overwrite=False, interactive=True)
if "zho-Hans_ocr" in actions:
    process_ocr(title_root, Language.zho_hans, overwrite=False, interactive=True)
if "zho-Hant_ocr" in actions:
    process_ocr(title_root, Language.zho_hant, overwrite=False, interactive=True)
if "zho-Hans_eng" in actions:
    zho_hans_path = (
        output_path / "zho-Hans_ocr" / "fuse_clean_validate_review_flatten.srt"
    )
    eng_path = output_path / "eng_ocr" / "fuse_clean_validate_review_flatten.srt"
    process_zho_hans_eng(title_root, zho_hans_path, eng_path, overwrite=False)
if "yue-Hant_transcribe" in actions:
    process_transcription(
        title_root,
        reference_path=(
            output_path / "zho-Hant_ocr" / "fuse_clean_validate_review_flatten.srt"
        ),
        additional_context=transcription_additional_context,
        reference_name="zho-Hant",
        terminal_authority="merged",
    )
