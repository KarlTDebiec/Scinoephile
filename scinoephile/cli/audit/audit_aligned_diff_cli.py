#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for aligned subtitle diff audits."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.analysis.audit.aligned_diff import (
    AlignedDiffAuditFilter,
    audit_aligned_diff,
)
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import (
    float_arg,
    get_arg_groups_by_name,
    input_file_arg,
)
from scinoephile.core import ScinoephileError

from .audit_cli_base import AuditCliBase

__all__ = ["AuditAlignedDiffCli"]

AUDIT_ALIGNED_DIFF_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audit character-aligned subtitle differences": "审核字符对齐的字幕差异",
        "optional original subtitle SRT file matched by timing overlap": (
            "按时间重叠匹配的可选原始字幕 SRT 文件"
        ),
        "transcribed subtitle SRT file under audit": "待审核的转写字幕 SRT 文件",
        "reference subtitle SRT file used for comparison": (
            "用于比较的参考字幕 SRT 文件"
        ),
        "optional guide subtitle SRT file aligned with the transcription": (
            "与转写字幕对齐的可选导引字幕 SRT 文件"
        ),
        (
            "rows to include: all or changes; all includes every aligned row; "
            "changes includes differing rows (default: %(default)s)"
        ): ("要包含的行：all 表示每个对齐行，changes 表示差异行（默认：%(default)s）"),
        "similarity threshold used to pair replacements (default: %(default)s)": (
            "用于配对替换项的相似度阈值（默认：%(default)s）"
        ),
    },
    "zh-hant": {
        "audit character-aligned subtitle differences": "稽核字元對齊的字幕差異",
        "optional original subtitle SRT file matched by timing overlap": (
            "按時間重疊配對的可選原始字幕 SRT 檔"
        ),
        "transcribed subtitle SRT file under audit": "待稽核的轉寫字幕 SRT 檔",
        "reference subtitle SRT file used for comparison": (
            "用於比較的參考字幕 SRT 檔"
        ),
        "optional guide subtitle SRT file aligned with the transcription": (
            "與轉寫字幕對齊的可選導引字幕 SRT 檔"
        ),
        (
            "rows to include: all or changes; all includes every aligned row; "
            "changes includes differing rows (default: %(default)s)"
        ): ("要包含的列：all 表示每個對齊列，changes 表示差異列（預設：%(default)s）"),
        "similarity threshold used to pair replacements (default: %(default)s)": (
            "用於配對替換項的相似度閾值（預設：%(default)s）"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class AuditAlignedDiffCli(AuditCliBase):
    """Audit character-aligned subtitle differences."""

    localizations = AUDIT_ALIGNED_DIFF_LOCALIZATIONS
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
            "output arguments",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--original",
            dest="original_path",
            type=input_file_arg(),
            help="optional original subtitle SRT file matched by timing overlap",
        )
        arg_groups["input arguments"].add_argument(
            "--transcription",
            dest="transcription_path",
            required=True,
            type=input_file_arg(),
            help="transcribed subtitle SRT file under audit",
        )
        arg_groups["input arguments"].add_argument(
            "--reference",
            dest="reference_path",
            required=True,
            type=input_file_arg(),
            help="reference subtitle SRT file used for comparison",
        )
        arg_groups["input arguments"].add_argument(
            "--guide",
            dest="guide_path",
            type=input_file_arg(),
            help="optional guide subtitle SRT file aligned with the transcription",
        )

        # Operation arguments
        cls.add_row_filter_argument(
            parser,
            AlignedDiffAuditFilter,
            AlignedDiffAuditFilter.changes,
            description=(
                "all includes every aligned row; changes includes differing rows"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--similarity-cutoff",
            default=0.6,
            type=float_arg(min_value=0.0, max_value=1.0),
            help=(
                "similarity threshold used to pair replacements (default: %(default)s)"
            ),
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "aligned-diff"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        original_path: Path | None,
        transcription_path: Path,
        reference_path: Path,
        guide_path: Path | None,
        first_index: int | None,
        last_index: int | None,
        first_block: int | None,
        last_block: int | None,
        row_filter: AlignedDiffAuditFilter,
        similarity_cutoff: float,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments.

        Arguments:
            _parser: parser used to report user-facing errors
            original_path: optional original subtitle SRT path
            transcription_path: transcribed subtitle SRT path
            reference_path: comparison reference subtitle SRT path
            guide_path: optional guide subtitle SRT path
            first_index: first transcription subtitle number to include
            last_index: last transcription subtitle number to include
            first_block: first transcription block number to include
            last_block: last transcription block number to include
            row_filter: rows to include in the report
            similarity_cutoff: similarity cutoff for pairing replacement blocks
            outfile_path: optional Markdown output path
            overwrite: whether to overwrite an existing output file
        """
        parser = _parser or cls.argparser()

        # Read inputs
        original = None
        if original_path is not None:
            original = read_series(parser, original_path)
        transcription = read_series(parser, transcription_path)
        reference = read_series(parser, reference_path)
        guide = None
        if guide_path is not None:
            guide = read_series(parser, guide_path)

        # Perform operation
        try:
            report = audit_aligned_diff(
                transcription,
                reference,
                guide,
                original=original,
                row_filter=row_filter,
                first_index=first_index,
                last_index=last_index,
                first_block=first_block,
                last_block=last_block,
                similarity_cutoff=similarity_cutoff,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write output
        cls.write_report(parser, report, outfile_path, overwrite)


if __name__ == "__main__":
    AuditAlignedDiffCli.main()
