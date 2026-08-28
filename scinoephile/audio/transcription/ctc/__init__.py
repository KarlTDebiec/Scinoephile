#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CTC transcription alignment.

Package hierarchy (modules may import from any above):
* path / text / tokenization
* model
* aligner
"""

from __future__ import annotations

from .aligner import CtcAligner

__all__ = ["CtcAligner"]
