#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for ACOPOPB."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Language
from test.data.ocr import process_ocr
from test.data.stacking import process_yue_hans_eng, process_zho_hans_eng
from test.data.transcription import process_transcription
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
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
《西遊記第壹佰零壹回之月光寶盒》係一九九五年香港粵語無厘頭奇幻喜劇。開場講
孫悟空反叛師父唐三藏，觀世音令佢五百年後投胎贖罪；五百年後，孫悟空轉世成
五嶽山斧頭幫幫主至尊寶，遇上春三十娘同白晶晶。對白節奏急、口語化，夾雜古裝
稱謂、佛道術語、粗口、諧音笑話同刻意重複。請按實際粵語語音用香港繁體粵語
字詞轉錄，保留語氣助詞同角色口吻。參考字幕主要提供語意同時間提示，部分句子
係書面中文或普通話式改寫，唔應照抄而令粵語普通話化。

電影專有名稱及用語：
- 孫悟空 / 悟空 / 老孫：同一角色；五百年後轉世為至尊寶。
- 唐三藏 / 唐僧 / 師父：孫悟空師父。
- 觀世音 / 觀音姐姐：開場追究孫悟空罪責嘅菩薩。
- 至尊寶 / 幫主 / 玉面飛龍：斧頭幫幫主，孫悟空轉世。
- 二當家：斧頭幫二把手，豬八戒轉世。
- 盲炳：斧頭幫幫眾；參考字幕有時寫成「瞎子」。
- 春三十娘 / 蜘蛛精：盤絲大仙大弟子，白晶晶師姐。
- 白晶晶 / 晶晶 / 白骨精：春三十娘師妹，五百年前同孫悟空有情緣。
- 菩提老祖：神仙；佢化身成一揪菩提子引出連串諧音笑話，參考字幕有時概括寫
  「葡萄」，要以實際粵語語音為準。
- 紫霞仙子 / 盤絲大仙：同一角色於唔同時期嘅稱呼。
- 牛魔王：孫悟空結拜大哥。
- 五嶽山：斧頭幫所在，前稱五指山；主要洞府叫盤絲洞，亦提到菩提洞。
- 月光寶盒：可用真言「般若波羅蜜」令時光倒流嘅寶物。
- 照妖鏡 / 乾坤袋 / 隱身符 / 移魂大法 / 三味白骨火：劇中法器、法術名稱。
"""

set_logging_verbosity(2)

actions = {
    # "eng_ocr",
    # "yue-Hans_ocr",
    # "yue-Hant_ocr",
    # "zho-Hans_ocr",
    # "zho-Hant_ocr",
    # "yue-Hans_eng",
    # "zho-Hans_eng",
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
        additional_context=transcription_additional_context,
        run_review_and_translation=False,
        overwrite=True,
    )
