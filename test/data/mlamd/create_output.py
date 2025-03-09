#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for creating expected test output for MLAMD."""
from __future__ import annotations

from scinoephile.common import package_root
from scinoephile.common.logging import set_logging_verbosity
from scinoephile.image import ImageSeries
from scinoephile.image.validation import validate_ocr_hanzi

if __name__ == "__main__":
    data_root = package_root.parent / "test" / "data"

    set_logging_verbosity(2)

    # Simplified Standard Chinese
    # zho_hans = ImageSeries.load(data_root / "mlamd" / "input" / "cmn-Hans.sup")
    # zho_hans.save(data_root / "mlamd" / "output" / "cmn-Hans")

    # zho_hans = ImageSeries.load(data_root / "mlamd" / "output" / "cmn-Hans")
    # zho_hans = get_hanzi_cleaned(zho_hans)
    # zho_hans = get_hanzi_flattened(zho_hans)
    # zho_hans.save(data_root / "mlamd" / "output" / "cmn-Hans" / "cmn-Hans.srt")

    zho_hans = ImageSeries.load(data_root / "mlamd" / "output" / "cmn-Hans")
    validate_ocr_hanzi(
        zho_hans,
        data_root / "mlamd" / "output" / "cmn-Hans_validation",
    )

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
    # eng = ImageSeries.load(get_test_file_path("mlamd/output/eng"))
    # eng = get_transcriptions(openai_service, eng)
    # eng.save(get_output_path("mlamd/output/eng"))

    # Bilingual Simplified Standard Chinese and English
    # cmn_hans_eng = get_synced_series(zho_hans, eng)
    # cmn_hans_eng.save(get_output_path("mlamd/output/cmn-Hans_eng.srt"))
