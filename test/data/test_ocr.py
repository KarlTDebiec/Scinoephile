#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of test.data.ocr."""

from __future__ import annotations

from inspect import signature

from test.data.ocr import process_eng_ocr, process_zho_hans_ocr, process_zho_hant_ocr


def test_ocr_fixture_processors_default_to_dev_mode():
    """Test OCR fixture processors write validation data updates to the repo."""
    for processor in (process_eng_ocr, process_zho_hans_ocr, process_zho_hant_ocr):
        assert signature(processor).parameters["dev"].default is True
