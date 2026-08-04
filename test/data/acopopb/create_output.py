#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for ACOPOPB."""

from __future__ import annotations

from os import environ
from pathlib import Path

from scinoephile.audio.transcription import VADMode
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Language
from scinoephile.lang.transcription import (
    BlockDelineationMode,
    BlockPunctuationMode,
    MlxAudioTimingMode,
    TranscriptionAlignmentMode,
)
from test.data.ocr import process_ocr
from test.data.stacking import process_yue_hans_eng, process_zho_hans_eng
from test.data.transcription import process_transcription_pipeline
from test.helpers import test_data_root

title_root = test_data_root / Path(__file__).parent.name
output_path = title_root / "output"
eng_ocr_path = output_path / "eng_ocr"
yue_hans_ocr_path = output_path / "yue-Hans_ocr"
yue_hant_ocr_path = output_path / "yue-Hant_ocr"
yue_hant_transcribe_path = output_path / "yue-Hant_transcribe"
yue_hant_transcribe_vad_off_path = yue_hant_transcribe_path / "vad-off"
yue_hant_transcribe_vad_off_stripped_punctuation_path = (
    yue_hant_transcribe_path / "vad-off-stripped-punctuation"
)
yue_hant_transcribe_vad_off_phrase_timing_stripped_punctuation_path = (
    yue_hant_transcribe_path / "vad-off-phrase-timing-stripped-punctuation"
)
yue_hant_transcribe_vad_off_phrase_timing_block_positional_path = (
    yue_hant_transcribe_path / "vad-off-phrase-timing-block-positional"
)
yue_hant_transcribe_vad_off_phrase_timing_advisory_delineation_path = (
    yue_hant_transcribe_path / "vad-off-phrase-timing-advisory-delineation"
)
yue_hant_transcribe_vad_off_phrase_timing_gated_advisory_delineation_path = (
    yue_hant_transcribe_path / "vad-off-phrase-timing-gated-advisory-delineation"
)
yue_hant_transcribe_vad_off_phrase_timing_pairwise_path = (
    yue_hant_transcribe_path / "vad-off-phrase-timing-pairwise"
)
yue_hant_transcribe_vad_off_phrase_timing_candidate_delineation_path = (
    yue_hant_transcribe_path / "vad-off-phrase-timing-candidate-delineation"
)
yue_hant_transcribe_vad_off_phrase_timing_positional_punctuation_path = (
    yue_hant_transcribe_path / "vad-off-phrase-timing-positional-punctuation"
)
yue_hant_transcribe_vad_auto_phrase_timing_stripped_punctuation_path = (
    yue_hant_transcribe_path / "vad-auto-phrase-timing-stripped-punctuation"
)
yue_hant_transcribe_vad_auto_phrase_timing_gated_advisory_delineation_path = (
    yue_hant_transcribe_path / "vad-auto-phrase-timing-gated-advisory-delineation"
)
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

selected_transcription_name = environ.get("SCINOEPHILE_TRANSCRIPTION_NAME")
if selected_transcription_name is None:
    transcription_names = ("whisper", "mimo", "qwen")
elif selected_transcription_name in {"whisper", "mimo", "qwen"}:
    transcription_names = (selected_transcription_name,)
else:
    raise ValueError("SCINOEPHILE_TRANSCRIPTION_NAME must be whisper, mimo, or qwen")

actions = {
    # "eng_ocr",
    # "yue-Hans_ocr",
    # "yue-Hant_ocr",
    # "zho-Hans_ocr",
    # "zho-Hant_ocr",
    # "yue-Hans_eng",
    # "zho-Hans_eng",
    "yue-Hant_transcribe_vad_auto_phrase_timing",
    # "yue-Hant_transcribe_advisory_delineation",
    "yue-Hant_transcribe_vad_auto_gated_advisory_delineation",
    # "yue-Hant_transcribe_pairwise",
    # "yue-Hant_transcribe_candidate_delineation",
    # "yue-Hant_transcribe_positional_punctuation",
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
    process_transcription_pipeline(
        title_root,
        zho_hant_guide_path,
        reference_path=yue_hant_ocr_path / "fuse_clean_validate_review_flatten.srt",
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        output_dir_path=yue_hant_transcribe_vad_off_path,
        audio_dir_path=yue_hant_transcribe_path / "audio",
        additional_context=transcription_additional_context,
        transcription_no_op=False,
        transcription_alignment_mode=TranscriptionAlignmentMode.BLOCK,
        transcription_fallback_to_no_op=True,
        vad_mode=VADMode.OFF,
        transcription_overwrite=True,
        run_merge_and_translation=True,
        overwrite=True,
    )
if "yue-Hant_transcribe_strip_punctuation" in actions:
    process_transcription_pipeline(
        title_root,
        zho_hant_guide_path,
        reference_path=yue_hant_ocr_path / "fuse_clean_validate_review_flatten.srt",
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        output_dir_path=yue_hant_transcribe_vad_off_stripped_punctuation_path,
        audio_dir_path=yue_hant_transcribe_path / "audio",
        additional_context=transcription_additional_context,
        transcription_no_op=False,
        transcription_alignment_mode=TranscriptionAlignmentMode.BLOCK,
        transcription_fallback_to_no_op=True,
        strip_mlx_audio_punctuation=True,
        vad_mode=VADMode.OFF,
        stop_at_idx=20,
        transcription_names=("mimo", "qwen"),
        transcription_overwrite=True,
        run_merge_and_translation=False,
        overwrite=True,
    )
if "yue-Hant_transcribe_phrase_timing" in actions:
    process_transcription_pipeline(
        title_root,
        zho_hant_guide_path,
        reference_path=yue_hant_ocr_path / "fuse_clean_validate_review_flatten.srt",
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        output_dir_path=(
            yue_hant_transcribe_vad_off_phrase_timing_stripped_punctuation_path
        ),
        audio_dir_path=yue_hant_transcribe_path / "audio",
        additional_context=transcription_additional_context,
        transcription_no_op=False,
        transcription_alignment_mode=TranscriptionAlignmentMode.BLOCK,
        transcription_fallback_to_no_op=True,
        strip_mlx_audio_punctuation=True,
        mlx_audio_timing_mode=MlxAudioTimingMode.PHRASE,
        vad_mode=VADMode.OFF,
        transcription_names=transcription_names,
        transcription_overwrite=True,
        run_merge_and_translation=False,
        overwrite=True,
    )
if "yue-Hant_transcribe_block_positional" in actions:
    process_transcription_pipeline(
        title_root,
        zho_hant_guide_path,
        reference_path=yue_hant_ocr_path / "fuse_clean_validate_review_flatten.srt",
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        output_dir_path=yue_hant_transcribe_vad_off_phrase_timing_block_positional_path,
        audio_dir_path=yue_hant_transcribe_path / "audio",
        additional_context=transcription_additional_context,
        transcription_no_op=False,
        transcription_alignment_mode=TranscriptionAlignmentMode.BLOCK_POSITIONAL,
        transcription_fallback_to_no_op=True,
        mlx_audio_timing_mode=MlxAudioTimingMode.PHRASE,
        vad_mode=VADMode.OFF,
        stop_at_idx=20,
        transcription_names=("mimo", "qwen"),
        transcription_overwrite=True,
        run_merge_and_translation=False,
        overwrite=True,
    )
if "yue-Hant_transcribe_advisory_delineation" in actions:
    process_transcription_pipeline(
        title_root,
        zho_hant_guide_path,
        reference_path=yue_hant_ocr_path / "fuse_clean_validate_review_flatten.srt",
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        output_dir_path=(
            yue_hant_transcribe_vad_off_phrase_timing_advisory_delineation_path
        ),
        audio_dir_path=yue_hant_transcribe_path / "audio",
        additional_context=transcription_additional_context,
        transcription_no_op=False,
        transcription_alignment_mode=TranscriptionAlignmentMode.BLOCK,
        transcription_block_delineation_mode=BlockDelineationMode.ADVISORY,
        transcription_fallback_to_no_op=True,
        strip_mlx_audio_punctuation=True,
        mlx_audio_timing_mode=MlxAudioTimingMode.PHRASE,
        vad_mode=VADMode.OFF,
        stop_at_idx=20,
        transcription_names=("mimo", "qwen"),
        transcription_overwrite=True,
        run_merge_and_translation=False,
        overwrite=True,
    )
if "yue-Hant_transcribe_gated_advisory_delineation" in actions:
    process_transcription_pipeline(
        title_root,
        zho_hant_guide_path,
        reference_path=yue_hant_ocr_path / "fuse_clean_validate_review_flatten.srt",
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        output_dir_path=(
            yue_hant_transcribe_vad_off_phrase_timing_gated_advisory_delineation_path
        ),
        audio_dir_path=yue_hant_transcribe_path / "audio",
        additional_context=transcription_additional_context,
        transcription_no_op=False,
        transcription_alignment_mode=TranscriptionAlignmentMode.BLOCK,
        transcription_block_delineation_mode=BlockDelineationMode.GATED_ADVISORY,
        transcription_fallback_to_no_op=True,
        strip_mlx_audio_punctuation=True,
        mlx_audio_timing_mode=MlxAudioTimingMode.PHRASE,
        vad_mode=VADMode.OFF,
        transcription_names=transcription_names,
        transcription_overwrite=True,
        run_merge_and_translation=False,
        overwrite=True,
    )
if "yue-Hant_transcribe_vad_auto_phrase_timing" in actions:
    process_transcription_pipeline(
        title_root,
        zho_hant_guide_path,
        reference_path=yue_hant_ocr_path / "fuse_clean_validate_review_flatten.srt",
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        output_dir_path=(
            yue_hant_transcribe_vad_auto_phrase_timing_stripped_punctuation_path
        ),
        audio_dir_path=yue_hant_transcribe_path / "audio",
        additional_context=transcription_additional_context,
        transcription_no_op=False,
        transcription_alignment_mode=TranscriptionAlignmentMode.BLOCK,
        transcription_fallback_to_no_op=True,
        strip_mlx_audio_punctuation=True,
        mlx_audio_timing_mode=MlxAudioTimingMode.PHRASE,
        vad_mode=VADMode.AUTO,
        transcription_names=transcription_names,
        transcription_overwrite=True,
        run_merge_and_translation=False,
        overwrite=True,
    )
if "yue-Hant_transcribe_vad_auto_gated_advisory_delineation" in actions:
    process_transcription_pipeline(
        title_root,
        zho_hant_guide_path,
        reference_path=yue_hant_ocr_path / "fuse_clean_validate_review_flatten.srt",
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        output_dir_path=(
            yue_hant_transcribe_vad_auto_phrase_timing_gated_advisory_delineation_path
        ),
        audio_dir_path=yue_hant_transcribe_path / "audio",
        additional_context=transcription_additional_context,
        transcription_no_op=False,
        transcription_alignment_mode=TranscriptionAlignmentMode.BLOCK,
        transcription_block_delineation_mode=BlockDelineationMode.GATED_ADVISORY,
        transcription_fallback_to_no_op=True,
        strip_mlx_audio_punctuation=True,
        mlx_audio_timing_mode=MlxAudioTimingMode.PHRASE,
        vad_mode=VADMode.AUTO,
        transcription_names=transcription_names,
        transcription_overwrite=True,
        run_merge_and_translation=False,
        overwrite=True,
    )
if "yue-Hant_transcribe_pairwise" in actions:
    process_transcription_pipeline(
        title_root,
        zho_hant_guide_path,
        reference_path=yue_hant_ocr_path / "fuse_clean_validate_review_flatten.srt",
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        output_dir_path=yue_hant_transcribe_vad_off_phrase_timing_pairwise_path,
        audio_dir_path=yue_hant_transcribe_path / "audio",
        additional_context=transcription_additional_context,
        transcription_no_op=False,
        transcription_alignment_mode=TranscriptionAlignmentMode.PAIRWISE,
        strip_mlx_audio_punctuation=True,
        mlx_audio_timing_mode=MlxAudioTimingMode.PHRASE,
        vad_mode=VADMode.OFF,
        stop_at_idx=20,
        transcription_names=("mimo", "qwen"),
        transcription_overwrite=True,
        run_merge_and_translation=False,
        overwrite=True,
    )
if "yue-Hant_transcribe_candidate_delineation" in actions:
    process_transcription_pipeline(
        title_root,
        zho_hant_guide_path,
        reference_path=yue_hant_ocr_path / "fuse_clean_validate_review_flatten.srt",
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        output_dir_path=(
            yue_hant_transcribe_vad_off_phrase_timing_candidate_delineation_path
        ),
        audio_dir_path=yue_hant_transcribe_path / "audio",
        additional_context=transcription_additional_context,
        transcription_no_op=False,
        transcription_alignment_mode=TranscriptionAlignmentMode.BLOCK,
        transcription_block_delineation_mode=BlockDelineationMode.CANDIDATE,
        transcription_fallback_to_no_op=True,
        strip_mlx_audio_punctuation=True,
        mlx_audio_timing_mode=MlxAudioTimingMode.PHRASE,
        vad_mode=VADMode.OFF,
        stop_at_idx=20,
        transcription_names=("mimo", "qwen"),
        transcription_overwrite=True,
        run_merge_and_translation=False,
        overwrite=True,
    )
if "yue-Hant_transcribe_positional_punctuation" in actions:
    process_transcription_pipeline(
        title_root,
        zho_hant_guide_path,
        reference_path=yue_hant_ocr_path / "fuse_clean_validate_review_flatten.srt",
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        output_dir_path=(
            yue_hant_transcribe_vad_off_phrase_timing_positional_punctuation_path
        ),
        audio_dir_path=yue_hant_transcribe_path / "audio",
        additional_context=transcription_additional_context,
        transcription_no_op=False,
        transcription_alignment_mode=TranscriptionAlignmentMode.BLOCK,
        transcription_block_punctuation_mode=BlockPunctuationMode.POSITIONAL,
        transcription_fallback_to_no_op=True,
        strip_mlx_audio_punctuation=True,
        mlx_audio_timing_mode=MlxAudioTimingMode.PHRASE,
        vad_mode=VADMode.OFF,
        stop_at_idx=20,
        transcription_names=("mimo", "qwen"),
        transcription_overwrite=True,
        run_merge_and_translation=False,
        overwrite=True,
    )
