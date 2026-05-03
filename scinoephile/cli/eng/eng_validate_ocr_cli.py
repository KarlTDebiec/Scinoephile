#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for English OCR subtitle validation."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import ClassVar, Unpack

from scinoephile.common import CLIKwargs, DirectoryNotFoundError
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    int_arg,
    output_dir_arg,
)
from scinoephile.common.exception import NotAFileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng.ocr_validation import validate_eng_ocr

__all__ = ["EngValidateOcrCli"]


class EngValidateOcrCli(ScinoephileCliBase):
    """Validate OCR text against subtitle images."""

    localizations: ClassVar[dict[str, dict[str, str]]] = {
        "zh-hans": {
            "command-line interface for English OCR subtitle validation": (
                "英文 OCR 字幕校验命令行界面"
            ),
            "directory in which to save validation image outputs": (
                "保存校验图像输出的目录"
            ),
            "prompt for interactive validation decisions": "提示进行交互式校验决策",
            "stop validation after this subtitle index": "在此字幕索引后停止校验",
            "validate OCR text against subtitle images": "对照字幕图像校验 OCR 文本",
        },
        "zh-hant": {
            "command-line interface for English OCR subtitle validation": (
                "英文 OCR 字幕驗證命令列介面"
            ),
            "directory in which to save validation image outputs": (
                "儲存驗證影像輸出的目錄"
            ),
            "prompt for interactive validation decisions": "提示進行互動式驗證決策",
            "stop validation after this subtitle index": "在此字幕索引後停止驗證",
            "validate OCR text against subtitle images": "對照字幕影像驗證 OCR 文字",
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
            "-i",
            "--infile",
            required=True,
            type=Path,
            help=(
                "English OCR image subtitle infile path "
                "(directory containing index.html and png files, or a .sup file)"
            ),
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--stop-at-idx",
            type=int_arg(min_value=0),
            help="stop validation after this subtitle index",
        )
        arg_groups["operation arguments"].add_argument(
            "--interactive",
            action="store_true",
            help="prompt for interactive validation decisions",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            required=True,
            type=output_dir_arg(create=False),
            help="directory in which to save validation image outputs",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile directory if it exists",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "validate-ocr"

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        # Validate arguments
        parser = kwargs.pop("_parser", cls.argparser())
        infile_path = kwargs.pop("infile")
        stop_at_idx = kwargs.pop("stop_at_idx")
        interactive = kwargs.pop("interactive")
        outfile_path: Path = kwargs.pop("outfile")
        overwrite = kwargs.pop("overwrite")
        if outfile_path.exists() and not overwrite:
            parser.error(f"{outfile_path} already exists")

        # Read input
        try:
            series = ImageSeries.load(infile_path)
        except (
            DirectoryNotFoundError,
            FileNotFoundError,
            NotADirectoryError,
            NotAFileError,
            ValueError,
        ) as exc:
            parser.error(str(exc))

        # Perform operations
        validated = validate_eng_ocr(
            series,
            stop_at_idx=stop_at_idx,
            interactive=interactive,
        )

        # Write output
        validated.save(outfile_path)


if __name__ == "__main__":
    EngValidateOcrCli.main()
