#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for OCR-fusion audits."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path
from typing import cast

from scinoephile.analysis.ocr_fusion_audit import (
    OcrFusionAuditFilter,
    audit_ocr_fusion,
)
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import (
    enum_arg,
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
)
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.llms.ocr_fusion import OcrFusionManager, OcrFusionTestCase

from .audit_workflow_cli_base import AuditCliBase

__all__ = ["AuditOcrFusionCli"]

AUDIT_OCR_FUSION_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        (
            "audit OCR-fusion decisions against source tracks and optional "
            "validated truth"
        ): ("审核 OCR 融合决策、来源轨道及可选的已验证真值"),
        "first OCR source subtitle SRT file": "第一个 OCR 来源字幕 SRT 文件",
        "second OCR source subtitle SRT file": "第二个 OCR 来源字幕 SRT 文件",
        "fused OCR subtitle SRT file": "OCR 融合字幕 SRT 文件",
        "optional validated subtitle SRT file used as ground truth": (
            "用作真值的可选已验证字幕 SRT 文件"
        ),
        "OCR-fusion test-case JSON file": "OCR 融合测试用例 JSON 文件",
        (
            "rows to include: all, changes, discrepancies, or unverified "
            "(default: changes)"
        ): (
            "要包含的行：all 表示全部，changes 表示来源差异，discrepancies "
            "表示与已验证轨道不同，unverified 表示未验证（默认：changes）"
        ),
        "exact case difficulty levels to include (default: all)": (
            "要包含的指定测试用例难度级别（默认：all）"
        ),
    },
    "zh-hant": {
        (
            "audit OCR-fusion decisions against source tracks and optional "
            "validated truth"
        ): ("稽核 OCR 融合決策、來源軌道及選用的已驗證真值"),
        "first OCR source subtitle SRT file": "第一個 OCR 來源字幕 SRT 檔",
        "second OCR source subtitle SRT file": "第二個 OCR 來源字幕 SRT 檔",
        "fused OCR subtitle SRT file": "OCR 融合字幕 SRT 檔",
        "optional validated subtitle SRT file used as ground truth": (
            "用作真值的選用已驗證字幕 SRT 檔"
        ),
        "OCR-fusion test-case JSON file": "OCR 融合測試案例 JSON 檔",
        (
            "rows to include: all, changes, discrepancies, or unverified "
            "(default: changes)"
        ): (
            "要包含的列：all 表示全部，changes 表示來源差異，discrepancies "
            "表示與已驗證軌道不同，unverified 表示未驗證（預設：changes）"
        ),
        "exact case difficulty levels to include (default: all)": (
            "要包含的指定測試案例難度級別（預設：all）"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class AuditOcrFusionCli(AuditCliBase):
    """Audit OCR-fusion decisions against source tracks and optional validated truth."""

    localizations = AUDIT_OCR_FUSION_LOCALIZATIONS
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
            "operation arguments",
            optional_arguments_name="additional arguments",
        )
        arg_groups["input arguments"].add_argument(
            "--source-one",
            dest="source_one_path",
            required=True,
            type=input_file_arg(),
            help="first OCR source subtitle SRT file",
        )
        arg_groups["input arguments"].add_argument(
            "--source-two",
            dest="source_two_path",
            required=True,
            type=input_file_arg(),
            help="second OCR source subtitle SRT file",
        )
        arg_groups["input arguments"].add_argument(
            "--fused",
            dest="fused_path",
            required=True,
            type=input_file_arg(),
            help="fused OCR subtitle SRT file",
        )
        arg_groups["input arguments"].add_argument(
            "--validated",
            dest="validated_path",
            type=input_file_arg(),
            help="optional validated subtitle SRT file used as ground truth",
        )
        arg_groups["input arguments"].add_argument(
            "--json",
            dest="json_path",
            required=True,
            type=input_file_arg(),
            help="OCR-fusion test-case JSON file",
        )
        arg_groups["operation arguments"].add_argument(
            "--filter",
            choices=tuple(OcrFusionAuditFilter),
            default=OcrFusionAuditFilter.changes,
            dest="row_filter",
            metavar="{all,changes,discrepancies,unverified}",
            type=enum_arg(OcrFusionAuditFilter),
            help=(
                "rows to include: all, changes, discrepancies, or unverified "
                "(default: changes)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--difficulty",
            default=(),
            dest="difficulties",
            metavar="LEVEL",
            nargs="+",
            type=int_arg(min_value=0),
            help="exact case difficulty levels to include (default: all)",
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return "ocr-fusion"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        source_one_path: Path,
        source_two_path: Path,
        fused_path: Path,
        validated_path: Path | None,
        json_path: Path,
        difficulties: Sequence[int],
        row_filter: OcrFusionAuditFilter,
        first_index: int | None,
        last_index: int | None,
        first_block: int | None,
        last_block: int | None,
        outfile_path: Path | None,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()
        cls.validate_range(parser, first_index, last_index)
        cls.validate_block_range(parser, first_block, last_block)
        source_one = read_series(parser, source_one_path)
        source_two = read_series(parser, source_two_path)
        fused = read_series(parser, fused_path)
        validated = None
        if validated_path is not None:
            validated = read_series(parser, validated_path)
        loaded_test_cases = cls.load_test_cases(
            parser,
            json_path,
            OcrFusionManager,
            workflow_name="OCR-fusion",
        )
        test_cases = [
            cast(OcrFusionTestCase, test_case) for test_case in loaded_test_cases
        ]

        try:
            report = audit_ocr_fusion(
                source_one,
                source_two,
                fused,
                test_cases,
                validated=validated,
                difficulties=difficulties,
                row_filter=row_filter,
                first_index=first_index,
                last_index=last_index,
                first_block=first_block,
                last_block=last_block,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))
        cls.write_report(parser, report, outfile_path)


if __name__ == "__main__":
    AuditOcrFusionCli.main()
