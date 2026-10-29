#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CLI for the local, single-language proofreading audit browser."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.cli.helpers.web import (
    WEB_LOCALIZATIONS,
    WebServerArguments,
    add_web_server_args,
)
from scinoephile.common.argument_parsing import (
    enum_arg,
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.web.audit_review.app import serve_audit
from scinoephile.web.audit_review.session import AuditSession

__all__ = ["AuditReviewServeCli"]

AUDIT_REVIEW_SERVE_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "serve the subtitle audit browser": "启动字幕审核网页浏览器",
        "original subtitle SRT file": "原始字幕 SRT 文件",
        "edited SRT file; resume if present": "编辑后字幕 SRT 文件（存在时继续编辑）",
        "optional read/write proofreading decision JSON; created on save": (
            "可选读写校对决策 JSON；保存时创建"
        ),
        "optional Markdown audit notes to import": "可选导入的 Markdown 审核备注",
        "subtitle language (default: auto-detect)": "字幕语言（默认：从输入检测）",
        "display title (default: input filename stem)": "显示标题（默认：输入文件名）",
        "audit web UI must use a loopback host": "审核网页界面必须使用本机回环地址",
    },
    "zh-hant": {
        "serve the subtitle audit browser": "啟動字幕稽核網頁瀏覽器",
        "original subtitle SRT file": "原始字幕 SRT 檔",
        "edited SRT file; resume if present": "編輯後字幕 SRT 檔（存在時繼續編輯）",
        "optional read/write proofreading decision JSON; created on save": (
            "可選讀寫校對決策 JSON；儲存時建立"
        ),
        "optional Markdown audit notes to import": "可選匯入的 Markdown 稽核備註",
        "subtitle language (default: auto-detect)": "字幕語言（預設：從輸入偵測）",
        "display title (default: input filename stem)": "顯示標題（預設：輸入檔名）",
        "audit web UI must use a loopback host": "稽核網頁介面必須使用本機回環位址",
    },
}
"""Translations for the proofreading editor command."""


class AuditReviewServeCli(ScinoephileCliBase):
    """Serve the subtitle audit browser."""

    localizations = merge_localizations(
        WEB_LOCALIZATIONS, AUDIT_REVIEW_SERVE_LOCALIZATIONS
    )
    """Translated CLI descriptions and argument help."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add project input and local web server settings.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)
        groups = get_arg_groups_by_name(
            parser,
            "input arguments",
            "web arguments",
            "output arguments",
            optional_arguments_name="additional arguments",
        )
        groups["input arguments"].add_argument(
            "-i",
            "--infile",
            dest="infile_path",
            required=True,
            type=input_file_arg(),
            help="original subtitle SRT file",
        )
        groups["input arguments"].add_argument(
            "--json",
            dest="json_path",
            type=output_file_arg(exist_ok=True),
            help="optional read/write proofreading decision JSON; created on save",
        )
        groups["input arguments"].add_argument(
            "--audit-notes",
            dest="report_path",
            type=input_file_arg(),
            help="optional Markdown audit notes to import",
        )
        groups["input arguments"].add_argument(
            "--language",
            type=enum_arg(Language),
            help="subtitle language (default: auto-detect)",
        )
        groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            dest="outfile_path",
            required=True,
            type=output_file_arg(exist_ok=True),
            help="edited SRT file; resume if present",
        )
        groups["web arguments"].add_argument(
            "--title", help="display title (default: input filename stem)"
        )
        add_web_server_args(groups["web arguments"])
        parser.set_defaults(web_args=WebServerArguments(port=5020))

    @classmethod
    def name(cls) -> str:
        """Return the audit subcommand name.

        Returns:
            audit subcommand name
        """
        return "serve"

    @classmethod
    def _main(
        cls,
        *,
        infile_path: Path,
        outfile_path: Path,
        web_args: WebServerArguments,
        title: str | None = None,
        json_path: Path | None = None,
        language: Language | None = None,
        report_path: Path | None = None,
        _parser: ArgumentParser | None = None,
    ):
        """Open a source-backed audit project and serve its local UI.

        Arguments:
            infile_path: immutable source subtitles
            outfile_path: edited subtitle output
            web_args: loopback server address and port
            title: display title override
            json_path: optional read/write native proofreading decisions
            language: optional explicit subtitle language
            report_path: optional report used only to seed audit notes
            _parser: parser for user-facing error messages
        """
        parser = _parser or cls.argparser()
        if web_args.host not in {"127.0.0.1", "localhost", "::1"}:
            parser.error("audit web UI must use a loopback host")
        try:
            serve_audit(
                AuditSession(
                    infile_path,
                    outfile_path,
                    json_path=json_path,
                    title=title,
                    language=language,
                    report_path=report_path,
                ),
                host=web_args.host,
                port=web_args.port,
            )
        except (ScinoephileError, OSError) as exc:
            parser.error(str(exc))
