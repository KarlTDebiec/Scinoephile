#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Compatibility parsing for review audits without an explicit report command."""

from __future__ import annotations

import sys
from argparse import ArgumentParser
from collections.abc import Iterable
from typing import Any

__all__ = ["ReviewArgumentParser"]


class ReviewArgumentParser(ArgumentParser):
    """Allow the review command to default legacy option-only calls to report."""

    default_review_report = False
    """Whether this particular parser represents the review command."""

    def parse_known_args(
        self, args: Iterable[str] | None = None, namespace: Any = None
    ) -> tuple[Any, list[str]]:
        """Normalize legacy review arguments before standard argparse processing.

        Arguments:
            args: explicit arguments, or the current process arguments
            namespace: optional namespace receiving parsed values
        Returns:
            parsed namespace and unrecognized arguments
        """
        values = list(sys.argv[1:])
        if args is not None:
            values = list(args)
        if (
            self.default_review_report
            and values
            and values[0].startswith("-")
            and values[0] not in {"-h", "--help"}
        ):
            values.insert(0, "report")
        return super().parse_known_args(values, namespace)
