#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for traditional-simplification review audits."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path

from scinoephile.analysis.audit.review import (
    ReviewAuditFilter,
    ReviewAuditPair,
    audit_review_workflow,
)
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import get_arg_groups_by_name, input_file_arg
from scinoephile.core import ScinoephileError

from .audit_workflow_cli_base import AuditWorkflowCliBase

__all__ = ["AuditReviewTradCli"]

AUDIT_TRADITIONAL_SIMPLIFICATION_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audit traditional review followed by review of its simplified form": (
            "审核繁体字校对及其后续简化形式校对"
        ),
        "traditional-script review input SRT file": "繁体字校对输入 SRT 文件",
        "traditional-script reviewed SRT file": "繁体字校对后 SRT 文件",
        "simplified traditional-script SRT file before review": (
            "校对前由繁体字转换的简体字 SRT 文件"
        ),
        "simplified traditional-script SRT file after review": (
            "校对后由繁体字转换的简体字 SRT 文件"
        ),
        "optional JSON corresponding to the traditional review": (
            "与繁体字校对对应的可选 JSON"
        ),
        "optional JSON corresponding to the traditional simplification review": (
            "与繁体字简化校对对应的可选 JSON"
        ),
    },
    "zh-hant": {
        "audit traditional review followed by review of its simplified form": (
            "稽核繁體字校對及其後續簡化形式校對"
        ),
        "traditional-script review input SRT file": "繁體字校對輸入 SRT 檔",
        "traditional-script reviewed SRT file": "繁體字校對後 SRT 檔",
        "simplified traditional-script SRT file before review": (
            "校對前由繁體字轉換的簡體字 SRT 檔"
        ),
        "simplified traditional-script SRT file after review": (
            "校對後由繁體字轉換的簡體字 SRT 檔"
        ),
        "optional JSON corresponding to the traditional review": (
            "與繁體字校對對應的選用 JSON"
        ),
        "optional JSON corresponding to the traditional simplification review": (
            "與繁體字簡化校對對應的選用 JSON"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class AuditReviewTradCli(AuditWorkflowCliBase):
    """Audit traditional review followed by review of its simplified form."""

    localizations = AUDIT_TRADITIONAL_SIMPLIFICATION_LOCALIZATIONS
    """Localized help text keyed by locale and English source text."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)
        arg_groups = get_arg_groups_by_name(
            parser,
            "input arguments",
            optional_arguments_name="additional arguments",
        )
        arg_groups["input arguments"].add_argument(
            "--traditional",
            dest="traditional_path",
            required=True,
            type=input_file_arg(),
            help="traditional-script review input SRT file",
        )
        arg_groups["input arguments"].add_argument(
            "--traditional-reviewed",
            dest="traditional_reviewed_path",
            required=True,
            type=input_file_arg(),
            help="traditional-script reviewed SRT file",
        )
        arg_groups["input arguments"].add_argument(
            "--traditional-simplified",
            dest="traditional_simplified_path",
            required=True,
            type=input_file_arg(),
            help="simplified traditional-script SRT file before review",
        )
        arg_groups["input arguments"].add_argument(
            "--traditional-simplified-reviewed",
            dest="traditional_simplified_reviewed_path",
            required=True,
            type=input_file_arg(),
            help="simplified traditional-script SRT file after review",
        )
        arg_groups["input arguments"].add_argument(
            "--traditional-json",
            dest="traditional_json_path",
            type=input_file_arg(),
            help="optional JSON corresponding to the traditional review",
        )
        arg_groups["input arguments"].add_argument(
            "--traditional-simplified-json",
            dest="traditional_simplified_json_path",
            type=input_file_arg(),
            help=(
                "optional JSON corresponding to the traditional simplification review"
            ),
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "review-trad"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        traditional_path: Path,
        traditional_reviewed_path: Path,
        traditional_simplified_path: Path,
        traditional_simplified_reviewed_path: Path,
        traditional_json_path: Path | None,
        traditional_simplified_json_path: Path | None,
        row_filter: ReviewAuditFilter,
        characters: Sequence[str],
        first_index: int | None,
        last_index: int | None,
        first_block: int | None,
        last_block: int | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        cls.validate_range(parser, first_index, last_index)

        # Read inputs
        traditional = read_series(parser, traditional_path)
        traditional_reviewed = read_series(parser, traditional_reviewed_path)
        traditional_simplified = read_series(parser, traditional_simplified_path)
        traditional_simplified_reviewed = read_series(
            parser,
            traditional_simplified_reviewed_path,
        )

        # Perform operation
        try:
            report = audit_review_workflow(
                reviews=(
                    ReviewAuditPair(
                        label="Traditional",
                        original=traditional,
                        reviewed=traditional_reviewed,
                        review_cases=cls.load_review_cases(
                            parser,
                            traditional_json_path,
                        ),
                    ),
                    ReviewAuditPair(
                        label="Traditional simplification",
                        original=traditional_simplified,
                        reviewed=traditional_simplified_reviewed,
                        review_cases=cls.load_review_cases(
                            parser,
                            traditional_simplified_json_path,
                        ),
                    ),
                ),
                row_filter=row_filter,
                characters=cls.get_character_variants(characters),
                first_index=first_index,
                last_index=last_index,
                first_block=first_block,
                last_block=last_block,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write output
        cls.write_report(parser, report, outfile_path, overwrite)


if __name__ == "__main__":
    AuditReviewTradCli.main()
