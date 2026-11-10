#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Run an independent proofreading audit using an LLM."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path

from scinoephile.cli.helpers.blocks import (
    BLOCK_LOCALIZATIONS,
    add_block_range_args,
    get_block_range_indexes,
)
from scinoephile.cli.helpers.cache import (
    CACHE_LOCALIZATIONS,
    CacheArguments,
    add_cache_args,
)
from scinoephile.cli.helpers.llms import (
    LLM_LOCALIZATIONS,
    LlmArguments,
    add_llm_provider_args,
    read_llm_additional_context,
)
from scinoephile.common.cli.argument_parsing import (
    enum_arg,
    enum_metavar,
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.llms.providers.registry import get_provider
from scinoephile.operations.review_audit.project import ReviewAuditProject
from scinoephile.operations.review_audit.run import run_audit_selection

__all__ = ["AuditReviewRunCli"]

logger = getLogger(__name__)

AUDIT_REVIEW_RUN_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audit subtitle proofreading with an LLM": "使用大语言模型审核字幕校对",
        "original subtitle SRT file before review": "校对前的原始字幕 SRT 文件",
        (
            "proofread SRT output; audit cases are saved beside it as "
            "<reviewed-stem>.audit.json"
        ): ("校对后的 SRT 输出；审核案例保存在同一目录的 <reviewed-stem>.audit.json"),
        "proofreading test-case JSON (default: <reviewed-stem>.review.json)": (
            "校对测试案例 JSON（默认：<reviewed-stem>.review.json）"
        ),
        "subtitle language (default: detected automatically)": (
            "字幕语言（默认：自动检测）"
        ),
        "replace existing audit findings in the selected blocks": (
            "替换所选区块中已有的审核结果"
        ),
    },
    "zh-hant": {
        "audit subtitle proofreading with an LLM": "使用大型語言模型稽核字幕校對",
        "original subtitle SRT file before review": "校對前的原始字幕 SRT 檔",
        (
            "proofread SRT output; audit cases are saved beside it as "
            "<reviewed-stem>.audit.json"
        ): ("校對後的 SRT 輸出；稽核案例儲存在同一目錄的 <reviewed-stem>.audit.json"),
        "proofreading test-case JSON (default: <reviewed-stem>.review.json)": (
            "校對測試案例 JSON（預設：<reviewed-stem>.review.json）"
        ),
        "subtitle language (default: detected automatically)": (
            "字幕語言（預設：自動偵測）"
        ),
        "replace existing audit findings in the selected blocks": (
            "取代所選區塊中已有的稽核結果"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class AuditReviewRunCli(ScinoephileCliBase):
    """Audit subtitle proofreading with an LLM."""

    localizations = merge_localizations(
        AUDIT_REVIEW_RUN_LOCALIZATIONS,
        BLOCK_LOCALIZATIONS,
        CACHE_LOCALIZATIONS,
        LLM_LOCALIZATIONS,
    )
    """Localized help text keyed by locale and English source text."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)
        groups = get_arg_groups_by_name(
            parser,
            "input arguments",
            "operation arguments",
            "llm arguments",
            "cache arguments",
            "additional help",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        groups["input arguments"].add_argument(
            "--original",
            dest="original_path",
            required=True,
            type=input_file_arg(),
            help="original subtitle SRT file before review",
        )
        groups["input arguments"].add_argument(
            "--reviewed",
            dest="reviewed_path",
            required=True,
            type=output_file_arg(exist_ok=True, create=False),
            help=(
                "proofread SRT output; audit cases are saved beside it as "
                "<reviewed-stem>.audit.json"
            ),
        )
        groups["input arguments"].add_argument(
            "--json",
            dest="json_path",
            type=output_file_arg(exist_ok=True, create=False),
            help="proofreading test-case JSON (default: <reviewed-stem>.review.json)",
        )

        # Operation arguments
        groups["operation arguments"].add_argument(
            "--language",
            metavar=enum_metavar(Language),
            type=enum_arg(Language),
            help="subtitle language (default: detected automatically)",
        )
        groups["operation arguments"].add_argument(
            "--rerun",
            action="store_true",
            help="replace existing audit findings in the selected blocks",
        )
        add_block_range_args(groups["operation arguments"])

        # LLM arguments
        add_llm_provider_args(
            groups["llm arguments"], groups["additional help"], allow_no_op=False
        )

        # Cache arguments
        add_cache_args(groups["cache arguments"])
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Return the audit subcommand name.

        Returns:
            audit subcommand name
        """
        return "run"

    @classmethod
    def _main(
        cls,
        *,
        original_path: Path,
        reviewed_path: Path,
        json_path: Path | None,
        language: Language | None,
        first_block: int | None,
        last_block: int | None,
        rerun: bool,
        llm_args: LlmArguments,
        cache_args: CacheArguments,
        _parser: ArgumentParser | None = None,
    ):
        """Run an audit and persist its findings block by block.

        Arguments:
            original_path: original SRT file
            reviewed_path: proofread SRT file
            json_path: optional override for the native proofreading JSON
            language: optional explicit subtitle language
            first_block: first source block to audit
            last_block: last source block to audit
            rerun: replace existing findings for the selected blocks
            llm_args: LLM configuration
            cache_args: cache configuration
            _parser: parser for user-facing errors
        """
        parser = _parser or cls.argparser()
        additional_context = read_llm_additional_context(
            parser, llm_args.additional_context_file_path
        )
        try:
            audit = ReviewAuditProject(
                original_path, reviewed_path, json_path=json_path, language=language
            )
            start_at_idx, stop_at_idx = get_block_range_indexes(
                parser, first_block, last_block, audit.block_count
            )
            provider = get_provider(llm_args.provider_name, **llm_args.provider_kwargs)
            audited_blocks = run_audit_selection(
                audit,
                provider,
                start_at_idx=start_at_idx,
                stop_at_idx=stop_at_idx,
                rerun=rerun,
                additional_context=additional_context,
                cache_root_path=cache_args.root_path,
                overwrite_cache=cache_args.overwrite,
            )
        except (OSError, ScinoephileError, ValueError) as exc:
            parser.error(str(exc))
        logger.info(
            f"Audited {audited_blocks} blocks. "
            f"Saved findings to {audit.audit_json_path}"
        )


if __name__ == "__main__":
    AuditReviewRunCli.main()
