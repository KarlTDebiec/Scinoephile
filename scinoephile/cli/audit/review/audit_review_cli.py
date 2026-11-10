#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command group for proofreading audits."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from scinoephile.common.cli import CommandLineInterface
from scinoephile.core.cli import ScinoephileCliBase

from .audit_review_report_cli import AuditReviewReportCli
from .audit_review_run_cli import AuditReviewRunCli
from .audit_review_serve_cli import AuditReviewServeCli

__all__ = ["AuditReviewCli"]

AUDIT_REVIEW_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "report on, audit, or edit subtitle proofreading": (
            "生成字幕校对报告、运行审核或打开编辑器"
        )
    },
    "zh-hant": {
        "report on, audit, or edit subtitle proofreading": (
            "產生字幕校對報告、執行稽核或開啟編輯器"
        )
    },
}
"""Translated review command group description."""


class AuditReviewCli(ScinoephileCliBase):
    """Report on, audit, or edit subtitle proofreading."""

    localizations = AUDIT_REVIEW_LOCALIZATIONS
    """Translated review command group description."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Register the audit, report, and browser commands.

        Arguments:
            parser: parser to configure
        """
        super().add_arguments_to_argparser(parser)
        subparsers = parser.add_subparsers(
            dest="review_subcommand_name", help="subcommand", required=True
        )
        for command in cls.subcommands().values():
            command.argparser(subparsers=subparsers)

    @classmethod
    def name(cls) -> str:
        """Return the review command group name.

        Returns:
            review subcommand name
        """
        return "review"

    @classmethod
    def subcommands(cls) -> dict[str, type[CommandLineInterface]]:
        """Return review output modes and their CLI implementations.

        Returns:
            review command implementations keyed by name
        """
        return {
            "run": AuditReviewRunCli,
            "report": AuditReviewReportCli,
            "serve": AuditReviewServeCli,
        }

    @classmethod
    def _main(cls, *, review_subcommand_name: str, **kwargs: Any):
        """Dispatch the selected review interface.

        Arguments:
            review_subcommand_name: selected review command
            **kwargs: parsed arguments for the selected command
        """
        cls.subcommands()[review_subcommand_name]._main(**kwargs)
