#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Language identification for text and subtitle series.

Package hierarchy (modules may import from any above):
* language_id
"""

from __future__ import annotations

from collections import Counter

from scinoephile.core import Language
from scinoephile.core.subtitles import Series

from .language_id import LanguageId

__all__ = [
    "LanguageId",
    "get_series_language",
]

SERIES_LANGUAGE_AGREEMENT_THRESHOLD = 3
"""Number of conclusive subtitles that must agree on a series language."""


def get_series_language(series: Series) -> Language | None:
    """Get the detected language of a subtitle series.

    Arguments:
        series: subtitle series to classify
    Returns:
        detected language, if enough subtitle events agree
    """
    counts: Counter[Language] = Counter()
    for subtitle in series.events:
        language = LanguageId.from_text(subtitle.text).language
        if language is None:
            continue
        counts[language] += 1

    if not counts:
        return None

    most_common = counts.most_common(2)
    language, count = most_common[0]
    if count < SERIES_LANGUAGE_AGREEMENT_THRESHOLD:
        return None
    if len(most_common) > 1 and most_common[1][1] == count:
        return None
    return language
