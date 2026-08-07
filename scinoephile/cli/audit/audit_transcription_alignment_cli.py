#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for multi-source transcription alignment audits."""

from __future__ import annotations

from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path

from pydantic import ValidationError

from scinoephile.analysis.audit.transcription_alignment import (
    audit_transcription_alignment,
)
from scinoephile.analysis.transcription_alignment import TranscriptionAlignmentArtifact
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import get_arg_groups_by_name, input_file_arg
from scinoephile.core import Language
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.lang.transcription.multisource_alignment import (
    CantoneseTimedTokenSimilarity,
)

from .audit_cli_base import AuditCliBase

__all__ = ["AuditTranscriptionAlignmentCli"]

AUDIT_TRANSCRIPTION_ALIGNMENT_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audit aligned multi-source transcription evidence": ("审核多来源转写对齐证据"),
        "transcription alignment artifact JSON file": "转写对齐成品 JSON 文件",
        "named reference subtitle as NAME=PATH; repeat for multiple references": (
            "命名的独立参考字幕，格式为名称=路径；多个参考字幕可重复使用"
        ),
        "include the speaker annotation row": "包含说话者标注行",
        "include the spoken-language annotation row": "包含口语语言标注行",
        "include the merged-character source-support row": ("包含合并字符的来源支持行"),
        "include the singing and music annotation rows": "包含歌唱和音乐标注行",
        "include detailed subtitle and reference timing tables": (
            "包含详细的字幕和参考时间表"
        ),
    },
    "zh-hant": {
        "audit aligned multi-source transcription evidence": ("稽核多來源轉寫對齊證據"),
        "transcription alignment artifact JSON file": "轉寫對齊成品 JSON 檔",
        "named reference subtitle as NAME=PATH; repeat for multiple references": (
            "具名的獨立參考字幕，格式為名稱=路徑；多個參考字幕可重複使用"
        ),
        "include the speaker annotation row": "包含說話者標註列",
        "include the spoken-language annotation row": "包含口語語言標註列",
        "include the merged-character source-support row": ("包含合併字符的來源支持列"),
        "include the singing and music annotation rows": "包含歌唱和音樂標註列",
        "include detailed subtitle and reference timing tables": (
            "包含詳細的字幕和參考時間表"
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
            action="append",
            dest="reference_specs",
            metavar="NAME=PATH",
            type=_named_reference_arg,
            help=(
                "named reference subtitle as NAME=PATH; repeat for multiple references"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--include-speaker",
            action="store_true",
            help="include the speaker annotation row",
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
            "--include-audio-events",
            action="store_true",
            help="include the singing and music annotation rows",
        )
        arg_groups["operation arguments"].add_argument(
            "--include-timing",
            action="store_true",
            dest="include_timing_tables",
            help="include detailed subtitle and reference timing tables",
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
        reference_specs: list[tuple[str, Path]] | None,
        first_index: int | None,
        last_index: int | None,
        first_block: int | None,
        last_block: int | None,
        include_speaker: bool,
        include_language: bool,
        include_merge_support: bool,
        include_audio_events: bool,
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
            include_speaker: whether to render the speaker annotation row
            include_language: whether to render the spoken-language annotation row
            include_merge_support: whether to render merged-character source support
            include_audio_events: whether to render singing and music rows
            include_timing_tables: whether to render detailed timing tables
            outfile_path: optional Markdown output path
            overwrite: whether to overwrite an existing output file
        """
        parser = _parser or cls.argparser()
        try:
            artifact = TranscriptionAlignmentArtifact.load(alignment_path)
        except (OSError, UnicodeError, ValueError, ValidationError) as exc:
            parser.error(f"Unable to load transcription alignment artifact: {exc}")
        references = {}
        for reference_name, reference_path in reference_specs or ():
            if reference_name in references:
                parser.error(f"Duplicate reference name: {reference_name}")
            references[reference_name] = read_series(parser, reference_path)
        reference_similarity = None
        if artifact.language in {Language.yue_hans, Language.yue_hant}:
            reference_similarity = CantoneseTimedTokenSimilarity(
                timing_weight=4.0, timing_tolerance_seconds=0.75
            )
        try:
            report = audit_transcription_alignment(
                artifact,
                references,
                reference_similarity=reference_similarity,
                first_index=first_index,
                last_index=last_index,
                first_block=first_block,
                last_block=last_block,
                include_speaker=include_speaker,
                include_language=include_language,
                include_merge_support=include_merge_support,
                include_audio_events=include_audio_events,
                include_timing_tables=include_timing_tables,
            )
        except (ScinoephileError, ValueError) as exc:
            parser.error(str(exc))
        cls.write_report(parser, report, outfile_path, overwrite)


def _named_reference_arg(value: str) -> tuple[str, Path]:
    """Parse one named reference argument in NAME=PATH form."""
    name, separator, raw_path = value.partition("=")
    if not separator or not name.strip() or not raw_path.strip():
        raise ArgumentTypeError("references must use nonblank NAME=PATH syntax")
    reference_path = input_file_arg()(raw_path)
    if not isinstance(reference_path, Path):
        raise ArgumentTypeError("reference path must identify one input file")
    return name, reference_path


if __name__ == "__main__":
    AuditTranscriptionAlignmentCli.main()
