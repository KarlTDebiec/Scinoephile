#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for extracting subtitle streams from media."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.cli.cache.argument_types import cache_dir_path_arg
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_dir_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.argument_types import language_arg
from scinoephile.media.constants import DEFAULT_SUBTITLE_LANGUAGES
from scinoephile.workflows.subtitle_extraction import (
    SubtitleExtractionOutputKind,
    SubtitleExtractionOutputStatus,
    SubtitleExtractionResult,
    extract_subtitles,
)

__all__ = ["MediaExtractSubsCli"]


class MediaExtractSubsCli(ScinoephileCliBase):
    """Extract matching subtitle streams from a video file."""

    localizations = {
        "zh-hans": {
            "convert extracted SUP subtitle streams to image directories": (
                "将提取的 SUP 字幕流转换为图像目录"
            ),
            "cache directory (default: %(default)s)": "缓存目录（默认：%(default)s）",
            "directory to which matching subtitles will be extracted or mapped": (
                "匹配字幕将被提取或映射到的目录"
            ),
            "extract matching subtitle streams from a video file": (
                "从视频文件提取匹配的字幕流"
            ),
            "include additional subtitle stream details": "包含更多字幕流详细信息",
            "ISO 639 language codes to extract (default: chi eng yue zho)": (
                "要提取的 ISO 639 语言代码（默认：chi eng yue zho）"
            ),
            "overwrite extracted subtitle files if they exist": (
                "若提取的字幕文件已存在则覆盖"
            ),
            "video infile containing subtitle streams": "包含字幕流的视频输入文件",
        },
        "zh-hant": {
            "convert extracted SUP subtitle streams to image directories": (
                "將提取的 SUP 字幕流轉換為影像目錄"
            ),
            "cache directory (default: %(default)s)": "快取目錄（預設：%(default)s）",
            "directory to which matching subtitles will be extracted or mapped": (
                "匹配字幕將被提取或映射到的目錄"
            ),
            "extract matching subtitle streams from a video file": (
                "從影片檔提取匹配的字幕流"
            ),
            "include additional subtitle stream details": "包含更多字幕流詳細資訊",
            "ISO 639 language codes to extract (default: chi eng yue zho)": (
                "要提取的 ISO 639 語言代碼（預設：chi eng yue zho）"
            ),
            "overwrite extracted subtitle files if they exist": (
                "若提取的字幕檔已存在則覆寫"
            ),
            "video infile containing subtitle streams": "包含字幕流的影片輸入檔",
        },
    }
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
            "--infile",
            dest="infile_path",
            required=True,
            type=input_file_arg(),
            help="video infile containing subtitle streams",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--languages",
            default=list(DEFAULT_SUBTITLE_LANGUAGES),
            nargs="+",
            type=language_arg,
            help="ISO 639 language codes to extract (default: chi eng yue zho)",
        )
        arg_groups["operation arguments"].add_argument(
            "--details",
            action="store_true",
            help="include additional subtitle stream details",
        )
        arg_groups["operation arguments"].add_argument(
            "--cache-dir",
            default=cache_dir_path_arg("media", "subtitles"),
            dest="cache_dir_path",
            type=cache_dir_path_arg,
            help="cache directory (default: %(default)s)",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--output-dir",
            dest="output_dir_path",
            required=True,
            type=output_dir_arg(create=False),
            help="directory to which matching subtitles will be extracted or mapped",
        )
        arg_groups["output arguments"].add_argument(
            "--extract-sup",
            action="store_true",
            help="convert extracted SUP subtitle streams to image directories",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite extracted subtitle files if they exist",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "extract-subs"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        infile_path: Path,
        languages: list[str],
        details: bool,
        cache_dir_path: Path,
        extract_sup: bool,
        overwrite: bool,
        output_dir_path: Path,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()
        try:
            result = extract_subtitles(
                infile_path=infile_path,
                languages=languages,
                output_dir_path=output_dir_path,
                cache_dir_path=cache_dir_path,
                details=details,
                extract_sup=extract_sup,
                overwrite=overwrite,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))
        cls._print_result(result)

    @classmethod
    def _print_result(cls, result: SubtitleExtractionResult):
        """Print a subtitle extraction result.

        Arguments:
            result: subtitle extraction result
        """
        status_labels = {
            SubtitleExtractionOutputStatus.CREATED: "Created",
            SubtitleExtractionOutputStatus.EXISTED: "Already existed",
            SubtitleExtractionOutputStatus.OVERWRITTEN: "Overwritten",
        }
        kind_labels = {
            SubtitleExtractionOutputKind.SUBTITLE: "subtitle",
            SubtitleExtractionOutputKind.IMAGE_SERIES: "image series",
        }
        for status, status_label in status_labels.items():
            outputs = [output for output in result.outputs if output.status == status]
            if not outputs:
                continue
            print(f"{status_label}:")
            for output in outputs:
                print(
                    f"  {kind_labels[output.kind]}: "
                    f"{output.stream.description} -> {output.path}"
                )


if __name__ == "__main__":
    MediaExtractSubsCli.main()
