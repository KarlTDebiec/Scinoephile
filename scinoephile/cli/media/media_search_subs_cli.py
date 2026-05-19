#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for OpenSubtitles subtitle search."""

from __future__ import annotations

from argparse import ArgumentParser
from os import getenv
from pathlib import Path

from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    int_arg,
    output_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.argument_types import language_arg
from scinoephile.media.subtitles.opensubtitles import (
    OpenSubtitlesClient,
    OpenSubtitlesFile,
)

__all__ = ["MediaSearchSubsCli"]


class MediaSearchSubsCli(ScinoephileCliBase):
    """Search and download OpenSubtitles subtitle files."""

    localizations = {
        "zh-hans": {
            "command-line interface for OpenSubtitles subtitle search": (
                "OpenSubtitles 字幕搜索命令行界面"
            ),
            "downloaded subtitle output file": "下载字幕输出文件",
            "maximum number of subtitle files to display (default: %(default)s)": (
                "要显示的字幕文件最大数量（默认：%(default)s）"
            ),
            "OpenSubtitles API key": "OpenSubtitles API 密钥",
            "OpenSubtitles file_id to download": "要下载的 OpenSubtitles file_id",
            "OpenSubtitles password": "OpenSubtitles 密码",
            "OpenSubtitles search query": "OpenSubtitles 搜索查询",
            "OpenSubtitles username": "OpenSubtitles 用户名",
            "overwrite downloaded subtitle file if it exists": (
                "若下载的字幕文件已存在则覆盖"
            ),
            "search and download OpenSubtitles subtitle files": (
                "搜索并下载 OpenSubtitles 字幕文件"
            ),
            "subtitle language code": "字幕语言代码",
        },
        "zh-hant": {
            "command-line interface for OpenSubtitles subtitle search": (
                "OpenSubtitles 字幕搜尋命令列介面"
            ),
            "downloaded subtitle output file": "下載字幕輸出檔",
            "maximum number of subtitle files to display (default: %(default)s)": (
                "要顯示的字幕檔最大數量（預設：%(default)s）"
            ),
            "OpenSubtitles API key": "OpenSubtitles API 金鑰",
            "OpenSubtitles file_id to download": "要下載的 OpenSubtitles file_id",
            "OpenSubtitles password": "OpenSubtitles 密碼",
            "OpenSubtitles search query": "OpenSubtitles 搜尋查詢",
            "OpenSubtitles username": "OpenSubtitles 使用者名稱",
            "overwrite downloaded subtitle file if it exists": (
                "若下載的字幕檔已存在則覆寫"
            ),
            "search and download OpenSubtitles subtitle files": (
                "搜尋並下載 OpenSubtitles 字幕檔"
            ),
            "subtitle language code": "字幕語言代碼",
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
            "--query",
            required=True,
            help="OpenSubtitles search query",
        )
        arg_groups["input arguments"].add_argument(
            "--language",
            required=True,
            type=language_arg,
            help="subtitle language code",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--api-key",
            default=getenv("OPENSUBTITLES_API_KEY"),
            help="OpenSubtitles API key",
        )
        arg_groups["operation arguments"].add_argument(
            "--username",
            default=getenv("OPENSUBTITLES_USERNAME"),
            help="OpenSubtitles username",
        )
        arg_groups["operation arguments"].add_argument(
            "--password",
            default=getenv("OPENSUBTITLES_PASSWORD"),
            help="OpenSubtitles password",
        )
        arg_groups["operation arguments"].add_argument(
            "--limit",
            default=10,
            type=int_arg(min_value=1),
            help="maximum number of subtitle files to display (default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--file-id",
            dest="file_id",
            type=int_arg(min_value=1),
            help="OpenSubtitles file_id to download",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            dest="outfile_path",
            type=output_file_arg(exist_ok=True, create=False),
            help="downloaded subtitle output file",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite downloaded subtitle file if it exists",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "search-subs"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        query: str,
        language: str,
        api_key: str | None,
        username: str | None,
        password: str | None,
        limit: int,
        file_id: int | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()
        if outfile_path is not None and file_id is None:
            parser.error("--outfile may only be used with --file-id")
        if file_id is not None and outfile_path is None:
            parser.error("--file-id may only be used with --outfile")
        if overwrite and outfile_path is None:
            parser.error("--overwrite may only be used with --outfile")

        client = OpenSubtitlesClient(api_key=api_key)
        try:
            results = client.search(query=query, language=language, limit=limit)
            if not results:
                raise ScinoephileError("No OpenSubtitles files found")
            if outfile_path is None:
                cls._print_results(results)
            else:
                if file_id is None:
                    raise ValueError("file_id must be set when outfile_path is set")
                if not any(result.file_id == file_id for result in results):
                    raise ScinoephileError(
                        f"OpenSubtitles file_id {file_id} was not found in results"
                    )
                client.download(
                    file_id=file_id,
                    outfile_path=outfile_path,
                    username=username,
                    password=password,
                    overwrite=overwrite,
                )
        except ScinoephileError as exc:
            parser.error(str(exc))

    @classmethod
    def _print_results(cls, results: list[OpenSubtitlesFile]):
        """Print OpenSubtitles search results.

        Arguments:
            results: OpenSubtitles file results
        """
        print("file_id\tlang\tdownloads\trating\tfps\trelease/file")
        for result in results:
            row = [
                str(result.file_id),
                result.language or "",
                "" if result.download_count is None else str(result.download_count),
                "" if result.rating is None else str(result.rating),
                "" if result.fps is None else str(result.fps),
                result.release_name or result.file_name or "",
            ]
            print("\t".join(row))


if __name__ == "__main__":
    MediaSearchSubsCli.main()
