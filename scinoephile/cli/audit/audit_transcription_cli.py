#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for multi-source transcription alignment audits."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.analysis.audit.transcription.report import (
    audit_transcription_alignment,
)
from scinoephile.analysis.transcription import AlignmentArtifact
from scinoephile.cli.helpers.blocks import add_block_range_args
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    named_input_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.lang.yue.transcription import YueTokenSimilarity

from .audit_cli_base import AuditCliBase

__all__ = ["AuditTranscriptionCli"]

AUDIT_TRANSCRIPTION_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audit aligned multi-source transcription evidence": "审核多来源转写对齐证据",
        "transcription alignment artifact JSON file": "转写对齐成品 JSON 文件",
        (
            "named independent reference SRT file as NAME=PATH; repeat for "
            "multiple references"
        ): ("命名的独立参考 SRT 文件，格式为名称=路径；多个参考文件可重复使用"),
        "include the speaker annotation row": "包含说话者标注行",
        "include the spoken-language annotation row": "包含口语语言标注行",
        "include the merged-character source-support row": "包含合并字符的来源支持行",
        "include the singing and music annotation rows": "包含歌唱和音乐标注行",
        "include detailed subtitle and reference timing tables": (
            "包含详细的字幕和参考时间表"
        ),
    },
    "zh-hant": {
        "audit aligned multi-source transcription evidence": "稽核多來源轉寫對齊證據",
        "transcription alignment artifact JSON file": "轉寫對齊成品 JSON 檔",
        (
            "named independent reference SRT file as NAME=PATH; repeat for "
            "multiple references"
        ): ("具名的獨立參考 SRT 檔，格式為名稱=路徑；多個參考檔可重複使用"),
        "include the speaker annotation row": "包含說話者標註列",
        "include the spoken-language annotation row": "包含口語語言標註列",
        "include the merged-character source-support row": "包含合併字符的來源支持列",
        "include the singing and music annotation rows": "包含歌唱和音樂標註列",
        "include detailed subtitle and reference timing tables": (
            "包含詳細的字幕和參考時間表"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class AuditTranscriptionCli(AuditCliBase):
    """Audit aligned multi-source transcription evidence."""

    localizations = AUDIT_TRANSCRIPTION_LOCALIZATIONS
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
            "--alignment",
            dest="alignment_path",
            required=True,
            type=input_file_arg(),
            help="transcription alignment artifact JSON file",
        )
        arg_groups["input arguments"].add_argument(
            "--reference",
            action="append",
            dest="reference_specs",
            metavar="NAME=PATH",
            type=named_input_file_arg(),
            help=(
                "named independent reference SRT file as NAME=PATH; repeat for "
                "multiple references"
            ),
        )
        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--include-audio-events",
            action="store_true",
            help="include the singing and music annotation rows",
        )
        arg_groups["operation arguments"].add_argument(
            "--include-language",
            action="store_true",
            help="include the spoken-language annotation row",
        )
        arg_groups["operation arguments"].add_argument(
            "--include-merge-support",
            action="store_true",
            help="include the merged-character source-support row",
        )
        arg_groups["operation arguments"].add_argument(
            "--include-speaker",
            action="store_true",
            help="include the speaker annotation row",
        )
        arg_groups["operation arguments"].add_argument(
            "--include-timing",
            action="store_true",
            dest="include_timing_tables",
            help="include detailed subtitle and reference timing tables",
        )
        add_block_range_args(arg_groups["operation arguments"])

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "transcription"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        alignment_path: Path,
        reference_specs: list[tuple[str, Path]] | None,
        first_index: int | None,
        last_index: int | None,
        first_block: int | None,
        last_block: int | None,
        include_audio_events: bool,
        include_language: bool,
        include_merge_support: bool,
        include_speaker: bool,
        include_timing_tables: bool,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments.

        Arguments:
            _parser: parser used to report user-facing errors
            alignment_path: transcription alignment artifact JSON path
            reference_specs: optional named independent reference SRT paths
            first_index: first merged subtitle number to include
            last_index: last merged subtitle number to include
            first_block: first VAD block number to include
            last_block: last VAD block number to include
            include_audio_events: whether to render singing and music rows
            include_language: whether to render the spoken-language annotation row
            include_merge_support: whether to render merged-character source support
            include_speaker: whether to render the speaker annotation row
            include_timing_tables: whether to render detailed timing tables
            outfile_path: optional Markdown output path
            overwrite: whether to overwrite an existing output file
        """
        parser = _parser or cls.argparser()

        # Read inputs
        try:
            artifact = AlignmentArtifact.load(alignment_path)
        except (OSError, ValueError) as exc:
            parser.error(f"Unable to load transcription alignment artifact: {exc}")
        references = {}
        for reference_name, reference_path in reference_specs or ():
            if reference_name in references:
                parser.error(f"Duplicate reference name: {reference_name}")
            references[reference_name] = read_series(parser, reference_path)
        token_similarity = None
        if artifact.language.is_cantonese:
            token_similarity = YueTokenSimilarity()

        # Generate report
        try:
            report = audit_transcription_alignment(
                artifact,
                references,
                token_similarity=token_similarity,
                first_index=first_index,
                last_index=last_index,
                first_block=first_block,
                last_block=last_block,
                include_audio_events=include_audio_events,
                include_language=include_language,
                include_merge_support=include_merge_support,
                include_speaker=include_speaker,
                include_timing_tables=include_timing_tables,
            )
        except (ScinoephileError, ValueError) as exc:
            parser.error(str(exc))

        # Write output
        cls.write_report(parser, report, outfile_path, overwrite)


if __name__ == "__main__":
    AuditTranscriptionCli.main()
