#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command group for Markdown and interactive proofreading review audits."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from scinoephile.common.cli import CommandLineInterface
from scinoephile.core.cli import ScinoephileCliBase

from .audit_review_report_cli import AuditReviewReportCli
from .audit_review_serve_cli import AuditReviewServeCli

__all__ = ["AuditReviewCli"]


class AuditReviewCli(ScinoephileCliBase):
    """Audit subtitle reviews with reports or an interactive browser."""

    localizations = {
        "zh-hans": {
            "audit subtitle reviews with reports or an interactive browser": (
                "通过报告或交互式浏览器审核字幕校对"
            )
        },
        "zh-hant": {
            "audit subtitle reviews with reports or an interactive browser": (
                "透過報告或互動式瀏覽器稽核字幕校對"
            )
        },
    }
    """Translated review command group description."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Register the report and browser commands.

        Arguments:
            parser: nascent review command parser
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
            report and serve command implementations
        """
        return {"report": AuditReviewReportCli, "serve": AuditReviewServeCli}

    @classmethod
    def _main(cls, *, review_subcommand_name: str, **kwargs: Any):
        """Dispatch the selected review interface.

        Arguments:
            review_subcommand_name: report or serve
            **kwargs: parsed arguments for the selected command
        """
        cls.subcommands()[review_subcommand_name]._main(**kwargs)
