#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Functions for processing OCRed subtitles."""

from __future__ import annotations

from logging import info
from pathlib import Path
from typing import Any

from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.cmn import get_cmn_romanized
from scinoephile.lang.eng import (
    get_eng_cleaned,
    get_eng_flattened,
    validate_eng_ocr,
)
from scinoephile.lang.eng.ocr_fusion import get_eng_ocr_fused, get_eng_ocr_fuser
from scinoephile.lang.eng.proofreading import get_eng_proofread, get_eng_proofreader
from scinoephile.lang.zho import (
    get_zho_cleaned,
    get_zho_converted,
    get_zho_flattened,
    get_zho_ocr_fused,
    validate_zho_ocr,
)
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.lang.zho.ocr_fusion import ZhoHantOcrFusionPrompt, get_zho_ocr_fuser
from scinoephile.lang.zho.proofreading import (
    ZhoHansProofreadingPrompt,
    ZhoHantProofreadingPrompt,
    get_zho_proofread,
    get_zho_proofreader,
)

__all__ = [
    "process_eng_ocr",
    "process_zho_hans_ocr",
    "process_zho_hant_ocr",
]


def process_eng_ocr(  # noqa: PLR0912, PLR0915
    title_root: Path,
    sup_path: Path | None = None,
    *,
    fuser_kw: Any | None = None,
    proofreader_kw: Any | None = None,
    overwrite_srt: bool = False,
    overwrite_img: bool = False,
    force_validation: bool = False,
) -> Series:
    """Process English OCR subtitles into validated output.

    Arguments:
        title_root: title root directory
        sup_path: subtitle image input path
        fuser_kw: keyword arguments for OCR fuser
        proofreader_kw: keyword arguments for OCR proofreader
        overwrite_srt: whether to overwrite subtitle outputs
        overwrite_img: whether to overwrite image outputs
        force_validation: whether to rerun validation if output exists
    Returns:
        processed series
    """
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
        fuser_kw.setdefault(
            "test_case_path",
            title_root / "lang" / "eng" / "ocr_fusion.json",
        )
        fuser = get_eng_ocr_fuser(
            auto_verify=True,
            **fuser_kw,
        )
        fuse = get_eng_ocr_fused(lens, tesseract, fuser)
        fuse.save(fuse_path)

    # Clean
    clean_path = output_dir / "eng_fuse_clean.srt"
    if clean_path.exists() and not overwrite_srt:
        clean = Series.load(clean_path)
    else:
        clean = get_eng_cleaned(fuse, remove_empty=False)
        clean.save(output_dir / "eng_fuse_clean.srt")

    # Validate
    validate_path = output_dir / "eng_fuse_clean_validate.srt"
    if validate_path.exists() and not force_validation:
        validate = Series.load(validate_path)
    else:
        image_path = output_dir / "eng_image"
        if image_path.exists() and not overwrite_img:
            image = ImageSeries.load(image_path)
            if not any(sub.text for sub in image):
                info("Copying OCRed text into image subtitles")
                assert len(clean) == len(image), (
                    f"Length mismatch: {len(clean)} vs {len(image)}"
                )
                for text_sub, image_sub in zip(clean, image):
                    image_sub.text = text_sub.text
                image.save(image_path)
        else:
            if not sup_path:
                raise ScinoephileError("sup_path is required to build image output")
            image = ImageSeries.load(sup_path)
            assert len(clean) == len(image), (
                f"Length mismatch: {len(clean)} vs {len(image)}"
            )
            for text_sub, image_sub in zip(clean, image):
                image_sub.text = text_sub.text
            image.save(image_path)
        image_validation_path = output_dir / "eng_validation"
        validate = validate_eng_ocr(
            image,
            output_dir_path=image_validation_path,
            interactive=True,
        )
        validate.save(validate_path, exist_ok=True)
        validate = Series.load(validate_path)

    # Proofread
    proofread_path = output_dir / "eng_fuse_clean_validate_proofread.srt"
    if proofread_path.exists() and not overwrite_srt:
        proofread = Series.load(proofread_path)
    else:
        if proofreader_kw is None:
            proofreader_kw = {}
        proofreader_kw.setdefault(
            "test_case_path",
            title_root / "lang" / "eng" / "proofreading.json",
        )
        proofreader = get_eng_proofreader(
            auto_verify=True,
            **proofreader_kw,
        )
        proofread = get_eng_proofread(validate, proofreader)
        proofread.save(proofread_path)

    # Flatten
    flatten_path = output_dir / "eng_fuse_clean_validate_proofread_flatten.srt"
    if flatten_path.exists() and not overwrite_srt:
        flatten = Series.load(flatten_path)
    else:
        flatten = get_eng_flattened(proofread)
        flatten.save(flatten_path, exist_ok=True)

    return flatten


def process_zho_hans_ocr(  # noqa: PLR0912, PLR0915
    title_root: Path,
    sup_path: Path | None = None,
    *,
    fuser_kw: Any | None = None,
    proofreader_kw: Any | None = None,
    overwrite_srt: bool = False,
    overwrite_img: bool = False,
    force_validation: bool = False,
) -> Series:
    """Process 简体中文 OCR subtitles into validated output.

    Arguments:
        title_root: title root directory
        sup_path: subtitle image input path
        fuser_kw: keyword arguments for OCR fuser
        proofreader_kw: keyword arguments for OCR proofreader
        overwrite_srt: whether to overwrite subtitle outputs
        overwrite_img: whether to overwrite image outputs
        force_validation: whether to force validation even if validation output exists
    Returns:
        processed series
    """
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
        fuser_kw.setdefault(
            "test_case_path",
            title_root / "lang" / "zho" / "ocr_fusion" / "zho-Hans.json",
        )
        fuser = get_zho_ocr_fuser(
            auto_verify=True,
            **fuser_kw,
        )
        fuse = get_zho_ocr_fused(lens, paddle, fuser)
        fuse.save(fuse_path)

    # Clean
    clean_path = output_dir / "zho-Hans_fuse_clean.srt"
    if clean_path.exists() and not overwrite_srt:
        clean = Series.load(clean_path)
    else:
        clean = get_zho_cleaned(fuse, remove_empty=False)
        clean = get_zho_converted(clean)
        clean.save(clean_path)

    # Validate
    validate_path = output_dir / "zho-Hans_fuse_clean_validate.srt"
    if validate_path.exists() and not force_validation:
        validate = Series.load(validate_path)
    else:
        image_path = output_dir / "zho-Hans_image"
        if image_path.exists() and not overwrite_img:
            image = ImageSeries.load(image_path)
            if not any(sub.text for sub in image):
                info("Copying OCRed text into image subtitles")
                assert len(clean) == len(image), (
                    f"Length mismatch: {len(clean)} vs {len(image)}"
                )
                for text_sub, image_sub in zip(clean, image):
                    image_sub.text = text_sub.text
                image.save(image_path)
        else:
            if not sup_path:
                raise ScinoephileError("sup_path is required to build image output")
            image = ImageSeries.load(sup_path)
            assert len(clean) == len(image), (
                f"Length mismatch: {len(clean)} vs {len(image)}"
            )
            for text_sub, image_sub in zip(clean, image):
                image_sub.text = text_sub.text
            image.save(image_path)
        image_validation_path = output_dir / "zho-Hans_validation"
        validate = validate_zho_ocr(
            image,
            output_dir_path=image_validation_path,
            interactive=True,
        )
        validate.save(validate_path, exist_ok=True)
        validate = Series.load(validate_path)

    # Proofread
    proofread_path = output_dir / "zho-Hans_fuse_clean_validate_proofread.srt"
    if proofread_path.exists() and not overwrite_srt:
        proofread = Series.load(proofread_path)
    else:
        if proofreader_kw is None:
            proofreader_kw = {}
        proofreader_kw.setdefault(
            "test_case_path",
            title_root / "lang" / "zho" / "proofreading" / "zho-Hans.json",
        )
        proofreader = get_zho_proofreader(
            auto_verify=True,
            **proofreader_kw,
        )
        proofread = get_zho_proofread(validate, proofreader)
        proofread.save(proofread_path)

    # Flatten
    flatten_path = output_dir / "zho-Hans_fuse_clean_validate_proofread_flatten.srt"
    if flatten_path.exists() and not overwrite_srt:
        flatten = Series.load(flatten_path)
    else:
        flatten = get_zho_flattened(proofread)
        flatten.save(flatten_path, exist_ok=True)

    # Romanize
    romanize_path = (
        output_dir / "zho-Hans_fuse_clean_validate_proofread_flatten_romanize.srt"
    )
    if not romanize_path.exists() or overwrite_srt:
        romanized = get_cmn_romanized(flatten, append=True)
        romanized.save(romanize_path, exist_ok=True)

    return flatten


def process_zho_hant_ocr(  # noqa: PLR0912, PLR0915
    title_root: Path,
    sup_path: Path | None = None,
    *,
    fuser_kw: Any | None = None,
    proofreader_kw: Any | None = None,
    overwrite_srt: bool = False,
    overwrite_img: bool = False,
    force_validation: bool = False,
) -> Series:
    """Process 繁体中文 OCR subtitles into validated output.

    Arguments:
        title_root: title root directory
        sup_path: subtitle image input path
        fuser_kw: keyword arguments for OCR fuser
        proofreader_kw: keyword arguments for OCR proofreader
        overwrite_srt: whether to overwrite subtitle outputs
        overwrite_img: whether to overwrite image outputs
        force_validation: whether to force validation even if validation output exists
    Returns:
        processed series
    """
    input_dir = title_root / "input"
    output_dir = title_root / "output"

    # Fuse
    fuse_path = output_dir / "zho-Hant_fuse.srt"
    if fuse_path.exists() and not overwrite_srt:
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

        if fuser_kw is None:
            fuser_kw = {}
        fuser_kw.setdefault(
            "test_case_path",
            title_root / "lang" / "zho" / "ocr_fusion" / "zho-Hant.json",
        )
        fuser = get_zho_ocr_fuser(
            prompt_cls=ZhoHantOcrFusionPrompt,
            auto_verify=True,
            **fuser_kw,
        )
        fuse = get_zho_ocr_fused(lens, paddle, fuser)
        fuse.save(fuse_path)

    # Clean
    clean_path = output_dir / "zho-Hant_fuse_clean.srt"
    if clean_path.exists() and not overwrite_srt:
        clean = Series.load(clean_path)
    else:
        clean = get_zho_cleaned(fuse, remove_empty=False)
        clean = get_zho_converted(clean, OpenCCConfig.s2t)
        clean.save(output_dir / "zho-Hant_fuse_clean.srt")

    # Validate
    validate_path = output_dir / "zho-Hant_fuse_clean_validate.srt"
    if validate_path.exists() and not force_validation:
        validate = Series.load(validate_path)
    else:
        image_path = output_dir / "zho-Hant_image"
        if image_path.exists() and not overwrite_img:
            image = ImageSeries.load(image_path)
            if not any(sub.text for sub in image):
                info("Copying OCRed text into image subtitles")
                assert len(clean) == len(image), (
                    f"Length mismatch: {len(clean)} vs {len(image)}"
                )
                for text_sub, image_sub in zip(clean, image):
                    image_sub.text = text_sub.text
                image.save(image_path)
        else:
            if not sup_path:
                raise ScinoephileError("sup_path is required to build image output")
            image = ImageSeries.load(sup_path)
            assert len(clean) == len(image), (
                f"Length mismatch: {len(clean)} vs {len(image)}"
            )
            for text_sub, image_sub in zip(clean, image):
                image_sub.text = text_sub.text
            image.save(image_path)
        image_validation_path = output_dir / "zho-Hant_validation"
        validate = validate_zho_ocr(
            image,
            output_dir_path=image_validation_path,
            interactive=True,
        )
        validate.save(validate_path, exist_ok=True)
        validate = Series.load(validate_path)

    # Proofread
    proofread_path = output_dir / "zho-Hant_fuse_clean_validate_proofread.srt"
    if proofread_path.exists() and not overwrite_srt:
        proofread = Series.load(proofread_path)
    else:
        if proofreader_kw is None:
            proofreader_kw = {}
        proofreader_kw.setdefault(
            "test_case_path",
            title_root / "lang" / "zho" / "proofreading" / "zho-Hant.json",
        )
        proofreader = get_zho_proofreader(
            prompt_cls=ZhoHantProofreadingPrompt,
            auto_verify=True,
            **proofreader_kw,
        )
        proofread = get_zho_proofread(validate, proofreader)
        proofread.save(proofread_path)

    # Flatten
    flatten_path = output_dir / "zho-Hant_fuse_clean_validate_proofread_flatten.srt"
    if flatten_path.exists() and not overwrite_srt:
        flatten = Series.load(flatten_path)
    else:
        flatten = get_zho_flattened(proofread)
        flatten.save(flatten_path, exist_ok=True)

    # Simplify
    simplify_path = (
        output_dir / "zho-Hant_fuse_clean_validate_proofread_flatten_simplify.srt"
    )
    if simplify_path.exists() and not overwrite_srt:
        simplify = Series.load(simplify_path)
    else:
        simplify = get_zho_converted(flatten, OpenCCConfig.t2s)
        simplify.save(simplify_path, exist_ok=True)

    # Simplify proofread
    simplify_proofread_path = (
        output_dir
        / "zho-Hant_fuse_clean_validate_proofread_flatten_simplify_proofread.srt"
    )
    if simplify_proofread_path.exists() and not overwrite_srt:
        simplify_proofread = Series.load(simplify_proofread_path)
    else:
        simplify_proofreader = get_zho_proofreader(
            prompt_cls=ZhoHansProofreadingPrompt,
            test_case_path=title_root
            / "lang"
            / "zho"
            / "proofreading"
            / "zho-Hant_simplify.json",
            auto_verify=True,
        )
        simplify_proofread = get_zho_proofread(simplify, simplify_proofreader)
        simplify_proofread.save(simplify_proofread_path, exist_ok=True)

    # Romanize
    romanize_path = (
        output_dir / "zho-Hant_fuse_clean_validate_proofread_flatten_"
        "simplify_proofread_romanize.srt"
    )
    if not romanize_path.exists() or overwrite_srt:
        romanized = get_cmn_romanized(simplify_proofread, append=True)
        romanized.save(romanize_path, exist_ok=True)

    return flatten
