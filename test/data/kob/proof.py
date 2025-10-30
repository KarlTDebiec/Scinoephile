#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Script for proofreading English subtitles."""

from __future__ import annotations

import asyncio

from data.kob import kob_proof_test_cases

from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import Series
from scinoephile.core.english.proofing import EnglishProofer
from scinoephile.testing import test_data_root


async def main():
    input_dir = test_data_root / "kob" / "input"
    output_dir = test_data_root / "kob" / "output"
    set_logging_verbosity(2)

    # English
    eng = Series.load(input_dir / "eng.srt")

    # Utilities
    proofer = EnglishProofer(
        proof_test_cases=kob_proof_test_cases,
        test_case_directory_path=test_data_root / "kob" / "test_cases",
    )

    # Process all blocks
    eng_proof = await proofer.process_all_blocks(eng)

    # Update output file
    outfile_path = output_dir / "eng_proof.srt"
    if outfile_path.exists():
        outfile_path.unlink()
    eng_proof.save(outfile_path)


if __name__ == "__main__":
    asyncio.run(main())
