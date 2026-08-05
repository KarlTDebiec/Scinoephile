#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Run the ACOPOPB transcription pipeline for its first guide block."""

from __future__ import annotations

from scinoephile.common.logs import set_logging_verbosity
from test.data.acopopb.create_output import (
    process_yue_hant_transcription,
    yue_hant_transcribe_path,
)


def main():
    """Generate isolated first-block outputs using the production configuration."""
    set_logging_verbosity(2)
    output_dir_path = (
        yue_hant_transcribe_path.parent / "yue-Hant_transcribe-first-block"
    )
    process_yue_hant_transcription(output_dir_path, stop_at_idx=1)


if __name__ == "__main__":
    main()
