#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for subtitle audits."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from scinoephile.common import CommandLineInterface
from scinoephile.core.cli import ScinoephileCliBase

from .audit_delineation_cli import AuditDelineationCli
from .audit_ocr_fusion_cli import AuditOcrFusionCli
from .audit_punctuation_cli import AuditPunctuationCli
from .audit_review_cli import AuditReviewCli
from .audit_review_dual_cli import AuditReviewDualCli
from .audit_review_trad_cli import AuditReviewTradCli

__all__ = ["AuditCli"]

AUDIT_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audit subtitle workflows": "审核字幕工作流",
    },
    "zh-hant": {
        "audit subtitle workflows": "稽核字幕工作流程",
    },
}
"""Localized help text keyed by locale and English source text."""


class AuditCli(ScinoephileCliBase):
    """Audit subtitle workflows."""

    localizations = AUDIT_LOCALIZATIONS
    """Localized help text keyed by locale and English source text."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)
        subparsers = parser.add_subparsers(
            dest="audit_subcommand_name",
            help="subcommand",
            required=True,
        )
        subcommands = cls.subcommands()
        for name in sorted(subcommands):
            subcommands[name].argparser(subparsers=subparsers)

    @classmethod
    def subcommands(cls) -> dict[str, type[CommandLineInterface]]:
        """Names and types of tools wrapped by command-line interface.

        Returns:
            mapping of subcommand names to CLI classes
        """
        return {
            AuditDelineationCli.name(): AuditDelineationCli,
            AuditOcrFusionCli.name(): AuditOcrFusionCli,
            AuditPunctuationCli.name(): AuditPunctuationCli,
            AuditReviewCli.name(): AuditReviewCli,
            AuditReviewDualCli.name(): AuditReviewDualCli,
            AuditReviewTradCli.name(): AuditReviewTradCli,
        }

    @classmethod
    def _main(
        cls,
        *,
        audit_subcommand_name: str,
        **kwargs: Any,
    ):
        """Execute with provided keyword arguments.

        Arguments:
            audit_subcommand_name: audit subcommand to execute
            **kwargs: arguments forwarded to the selected audit subcommand
        """
        cls.subcommands()[audit_subcommand_name]._main(**kwargs)


if __name__ == "__main__":
    AuditCli.main()
