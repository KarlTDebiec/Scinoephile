#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Functions for synchronizing multilingual subtitles."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core.subtitles import Series
from scinoephile.core.synchronization import get_synced_series
from scinoephile.lang.eng import get_eng_cleaned, get_eng_flattened
from scinoephile.lang.zho import get_zho_cleaned, get_zho_flattened

__all__ = [
    "process_yue_hans_eng",
    "process_zho_hans_eng",
]


def process_yue_hans_eng(
    title_root: Path,
    yue_hans_path: Path | None = None,
    eng_path: Path | None = None,
    overwrite: bool = False,
) -> Series:
    """Process bilingual 简体粤文 and English subtitles into a synced series.

    Arguments:
        title_root: title root directory
        yue_hans_path: optional 简体粤文 subtitle path
        eng_path: optional English subtitle path
        overwrite: whether to overwrite subtitle outputs
    Returns:
        processed series
    """
    output_dir = title_root / "output"

    yue_hans_eng_path = output_dir / "yue-Hans_eng.srt"
    if yue_hans_eng_path.exists() and not overwrite:
        yue_hans_eng = Series.load(yue_hans_eng_path)
    else:
        if yue_hans_path is None:
            yue_hans_path = output_dir / "yue-Hans.srt"
        yue_hans = Series.load(yue_hans_path)
        yue_hans = get_zho_cleaned(yue_hans)
        yue_hans = get_zho_flattened(yue_hans)

        if eng_path is None:
            eng_path = output_dir / "eng.srt"
        eng = Series.load(eng_path)
        eng = get_eng_cleaned(eng)
        eng = get_eng_flattened(eng)

        yue_hans_eng = get_synced_series(yue_hans, eng)
        yue_hans_eng.save(output_dir / "yue-Hans_eng.srt")

    return yue_hans_eng


def process_zho_hans_eng(
    title_root: Path,
    zho_hans_path: Path | None = None,
    eng_path: Path | None = None,
    overwrite: bool = False,
) -> Series:
    """Process bilingual 简体中文 and English subtitles into a synced series.

    Arguments:
        title_root: title root directory
        zho_hans_path: optional 简体中文 subtitle path
        eng_path: optional English subtitle path
        overwrite: whether to overwrite subtitle outputs
    Returns:
        processed series
    """
    output_dir = title_root / "output"

    zho_hans_eng_path = output_dir / "zho-Hans_eng.srt"
    if zho_hans_eng_path.exists() and not overwrite:
        zho_hans_eng = Series.load(zho_hans_eng_path)
    else:
        if zho_hans_path is None:
            zho_hans_path = output_dir / "zho-Hans.srt"
        zho_hans = Series.load(zho_hans_path)
        zho_hans = get_zho_cleaned(zho_hans)
        zho_hans = get_zho_flattened(zho_hans)

        if eng_path is None:
            eng_path = output_dir / "eng.srt"
        eng = Series.load(eng_path)
        eng = get_eng_cleaned(eng)
        eng = get_eng_flattened(eng)

        zho_hans_eng = get_synced_series(zho_hans, eng)
        zho_hans_eng.save(output_dir / "zho-Hans_eng.srt")

    return zho_hans_eng
