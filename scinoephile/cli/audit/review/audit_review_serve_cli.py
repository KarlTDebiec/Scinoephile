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
from scinoephile.common.cli.argument_parsing import (
    enum_arg,
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.operations.review_audit.project import ReviewAuditProject
from scinoephile.web.audit_review.app import serve_audit

__all__ = ["AuditReviewServeCli"]

AUDIT_REVIEW_SERVE_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "start the local subtitle audit editor": "启动本地字幕审核编辑器",
        (
            "Requires the 'web' extra. Default address: http://127.0.0.1:5020/. "
            "Proofreading and auditing make model requests only when started "
            "in the browser."
        ): (
            "需要安装 'web' 可选依赖。默认地址：http://127.0.0.1:5020/。"
            "只有在浏览器中启动校对或审核时才会请求语言模型。"
        ),
        "original subtitle SRT file (read-only)": "原始字幕 SRT 文件（只读）",
        "proofread SRT output": "校对后的 SRT 输出",
        "proofreading JSON file (created if missing)": "校对 JSON 文件（不存在时创建）",
        "audit JSON file (created if missing)": "审核 JSON 文件（不存在时创建）",
        "subtitle language (default: saved audit language or auto-detect)": (
            "字幕语言（默认：使用已保存的审核语言，否则自动检测）"
        ),
        "audit web UI must use a loopback host": "审核网页界面必须使用本机回环地址",
    },
    "zh-hant": {
        "start the local subtitle audit editor": "啟動本機字幕稽核編輯器",
        (
            "Requires the 'web' extra. Default address: http://127.0.0.1:5020/. "
            "Proofreading and auditing make model requests only when started "
            "in the browser."
        ): (
            "需要安裝 'web' 選用相依套件。預設網址：http://127.0.0.1:5020/。"
            "只有在瀏覽器中啟動校對或稽核時才會請求語言模型。"
        ),
        "original subtitle SRT file (read-only)": "原始字幕 SRT 檔（唯讀）",
        "proofread SRT output": "校對後的 SRT 輸出",
        "proofreading JSON file (created if missing)": "校對 JSON 檔（不存在時建立）",
        "audit JSON file (created if missing)": "稽核 JSON 檔（不存在時建立）",
        "subtitle language (default: saved audit language or auto-detect)": (
            "字幕語言（預設：使用已儲存的稽核語言，否則自動偵測）"
        ),
        "audit web UI must use a loopback host": "稽核網頁介面必須使用本機回環位址",
    },
}
"""Translations for the proofreading editor command."""


class AuditReviewServeCli(ScinoephileCliBase):
    """Start the local subtitle audit editor.

    Requires the 'web' extra. Default address: http://127.0.0.1:5020/.
    Proofreading and auditing make model requests only when started in the browser.
    """

    localizations = merge_localizations(
        WEB_LOCALIZATIONS, AUDIT_REVIEW_SERVE_LOCALIZATIONS
    )
    """Translated CLI descriptions and argument help."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add project input and local web server settings.

        Arguments:
            parser: parser to configure
        """
        super().add_arguments_to_argparser(parser)
        groups = get_arg_groups_by_name(
            parser,
            "input arguments",
            "web arguments",
            "output arguments",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        groups["input arguments"].add_argument(
            "-i",
            "--infile",
            dest="infile_path",
            required=True,
            type=input_file_arg(),
            help="original subtitle SRT file (read-only)",
        )
        groups["input arguments"].add_argument(
            "--proofreading-json",
            dest="proofreading_json_path",
            required=True,
            type=output_file_arg(exist_ok=True, create=False),
            help="proofreading JSON file (created if missing)",
        )
        groups["input arguments"].add_argument(
            "--audit-json",
            dest="audit_json_path",
            required=True,
            type=output_file_arg(exist_ok=True, create=False),
            help="audit JSON file (created if missing)",
        )
        groups["input arguments"].add_argument(
            "--language",
            type=enum_arg(Language),
            help="subtitle language (default: saved audit language or auto-detect)",
        )

        # Web arguments
        add_web_server_args(groups["web arguments"])
        parser.set_defaults(web_args=WebServerArguments(port=5020))

        # Output arguments
        groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            dest="outfile_path",
            required=True,
            type=output_file_arg(exist_ok=True, create=False),
            help="proofread SRT output",
        )

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
        proofreading_json_path: Path,
        audit_json_path: Path,
        web_args: WebServerArguments,
        language: Language | None = None,
        _parser: ArgumentParser | None = None,
    ):
        """Open the subtitle project and start its local editor.

        Arguments:
            infile_path: immutable source subtitles
            outfile_path: edited subtitle output
            proofreading_json_path: proofreading test-case file
            audit_json_path: audit test-case file
            web_args: loopback server address and port
            language: optional explicit subtitle language
            _parser: parser for user-facing error messages
        """
        parser = _parser or cls.argparser()
        if web_args.host not in {"127.0.0.1", "localhost", "::1"}:
            parser.error("audit web UI must use a loopback host")
        try:
            serve_audit(
                ReviewAuditProject(
                    infile_path,
                    outfile_path,
                    proofreading_json_path=proofreading_json_path,
                    audit_json_path=audit_json_path,
                    language=language,
                ),
                title=web_args.title,
                host=web_args.host,
                port=web_args.port,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))
