#!/usr/bin/env python
# Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Update Chinese README translations."""

from __future__ import annotations

from logging import info

from scinoephile.common import package_root
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core.zhongwen import OpenCCConfig, get_zhongwen_converter
from scinoephile.documentation.translation import TranslateQuery, Translator
from scinoephile.testing import test_data_root


def split_readme(readme_text: str) -> tuple[str, str]:
    """Split README into header and body.

    The header includes badges and language links, ending at the line that starts with
    '[English]('.
    """
    header_lines = []
    lines = readme_text.splitlines()

    for line in lines:
        header_lines.append(line)
        if line.startswith("[English]("):
            break

    body_start = len(header_lines)
    header = "\n".join(header_lines) + "\n\n"
    body = "\n".join(lines[body_start:])

    return header, body


def main():
    """Update all README translations."""
    set_logging_verbosity(2)
    repo_root = package_root.parent
    translator = Translator(cache_dir_path=test_data_root / "cache")

    # English
    english_path = repo_root / "README.md"
    complete_english = english_path.read_text(encoding="utf-8")
    header, updated_english = split_readme(complete_english)

    # Chinese
    for language, iso_code, config in [
        ("zhongwen", "zh", OpenCCConfig.t2s),
        ("yuewen", "yue", OpenCCConfig.hk2s),
    ]:
        trad_path = repo_root / "docs" / f"README.{iso_code}-hant.md"
        info(f"Updating {trad_path.name}")
        complete_trad_chinese = trad_path.read_text(encoding="utf-8")
        _, outdated_trad_chinese = split_readme(complete_trad_chinese)
        updated_trad_chinese = translator(
            TranslateQuery(
                updated_english=updated_english,
                outdated_chinese=outdated_trad_chinese,
                language=language,
            )
        ).updated_chinese
        trad_path.write_text(
            (header + updated_trad_chinese).rstrip() + "\n", encoding="utf-8"
        )
        info(f"Updated {trad_path.name}")

        simp_path = repo_root / "docs" / f"README.{iso_code}-hans.md"
        info(f"Updating {simp_path.name}")
        updated_simp_chinese = get_zhongwen_converter(config).convert(
            updated_trad_chinese
        )
        simp_path.write_text(
            (header + updated_simp_chinese).rstrip() + "\n", encoding="utf-8"
        )
        info(f"Updated {simp_path.name}")




if __name__ == "__main__":
    main()
