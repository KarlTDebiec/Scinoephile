#!/usr/bin/env python
# Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Update Chinese README translations."""

from __future__ import annotations

from logging import info

from scinoephile.common import package_root
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core.hanzi import OpenCCConfig, get_hanzi_converter
from scinoephile.testing import test_data_root
from scinoephile.translation import ReadmeTranslator
from scinoephile.translation.models import ReadmeTranslationQuery


def split_readme(readme_text: str) -> tuple[str, str]:
    """Split README into header and body.

    The header includes badges and language links, ending at the first empty line
    before real content begins.
    """
    lines = readme_text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "":
            for j in range(i + 1, len(lines)):
                if lines[j].strip() != "":
                    return "\n".join(lines[:j]) + "\n\n", "\n".join(lines[j:])
            break
    return "", readme_text


def main() -> None:
    """Update all README translations."""
    set_logging_verbosity(2)
    repo_root = package_root.parent
    translator = ReadmeTranslator(
        cache_dir_path=test_data_root / "cache",
    )

    # English
    english_path = repo_root / "README.md"
    english_updated = english_path.read_text(encoding="utf-8")

    # 繁體中文
    zw_trad_path = repo_root / "README.zh-hant.md"
    info(f"Updating {zw_trad_path.name}")
    zw_trad_outdated = zw_trad_path.read_text(encoding="utf-8")
    zh_trad_updated = translator(
        ReadmeTranslationQuery(
            updated_english=english_updated,
            outdated_chinese=zw_trad_outdated,
            language="zhongwen",
        )
    ).updated_chinese
    zw_trad_path.write_text(zh_trad_updated.rstrip() + "\n", encoding="utf-8")
    info(f"Updated {zw_trad_path.name}")

    # 繁體粵文
    yw_trad_path = repo_root / "README.yue-hant.md"
    info(f"Updating {yw_trad_path.name}")
    yue_trad_outdated = yw_trad_path.read_text(encoding="utf-8")
    yue_trad_updated = translator(
        ReadmeTranslationQuery(
            updated_english=english_updated,
            outdated_chinese=yue_trad_outdated,
            language="yuewen",
        )
    ).updated_chinese
    yw_trad_path.write_text(yue_trad_updated.rstrip() + "\n", encoding="utf-8")
    info(f"Updated {yw_trad_path.name}")

    # 简体中文
    zw_simp_path = repo_root / "README.zh-hans.md"
    info(f"Updating {zw_simp_path.name}")
    zw_simp_updated = get_hanzi_converter(OpenCCConfig.t2s).convert(zh_trad_updated)
    zw_simp_path.write_text(zw_simp_updated.rstrip() + "\n", encoding="utf-8")
    info(f"Updated {zw_simp_path.name}")

    # 简体粵文
    yw_simp_path = repo_root / "README.yue-hans.md"
    info(f"Updating {yw_simp_path.name}")
    yw_simp_updated = get_hanzi_converter(OpenCCConfig.hk2s).convert(yue_trad_updated)
    yw_simp_path.write_text(yw_simp_updated.rstrip() + "\n", encoding="utf-8")
    info(f"Updated {yw_simp_path.name}")


if __name__ == "__main__":
    main()
