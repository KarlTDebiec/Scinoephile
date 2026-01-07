#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Functions for processing OCRed subtitles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scinoephile.core.subtitles import Series
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng import get_eng_cleaned, get_eng_flattened, validate_eng_ocr
from scinoephile.lang.eng.ocr_fusion import get_eng_ocr_fused, get_eng_ocr_fuser
from scinoephile.lang.zho import (
    get_zho_cleaned,
    get_zho_converted,
    get_zho_flattened,
    get_zho_ocr_fused,
    validate_zho_ocr,
)
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.lang.zho.ocr_fusion import ZhoHantOcrFusionPrompt, get_zho_ocr_fuser
from scinoephile.multilang.synchronization import get_synced_series

__all__ = [
    "process_eng_ocr",
    "process_zho_hans_ocr",
    "process_zho_hans_eng",
    "process_zho_hant_ocr",
]


def process_eng_ocr(
    title_root: Path,
    sup_path: Path,
    fuser_kw: Any | None = None,
    overwrite_srt: bool = False,
    overwrite_img: bool = False,
    validate: bool = True,
) -> Series:
    input_dir = title_root / "input"
    output_dir = title_root / "output"

    # Fuse
    fuse_path = output_dir / "eng_fuse.srt"
    if fuse_path.exists() and not overwrite_srt:
        fuse = Series.load(fuse_path)
    else:
        # Lens
        lens_path = input_dir / "eng_lens.srt"
        lens = Series.load(lens_path)
        lens = get_eng_cleaned(lens, remove_empty=False)
        lens.save(lens_path)

        # Tesseract
        tesseract_path = input_dir / "eng_tesseract.srt"
        tesseract = Series.load(tesseract_path)
        tesseract = get_eng_cleaned(tesseract, remove_empty=False)
        tesseract.save(tesseract_path)

        if fuser_kw is None:
            fuser_kw = {}
        fuser = get_eng_ocr_fuser(
            test_case_path=title_root / "lang" / "eng" / "ocr_fusion.json",
            auto_verify=True,
            **fuser_kw,
        )
        fuse = get_eng_ocr_fused(lens, tesseract, fuser)
        fuse.save(fuse_path)

    # Clean
    clean_path = output_dir / "eng_fuse_clean.srt"
    if clean_path.exists() and not overwrite_srt:
        fuse_clean = Series.load(clean_path)
    else:
        fuse_clean = get_eng_cleaned(fuse, remove_empty=False)
        fuse_clean.save(output_dir / "eng_fuse_clean.srt")

    # Image
    image_path = output_dir / "eng_image"
    if image_path.exists() and not overwrite_img:
        image = ImageSeries.load(image_path)
    else:
        image = ImageSeries.load(sup_path)
        assert len(fuse_clean) == len(image), (
            f"Length mismatch: {len(fuse_clean)} vs {len(image)}"
        )
        for text_sub, image_sub in zip(fuse_clean, image):
            image_sub.text = text_sub.text
        image.save(image_path)

    # Validate
    fuse_clean_validate_path = output_dir / "eng_fuse_clean_validate.srt"
    if fuse_clean_validate_path.exists() and not overwrite_img and not validate:
        fuse_clean_validate = Series.load(fuse_clean_validate_path)
    else:
        validation_path = output_dir / "eng_validation"
        fuse_clean_validate = validate_eng_ocr(
            image,
            output_dir_path=validation_path,
            interactive=True,
        )
        fuse_clean_validate.save(fuse_clean_validate_path, exist_ok=True)

    return fuse_clean_validate

    # Proofread
    # eng_proofreader = get_eng_proofreader(
    #     test_cases=get_kob_eng_proofreading_test_cases()
    #     + get_mnt_eng_proofreading_test_cases()
    #     + get_t_eng_proofreading_test_cases(),
    #     test_case_path=title_root / "lang" / "eng" / "proofreading.json",
    #     auto_verify=True,
    # )
    # eng_fuse_proofread = get_eng_proofread(eng_fuse, eng_proofreader)
    # eng_fuse_proofread.save(output_dir / "eng_fuse_proofread.srt")


def process_zho_hans_ocr(
    title_root: Path,
    sup_path: Path,
    fuser_kw: Any | None = None,
    overwrite_srt: bool = False,
    overwrite_img: bool = False,
    validate: bool = True,
) -> Series:
    input_dir = title_root / "input"
    output_dir = title_root / "output"

    # Fuse
    fuse_path = output_dir / "zho-Hans_fuse.srt"
    if fuse_path.exists() and not overwrite_srt:
        fuse = Series.load(fuse_path)
    else:
        # Lens
        lens_path = input_dir / "zho-Hans_lens.srt"
        lens = Series.load(lens_path)
        lens = get_zho_cleaned(lens, remove_empty=False)
        lens = get_zho_converted(lens)
        lens.save(lens_path)

        # Paddle
        paddle_path = input_dir / "zho-Hans_paddle.srt"
        paddle = Series.load(paddle_path)
        paddle = get_zho_cleaned(paddle, remove_empty=False)
        paddle = get_zho_converted(paddle)
        paddle.save(paddle_path)

        if fuser_kw is None:
            fuser_kw = {}
        fuser = get_zho_ocr_fuser(
            test_case_path=title_root / "lang" / "zho" / "ocr_fusion" / "zho-Hans.json",
            auto_verify=True,
            **fuser_kw,
        )
        fuse = get_zho_ocr_fused(lens, paddle, fuser)
        fuse.save(fuse_path)

    # Clean
    fuse_clean_path = output_dir / "zho-Hans_fuse_clean.srt"
    if fuse_clean_path.exists() and not overwrite_srt:
        fuse_clean = Series.load(fuse_clean_path)
    else:
        fuse_clean = get_zho_cleaned(fuse, remove_empty=False)
        fuse_clean = get_zho_converted(fuse_clean)
        fuse_clean.save(fuse_clean_path)

    # Image
    image_path = output_dir / "zho-Hans_image"
    if image_path.exists() and not overwrite_img:
        image = ImageSeries.load(image_path)
    else:
        image = ImageSeries.load(sup_path)
        assert len(fuse_clean) == len(image), (
            f"Length mismatch: {len(fuse_clean)} vs {len(image)}"
        )
        for text_sub, image_sub in zip(fuse_clean, image):
            image_sub.text = text_sub.text
        image.save(image_path)

    # Validate
    fuse_clean_validate_path = output_dir / "zho-Hans_fuse_clean_validate.srt"
    if fuse_clean_validate_path.exists() and not overwrite_img and not validate:
        fuse_clean_validate = Series.load(fuse_clean_validate_path)
    else:
        validation_path = output_dir / "zho-Hans_validation"
        fuse_clean_validate = validate_zho_ocr(
            image,
            output_dir_path=validation_path,
            interactive=True,
        )
        fuse_clean_validate.save(fuse_clean_validate_path, exist_ok=True)

    return fuse_clean_validate

    # Proofread
    # zho_proofreader = get_zho_proofreader(
    #     test_cases=get_kob_zho_proofreading_test_cases()
    #     + get_mnt_zho_proofreading_test_cases()
    #     + get_t_zho_proofreading_test_cases(),
    #     test_case_path=title_root / "lang" / "zho" / "proofreading.json",
    #     auto_verify=True,
    # )
    # zho_hans_fuse_proofread = get_zho_proofread(zho_hans_fuse, zho_proofreader)
    # zho_hans_fuse_proofread.save(output_dir / "zho-Hans_fuse_proofread.srt")


def process_zho_hant_ocr(
    title_root: Path,
    sup_path: Path,
    fuser_kw: Any | None = None,
    overwrite_srt: bool = False,
    overwrite_img: bool = False,
    validate: bool = True,
) -> Series:
    input_dir = title_root / "input"
    output_dir = title_root / "output"

    # Fuse
    fuse_path = output_dir / "zho-Hant_fuse.srt"
    if fuse_path.exists():
        fuse = Series.load(fuse_path)
    else:
        # Lens
        lens_path = input_dir / "zho-Hant_lens.srt"
        lens = Series.load(lens_path)
        lens = get_zho_cleaned(lens, remove_empty=False)
        lens = get_zho_converted(lens, OpenCCConfig.s2t)
        lens.save(lens_path)

        # PaddleOCR
        paddle_path = input_dir / "zho-Hant_paddle.srt"
        paddle = Series.load(paddle_path)
        paddle = get_zho_cleaned(paddle, remove_empty=False)
        paddle = get_zho_converted(paddle, OpenCCConfig.s2t)
        paddle.save(paddle_path)

        fuser = get_zho_ocr_fuser(
            prompt_cls=ZhoHantOcrFusionPrompt,
            test_case_path=title_root / "lang" / "zho" / "ocr_fusion" / "zho-Hant.json",
            auto_verify=True,
            **fuser_kw,
        )
        fuse = get_zho_ocr_fused(lens, paddle, fuser)
        fuse.save(fuse_path)

    # Clean
    fuse_clean_path = output_dir / "zho-Hant_fuse_clean.srt"
    if fuse_clean_path.exists() and not overwrite_srt:
        fuse_clean = Series.load(fuse_clean_path)
    else:
        fuse_clean = get_zho_cleaned(fuse, remove_empty=False)
        fuse_clean = get_zho_converted(fuse_clean, OpenCCConfig.s2t)
        fuse_clean.save(output_dir / "zho-Hant_fuse_clean.srt")

    # Image
    image_path = output_dir / "zho-Hant_image"
    if image_path.exists() and not overwrite_img:
        image = ImageSeries.load(image_path)
    else:
        image = ImageSeries.load(sup_path)
        assert len(fuse_clean) == len(image), (
            f"Length mismatch: {len(fuse_clean)} vs {len(image)}"
        )
        for text_sub, image_sub in zip(fuse_clean, image):
            image_sub.text = text_sub.text
        image.save(image_path)

    # Validate
    fuse_clean_validate_path = output_dir / "zho-Hant_fuse_clean_validate.srt"
    if fuse_clean_validate_path.exists() and not overwrite_img and not validate:
        fuse_clean_validate = Series.load(fuse_clean_validate_path)
    else:
        validation_path = output_dir / "zho-Hant_validation"
        fuse_clean_validate = validate_zho_ocr(
            image,
            output_dir_path=validation_path,
            interactive=True,
        )
        fuse_clean_validate.save(fuse_clean_validate_path, exist_ok=True)

    # Flatten
    fuse_clean_validate_flatten_path = (
        output_dir / "zho-Hant_fuse_clean_validate_flatten.srt"
    )
    if fuse_clean_validate_flatten_path.exists() and not overwrite_srt:
        fuse_clean_validate_flatten = Series.load(fuse_clean_validate_flatten_path)
    else:
        fuse_clean_validate_flatten = get_zho_flattened(fuse_clean_validate)
        fuse_clean_validate_flatten.save(
            fuse_clean_validate_flatten_path, exist_ok=True
        )

    return fuse_clean_validate_flatten


def process_zho_hans_eng(
    title_root: Path,
    zho_hans_path: Path | None = None,
    eng_path: Path | None = None,
    overwrite: bool = False,
) -> Series:
    output_dir = title_root / "output"

    zho_hans_eng_path = output_dir / "zho-Hans_eng.srt"
    if zho_hans_eng_path.exists() and not overwrite:
        zho_hans_eng = Series.load(zho_hans_eng_path)
    else:
        if zho_hans_path is None:
            zho_hans_path = output_dir / "zho-Hans.srt"
        zho_hans = Series.load(zho_hans_path)
        zho_hans = get_zho_flattened(zho_hans)

        if eng_path is None:
            eng_path = output_dir / "eng.srt"
        eng = Series.load(eng_path)
        eng = get_eng_flattened(eng)

        zho_hans_eng = get_synced_series(zho_hans, eng)
        zho_hans_eng.save(output_dir / "zho-Hans_eng.srt")

    return zho_hans_eng
