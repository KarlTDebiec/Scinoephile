#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MLAMD."""
from __future__ import annotations

from pathlib import Path

from scinoephile.common import package_root
from scinoephile.common.logging import set_logging_verbosity
from scinoephile.core.hanzi import get_hanzi_simplified
from scinoephile.image import ImageSeries
from scinoephile.openai import OpenAiService
from scinoephile.testing.file import get_test_file_path

if __name__ == "__main__":

    def get_output_path(relative_path: str) -> Path:
        return package_root.parent / "test" / "data" / Path(relative_path)

    set_logging_verbosity(2)
    openai_service = OpenAiService()

    # Simplified Standard Chinese
    # cmn_hans_hk = ImageSeries.load(get_test_file_path("mlamd/input/cmn-Hans-HK.sup"))
    # cmn_hans_hk.save(get_output_path("mlamd/output/cmn-Hans-HK"))
    cmn_hans_hk = ImageSeries.load(get_test_file_path("mlamd/output/cmn-Hans-HK"))
    cmn_hans_hk_simplify = get_hanzi_simplified(cmn_hans_hk)
    cmn_hans_hk_simplify.save(get_output_path("mlamd/output/cmn-Hans-HK"))
    # cmn_hans_hk = get_transcriptions(
    #     openai_service,
    #     cmn_hans_hk,
    #     upscale=True,
    #     language="Simplified Chinese, specifically Standard Chinese, Hong Kong",
    # )
    # cmn_hans_hk.save(get_output_path("mlamd/output/cmn-Hans-HK"))

    # Traditional Standard Chinese
    # cmn_hant_hk = ImageSeries.load(get_test_file_path("mlamd/input/cmn-Hant-HK.sup"))
    # cmn_hant_hk.save(get_output_path("mlamd/output/cmn-Hant-HK"))
    # cmn_hant_hk = ImageSeries.load(get_test_file_path("mlamd/output/cmn-Hant-HK"))
    # cmn_hant_hk = get_transcriptions(
    #     openai_service,
    #     cmn_hant_hk,
    #     upscale=True,
    #     language="Traditional Chinese, specifically Standard Chinese, Hong Kong",
    # )
    # cmn_hant_hk.save(get_output_path("mlamd/output/cmn-Hant-HK"))

    # Simplified and Traditional Chinese Together
    # cmn_hans_hk, cmn_hant_hk = get_revised_chinese_transcriptions(
    #     openai_service, cmn_hans_hk, cmn_hant_hk
    # )
    # cmn_hans_hk.save(get_output_path("mlamd/output/cmn-Hans-HK"))
    # cmn_hant_hk.save(get_output_path("mlamd/output/cmn-Hant-HK"))

    # English
    # en_hk = ImageSeries.load(get_test_file_path("mlamd/input/en-HK.sup"))
    # en_hk.save(get_output_path("mlamd/output/en-HK"))
    # en_hk = ImageSeries.load(get_test_file_path("mlamd/output/en-HK"))
    # en_hk = get_transcriptions(openai_service, en_hk)
    # en_hk.save(get_output_path("mlamd/output/en-HK"))
