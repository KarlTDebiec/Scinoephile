#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for ACOPTC."""

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
《西遊記大結局之仙履奇緣》係一九九五年香港粵語無厘頭奇幻喜劇，承接
《月光寶盒》。至尊寶為救白晶晶，利用月光寶盒返到五百年前，遇上同一肉身、
日夜交替嘅紫霞同青霞。紫霞認定拔出紫青寶劍嘅至尊寶係有緣人；至尊寶後來要
接受孫悟空身份同取西經使命。對白節奏急、口語化，夾雜古裝稱謂、佛道術語、
粗口、諧音笑話、刻意重複同角色扮演。請按實際粵語語音用香港繁體粵語字詞
轉錄，保留語氣助詞、粗口同角色口吻。參考字幕只提供語意同時間提示，部分句子
係書面中文或普通話式改寫，唔應照抄而令粵語普通話化。

電影專有名稱及用語：
- 至尊寶 / 孫悟空 / 齊天大聖 / 老孫：同一角色喺唔同身份或語境下嘅稱呼，
  按實際對白保留。
- 紫霞仙子 / 紫霞、青霞仙子 / 青霞：兩條燈芯共用同一肉身，日夜呈現唔同
  性格。
- 白晶晶 / 晶晶：至尊寶原本想救返嘅愛人。
- 牛魔王 / 大哥：孫悟空結拜大哥；鐵扇公主 / 牛夫人係佢妻子，香香係佢妹妹。
- 唐三藏 / 唐僧 / 師父、豬八戒 / 八戒、沙悟淨 / 沙僧：取西經師徒，按實際
  稱呼轉錄。
- 觀世音 / 觀音：處理孫悟空罪責同取經使命嘅菩薩。
- 月光寶盒：可以用真言「般若波羅蜜」穿梭時空嘅寶物。
- 紫青寶劍：紫霞用嚟認定有緣人嘅寶劍。
- 金剛圈 / 緊箍兒：套喺孫悟空頭上、約束佢取經嘅法器，按實際讀音選詞。
"""

set_logging_verbosity(2)

actions = {
    "eng_ocr",
    "yue-Hans_ocr",
    "yue-Hant_ocr",
    "zho-Hans_ocr",
    "zho-Hant_ocr",
    "yue-Hans_eng",
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
