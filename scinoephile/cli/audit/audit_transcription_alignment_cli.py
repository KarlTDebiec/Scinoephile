#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for multi-source transcription alignment audits."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from pydantic import ValidationError

from scinoephile.analysis.audit.transcription_alignment import (
    audit_transcription_alignment,
)
from scinoephile.analysis.transcription_alignment import TranscriptionAlignmentArtifact
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
)
from scinoephile.core.exceptions import ScinoephileError

from .audit_cli_base import AuditCliBase

__all__ = ["AuditTranscriptionAlignmentCli"]

AUDIT_TRANSCRIPTION_ALIGNMENT_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audit aligned multi-source transcription evidence": ("审核多来源转写对齐证据"),
        "transcription alignment artifact JSON file": "转写对齐成品 JSON 文件",
        "optional independent reference subtitle SRT file": (
            "可选的独立参考字幕 SRT 文件"
        ),
        "alignment columns per displayed chunk (default: %(default)s)": (
            "每个显示区段的对齐列数（默认：%(default)s）"
        ),
    },
    "zh-hant": {
        "audit aligned multi-source transcription evidence": ("稽核多來源轉寫對齊證據"),
        "transcription alignment artifact JSON file": "轉寫對齊成品 JSON 檔",
        "optional independent reference subtitle SRT file": (
            "可選的獨立參考字幕 SRT 檔"
        ),
        "alignment columns per displayed chunk (default: %(default)s)": (
            "每個顯示區段的對齊欄數（預設：%(default)s）"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class AuditTranscriptionAlignmentCli(AuditCliBase):
    """Audit aligned multi-source transcription evidence."""

    localizations = AUDIT_TRANSCRIPTION_ALIGNMENT_LOCALIZATIONS
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
        arg_groups["input arguments"].add_argument(
            "--alignment",
            dest="alignment_path",
            required=True,
            type=input_file_arg(),
            help="transcription alignment artifact JSON file",
        )
        arg_groups["input arguments"].add_argument(
            "--reference",
            dest="reference_path",
            type=input_file_arg(),
            help="optional independent reference subtitle SRT file",
        )
        arg_groups["operation arguments"].add_argument(
            "--columns",
            default=60,
            dest="columns_per_chunk",
            type=int_arg(min_value=1),
            help="alignment columns per displayed chunk (default: %(default)s)",
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "transcription-alignment"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        alignment_path: Path,
        reference_path: Path | None,
        first_index: int | None,
        last_index: int | None,
        first_block: int | None,
        last_block: int | None,
        columns_per_chunk: int,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments.

        Arguments:
            _parser: parser used to report user-facing errors
            alignment_path: transcription alignment artifact JSON path
            reference_path: optional independent reference SRT path
            first_index: first merged subtitle number to include
            last_index: last merged subtitle number to include
            first_block: first VAD block number to include
            last_block: last VAD block number to include
            columns_per_chunk: alignment columns per displayed chunk
            outfile_path: optional Markdown output path
            overwrite: whether to overwrite an existing output file
        """
        parser = _parser or cls.argparser()
        try:
            artifact = TranscriptionAlignmentArtifact.load(alignment_path)
        except (OSError, UnicodeError, ValueError, ValidationError) as exc:
            parser.error(f"Unable to load transcription alignment artifact: {exc}")
        reference = None
        if reference_path is not None:
            reference = read_series(parser, reference_path)
        try:
            report = audit_transcription_alignment(
                artifact,
                reference,
                first_index=first_index,
                last_index=last_index,
                first_block=first_block,
                last_block=last_block,
                columns_per_chunk=columns_per_chunk,
            )
        except (ScinoephileError, ValueError) as exc:
            parser.error(str(exc))
        cls.write_report(parser, report, outfile_path, overwrite)


if __name__ == "__main__":
    AuditTranscriptionAlignmentCli.main()
