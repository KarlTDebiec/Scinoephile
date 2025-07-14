#!/usr/bin/env python
# Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Update Chinese README translations."""

from __future__ import annotations

import logging
from logging import info

from scinoephile.common import package_root
from scinoephile.core.hanzi import OpenCCConfig, get_hanzi_converter
from scinoephile.translation import ReadmeTranslator

logging.basicConfig(level=logging.INFO)


def update_readmes() -> None:
    """Update all README translations."""
    repo_root = package_root.parent
    translator = ReadmeTranslator()

    english_path = repo_root / "README.md"
    english_readme = english_path.read_text(encoding="utf-8")

    # Traditional Zhongwen
    zh_trad_path = repo_root / "README.zh-hant.md"
    zh_trad_old = zh_trad_path.read_text(encoding="utf-8")
    info("Translating Zhongwen README")
    zh_trad_new = translator.translate(english_readme, zh_trad_old, "zhongwen")
    zh_trad_path.write_text(zh_trad_new, encoding="utf-8")

    # Traditional Yuewen
    yue_trad_path = repo_root / "README.yue-hant.md"
    yue_trad_old = yue_trad_path.read_text(encoding="utf-8")
    info("Translating Yuewen README")
    yue_trad_new = translator.translate(english_readme, yue_trad_old, "yuewen")
    yue_trad_path.write_text(yue_trad_new, encoding="utf-8")

    # Simplified conversions
    converter = get_hanzi_converter(OpenCCConfig.t2s)
    (repo_root / "README.zh-hans.md").write_text(
        converter.convert(zh_trad_new), encoding="utf-8"
    )
    (repo_root / "README.yue-hans.md").write_text(
        converter.convert(yue_trad_new), encoding="utf-8"
    )


def main() -> None:
    """Run as a script."""
    update_readmes()


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
