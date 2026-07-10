#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for OCR processing."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.cli.helpers.cache import CACHE_LOCALIZATIONS, add_cache_dir_arg
from scinoephile.cli.helpers.llms import (
    LLM_LOCALIZATIONS,
    LlmArguments,
    add_llm_provider_args,
    read_llm_additional_context,
)
from scinoephile.cli.helpers.web import (
    WEB_LOCALIZATIONS,
    WebServerArguments,
    add_web_server_args,
)
from scinoephile.common.argument_parsing import (
    enum_arg,
    enum_metavar,
    get_arg_groups_by_name,
    input_file_or_dir_arg,
    int_arg,
    output_dir_arg,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.llms.providers.registry import get_provider
from scinoephile.workflows.ocr_processing import (
    OcrProcessingResult,
    OcrProcessingWorkflow,
)

__all__ = ["OcrProcessCli"]

OCR_PROCESS_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "cache directory for extracted media subtitle artifacts (default: "
        "%(default)s)": "提取媒体字幕产物的缓存目录（默认：%(default)s）",
        "clean OCR subtitle outputs before fusing": "在融合前清理 OCR 字幕输出",
        "directory where OCR processing outputs will be written": (
            "写入 OCR 处理输出的目录"
        ),
        "image subtitle or media infile path": "图像字幕或媒体输入文件路径",
        "launch the local OCR validation web UI": "启动本地 OCR 校验网页界面",
        "language of the OCR text to process": "要处理的 OCR 文本语言",
        "maintainer option: write validation data updates to repo data": (
            "维护者选项：将校验数据更新写入仓库数据"
        ),
        "media subtitle stream index when infile is media": (
            "输入文件为媒体时的字幕流索引"
        ),
        "overwrite existing OCR processing outputs": "覆盖现有 OCR 处理输出",
        "process image subtitle OCR and fuse output for a selected language": (
            "处理图像字幕 OCR 并融合所选语言的输出"
        ),
        "Processed OCR outputs:": "已处理的 OCR 输出：",
    },
    "zh-hant": {
        "cache directory for extracted media subtitle artifacts (default: "
        "%(default)s)": "提取媒體字幕產物的快取目錄（預設：%(default)s）",
        "clean OCR subtitle outputs before fusing": "在融合前清理 OCR 字幕輸出",
        "directory where OCR processing outputs will be written": (
            "寫入 OCR 處理輸出的目錄"
        ),
        "image subtitle or media infile path": "影像字幕或媒體輸入檔案路徑",
        "launch the local OCR validation web UI": "啟動本機 OCR 驗證網頁介面",
        "language of the OCR text to process": "要處理的 OCR 文字語言",
        "maintainer option: write validation data updates to repo data": (
            "維護者選項：將驗證資料更新寫入儲存庫資料"
        ),
        "media subtitle stream index when infile is media": (
            "輸入檔案為媒體時的字幕流索引"
        ),
        "overwrite existing OCR processing outputs": "覆寫現有 OCR 處理輸出",
        "process image subtitle OCR and fuse output for a selected language": (
            "處理影像字幕 OCR 並融合所選語言的輸出"
        ),
        "Processed OCR outputs:": "已處理的 OCR 輸出：",
    },
}
"""Localized help text keyed by locale and English source text."""


class OcrProcessCli(ScinoephileCliBase):
    """Process image subtitle OCR and fuse output for a selected language."""

    localizations = merge_localizations(
        CACHE_LOCALIZATIONS,
        LLM_LOCALIZATIONS,
        WEB_LOCALIZATIONS,
        OCR_PROCESS_LOCALIZATIONS,
    )
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
            "llm arguments",
            "web arguments",
            "output arguments",
            "additional help",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--infile",
            dest="infile_path",
            required=True,
            type=input_file_or_dir_arg(),
            help="image subtitle or media infile path",
        )
        arg_groups["input arguments"].add_argument(
            "--stream-index",
            type=int_arg(min_value=0),
            help="media subtitle stream index when infile is media",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--language",
            required=True,
            metavar=enum_metavar(Language),
            type=enum_arg(Language),
            help="language of the OCR text to process",
        )
        arg_groups["operation arguments"].add_argument(
            "--clean",
            action="store_true",
            help="clean OCR subtitle outputs before fusing",
        )
        arg_groups["operation arguments"].add_argument(
            "--dev",
            action="store_true",
            help="maintainer option: write validation data updates to repo data",
        )
        add_cache_dir_arg(
            arg_groups["operation arguments"],
            "media",
            "subtitles",
            help_text=(
                "cache directory for extracted media subtitle artifacts "
                "(default: %(default)s)"
            ),
        )
        add_llm_provider_args(
            arg_groups["llm arguments"], arg_groups["additional help"]
        )

        # Web arguments
        arg_groups["web arguments"].add_argument(
            "--interactive",
            action="store_true",
            help="launch the local OCR validation web UI",
        )
        add_web_server_args(arg_groups["web arguments"])

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--output-dir",
            dest="output_dir_path",
            required=True,
            type=output_dir_arg(create=False),
            help="directory where OCR processing outputs will be written",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite existing OCR processing outputs",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "process"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        infile_path: Path,
        stream_index: int | None,
        language: Language,
        clean: bool,
        interactive: bool,
        web_args: WebServerArguments,
        dev: bool,
        cache_dir_path: Path,
        llm_args: LlmArguments,
        output_dir_path: Path,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        additional_context = read_llm_additional_context(
            parser, llm_args.additional_context_file_path
        )
        provider = get_provider(llm_args.provider_name, model=llm_args.model_name)

        # Perform operations
        try:
            result = OcrProcessingWorkflow(
                infile_path,
                output_dir_path,
                language=language,
                stream_index=stream_index,
                cache_dir_path=cache_dir_path,
                clean=clean,
                interactive=interactive,
                host=web_args.host,
                port=web_args.port,
                dev=dev,
                overwrite=overwrite,
                provider=provider,
                additional_context=additional_context,
            )()
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write outputs
        cls._print_result(result)

    @classmethod
    def _print_result(cls, result: OcrProcessingResult):
        """Print an OCR processing result.

        Arguments:
            result: OCR processing result
        """
        print(cls.translate_text("Processed OCR outputs:"))
        for name, path in result.output_paths.items():
            print(f"  {name}: {path}")


if __name__ == "__main__":
    OcrProcessCli.main()
