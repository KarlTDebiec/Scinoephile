#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MLAMD."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Language
from scinoephile.media.audio import AudioExtractionMode
from test.data.ocr import process_ocr
from test.data.stacking import process_yue_hans_eng, process_zho_hans_eng
from test.data.transcription import process_transcription_pipeline
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
output_path = title_root / "output"
set_logging_verbosity(2)

eng_ocr_path = output_path / "eng_ocr"
zho_hans_ocr_path = output_path / "zho-Hans_ocr"
zho_hant_ocr_path = output_path / "zho-Hant_ocr"
yue_hant_transcribe_path = output_path / "yue-Hant_transcribe"
yue_transcribe_backup_path = output_path / "yue_transcribe_backup"
yue_remux_path = Path("/Volumes/Backup/Video/BD Remux/My Life as McDull (2001).mkv")
old_yue_hans_path = (
    yue_transcribe_backup_path / "transcribe_translate_guided_review.srt"
)
transcription_additional_context = """
電影背景：
《麥兜故事》係二〇〇一年香港粵語動畫電影。成年麥兜回憶自己喺九龍大角咀成長、
同單親媽媽麥太生活，同埋喺春田花花幼稚園讀書嘅片段。故事由日常小事、幻想、
新聞報道、課堂對答、廣告式旁白同歌曲串連，講麥兜想去馬爾代夫、食聖誕火雞、
學運動攞金牌等願望。對白有兒童口吻、地道香港粵語、急口令、同音字笑話、
刻意重複同由古典樂改詞嘅歌。請按實際語音用香港繁體粵語字詞轉錄，保留語氣
助詞、口吃或重複、押韻同唔同說話語域。評估參考字幕係書面中文，可能意譯、
省略口語助詞或將粵語改成標準中文；唔應照抄而令轉錄普通話化。

電影專有名稱及用語：
- 麥兜 / 麥兜兜：主角，住喺大角咀嘅小豬；按實際對白保留所講嘅稱呼。
- 麥太 / 阿媽：麥兜嘅媽媽；本名玉蓮。
- 麥嘜：麥兜嘅同學兼朋友，唔好同「麥兜」混淆。
- Miss Chan / 陳老師：春田花花幼稚園老師；英文稱呼保留為「Miss Chan」。
- 校長：春田花花幼稚園校長，亦會用唔同身份同聲線出現。
- 春田花花幼稚園：麥兜讀書嘅學校；校歌亦用呢個全名。
- 大角咀：麥兜居住嘅九龍舊區。
- 馬爾代夫：麥兜夢想去嘅旅行地點，對白可能反覆逐字解釋個名。
- 李麗珊 / 珊珊：香港滑浪風帆奧運金牌運動員，麥兜嘅偶像。
- 黎根 / 黎根師傅：麥兜學搶包山嘅師傅。
- 長洲搶包山 / 包山：電影借嚟想像成體育比賽嘅香港傳統活動。
- 掟蛋撻：電影提出嘅另一項虛構比賽項目；「掟」按粵語用字書寫。
- 魚蛋、粗麵、通粉、火雞、豬腩肉：戲中反覆出現嘅食物名稱，按實際對白保留。
"""

actions = {
    # "eng_ocr",
    # "zho-Hans_ocr",
    # "zho-Hant_ocr",
    # "zho-Hans_eng",
    # "yue-Hans_eng",
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
if "yue-Hans_eng" in actions:
    yue_hans_path = (
        yue_transcribe_backup_path / "transcribe_translate_guided_review.srt"
    )
    eng_path = eng_ocr_path / "fuse_clean_validate_review_flatten.srt"
    process_yue_hans_eng(title_root, yue_hans_path, eng_path, overwrite=False)
if "yue-Hant_transcribe" in actions:
    process_transcription_pipeline(
        title_root,
        reference_path=zho_hant_ocr_path / "fuse_clean_validate_review_flatten.srt",
        language=Language.yue_hant,
        output_dir_path=yue_hant_transcribe_path,
        audio_path=yue_hant_transcribe_path / "audio.wav",
        media_path=yue_remux_path,
        stream_index=1,
        audio_extraction_mode=AudioExtractionMode.CENTER_HEAVY,
        additional_context=transcription_additional_context,
        reference_name="zho-Hant",
        terminal_alignment_authority="merged",
    )
