#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MLAMD."""
from __future__ import annotations

from pathlib import Path

from scinoephile.common import package_root
from scinoephile.common.logging import set_logging_verbosity
from scinoephile.core.synchronization import get_synced_series
from scinoephile.image import ImageSeries
from scinoephile.openai import OpenAiService
from scinoephile.testing.file import get_test_file_path

if __name__ == "__main__":

    def get_output_path(relative_path: str) -> Path:
        return package_root.parent / "test" / "data" / Path(relative_path)

    set_logging_verbosity(2)
    openai_service = OpenAiService()

    # Simplified Standard Chinese
    # cmn_hans = ImageSeries.load(get_test_file_path("mlamd/input/cmn-Hans.sup"))
    # cmn_hans.save(get_output_path("mlamd/output/cmn-Hans"))
    cmn_hans = ImageSeries.load(get_test_file_path("mlamd/output/cmn-Hans"))
    # cmn_hans_simplify = get_hanzi_simplified(cmn_hans)
    # cmn_hans_simplify.save(get_output_path("mlamd/output/cmn-Hans"))
    # cmn_hans_text = Series.load(
    #     get_output_path("mlamd/output/cmn-Hans/cmn-Hans.srt")
    # )
    # cmn_hans_text_traditionalize = get_hanzi_traditionalized(cmn_hans_text)
    # cmn_hans_text_traditionalize.save(
    #     get_output_path("mlamd/output/cmn-Hant/cmn-Hant.srt")
    # )
    # cmn_hans = get_transcriptions(
    #     openai_service,
    #     cmn_hans,
    #     upscale=True,
    #     language="Simplified Chinese, specifically Standard Chinese, Hong Kong",
    # )
    # cmn_hans.save(get_output_path("mlamd/output/cmn-Hans"))

    # Traditional Standard Chinese
    # cmn_hant = ImageSeries.load(get_test_file_path("mlamd/input/cmn-Hant.sup"))
    # cmn_hant.save(get_output_path("mlamd/output/cmn-Hant"))
    # cmn_hant = ImageSeries.load(get_test_file_path("mlamd/output/cmn-Hant"))
    # cmn_hant = get_transcriptions(
    #     openai_service,
    #     cmn_hant,
    #     upscale=True,
    #     language="Traditional Chinese, specifically Standard Chinese, Hong Kong",
    # )
    # cmn_hant.save(get_output_path("mlamd/output/cmn-Hant"))

    # Simplified and Traditional Chinese Together
    # cmn_hans, cmn_hant = get_revised_chinese_transcriptions(
    #     openai_service, cmn_hans, cmn_hant
    # )
    # cmn_hans.save(get_output_path("mlamd/output/cmn-Hans"))
    # cmn_hant.save(get_output_path("mlamd/output/cmn-Hant"))

    # English
    # eng = ImageSeries.load(get_test_file_path("mlamd/input/eng.sup"))
    # eng.save(get_output_path("mlamd/output/eng"))
    eng = ImageSeries.load(get_test_file_path("mlamd/output/eng"))
    # eng = get_transcriptions(openai_service, eng)
    # eng.save(get_output_path("mlamd/output/eng"))

    # Bilingual Simplified Standard Chinese and English
    cmn_hans_eng = get_synced_series(cmn_hans, eng)
    cmn_hans_eng.save(get_output_path("mlamd/output/cmn-Hans_eng.srt"))
