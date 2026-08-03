#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Block-level subtitle delineation using sparse LLM changes.

Package hierarchy (modules may import from any above):
* prompt
* models
* manager
* processor
"""

from __future__ import annotations

from .manager import (
    AdvisoryBlockDelineationManager,
    BlockDelineationManager,
    CandidateBlockDelineationManager,
)
from .models import (
    AdvisoryBlockDelineationBoundary,
    AdvisoryBlockDelineationBoundarySuggestion,
    AdvisoryBlockDelineationQuery,
    AdvisoryBlockDelineationTestCase,
    BlockDelineationAnswer,
    BlockDelineationBoundary,
    BlockDelineationBoundaryCandidate,
    BlockDelineationBoundaryChange,
    BlockDelineationQuery,
    BlockDelineationSubtitle,
    BlockDelineationTestCase,
    CandidateBlockDelineationBoundary,
    CandidateBlockDelineationQuery,
    CandidateBlockDelineationTestCase,
)
from .processor import (
    AdvisoryBlockDelineationProcessor,
    BlockDelineationProcessor,
    CandidateBlockDelineationProcessor,
)
from .prompt import (
    AdvisoryBlockDelineationPrompt,
    BlockDelineationPrompt,
    CandidateBlockDelineationPrompt,
)

__all__ = [
    "AdvisoryBlockDelineationBoundary",
    "AdvisoryBlockDelineationBoundarySuggestion",
    "AdvisoryBlockDelineationManager",
    "AdvisoryBlockDelineationProcessor",
    "AdvisoryBlockDelineationPrompt",
    "AdvisoryBlockDelineationQuery",
    "AdvisoryBlockDelineationTestCase",
    "BlockDelineationAnswer",
    "BlockDelineationBoundary",
    "BlockDelineationBoundaryCandidate",
    "BlockDelineationBoundaryChange",
    "BlockDelineationManager",
    "BlockDelineationProcessor",
    "BlockDelineationPrompt",
    "BlockDelineationQuery",
    "BlockDelineationSubtitle",
    "BlockDelineationTestCase",
    "CandidateBlockDelineationBoundary",
    "CandidateBlockDelineationManager",
    "CandidateBlockDelineationProcessor",
    "CandidateBlockDelineationPrompt",
    "CandidateBlockDelineationQuery",
    "CandidateBlockDelineationTestCase",
]
