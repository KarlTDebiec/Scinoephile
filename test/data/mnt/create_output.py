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
from test.data.ocr import process_ocr
from test.data.prompts import EngZhoYueGuidedTranslationPrompt
from test.data.stacking import process_zho_hans_eng
from test.data.transcription import process_transcription_pipeline
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
input_path = title_root / "input"
output_path = title_root / "output"
set_logging_verbosity(2)

eng_ocr_path = output_path / "eng_ocr"
zho_hans_ocr_path = output_path / "zho-Hans_ocr"
yue_hant_transcribe_path = output_path / "yue-Hant_transcribe"
yue_audio_cache_path = Path(
    "/Volumes/Backup/Video/Cache/My Neighbor Totoro (1988)/"
    "My Neighbor Totoro (1988) - yue.m4a"
)
# The remux metadata is reversed: stream 12 is the verified Cantonese program
yue_remux_path = Path(
    "/Volumes/Backup/Video/BD Remux/My Neighbor Totoro (1988) - [yolerejiju] "
    "My Neighbor Totoro 1988 1080p BD REMUX FLAC 2.0 [Audio Multi] "
    "[Sub Multi].mkv"
)

transcription_additional_context = """
電影背景：
《龍貓》係一九八八年宮崎駿動畫電影嘅香港粵語配音版。草壁一家搬到鄉郊，
小月同妹妹小美喺媽媽留院養病期間遇到龍貓、煤煤蟲同貓巴士。對白以家庭日常、
兒童說話同溫暖奇幻場面為主。請按實際粵語語音用香港繁體粵語字詞轉錄，保留
語氣助詞、兒童口吻同角色稱呼。評估參考字幕係書面中文，雖然對應粵語音軌，
但經常意譯或將粵語口語改寫成標準中文；唔應照抄而令轉錄普通話化。

電影專有名稱及用語：
- 小月 / 姐姐：草壁家長女，英文名 Satsuki。
- 小美 / 妹妹：草壁家幼女，英文名 Mei。
- 草壁：一家人嘅姓氏。
- 勘太：鄰居男孩。
- 婆婆：照顧兩姊妹嘅鄰居長輩。
- 龍貓：森林入面嘅神秘生物；按實際對白保留「龍貓」。
- 貓巴士：貓形巴士。
- 煤煤蟲 / 煤屎：屋入面嘅黑色小精靈；按實際粵語講法轉錄。
- 樟樹、橡果子 / 種子、粟米：故事中反覆出現嘅事物。
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
    # "eng_ocr",
    # "zho-Hans_ocr",
    # "zho-Hant_ocr",
    # "zho-Hans_eng",
    "yue-Hant_transcribe"
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
if "yue-Hant_transcribe" in actions:
    media_path = yue_audio_cache_path
    media_start_seconds = 0.0
    stream_index = 0
    if not media_path.exists():
        media_path = yue_remux_path
        media_start_seconds = 1.0
        stream_index = 12
    process_transcription_pipeline(
        title_root,
        reference_path=input_path / "yue_zho-Hant.srt",
        language=Language.yue_hant,
        output_dir_path=yue_hant_transcribe_path,
        audio_path=yue_hant_transcribe_path / "audio.wav",
        media_path=media_path,
        stream_index=stream_index,
        media_start_seconds=media_start_seconds,
        additional_context=transcription_additional_context,
        reference_name="zho-Hant",
        terminal_alignment_authority="zho-Hant",
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
