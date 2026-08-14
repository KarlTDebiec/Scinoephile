#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM query execution."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path

from pydantic import ValidationError

from scinoephile.core.exceptions import ScinoephileError

from .cache import LlmCache
from .llm_provider import LLMProvider
from .metrics import ChatCompletionMetrics
from .query import Query
from .test_case import TestCase
from .tool_box import ToolBox

__all__ = ["Queryer"]

logger = getLogger(__name__)


class Queryer[TTestCase: TestCase]:
    """Execute LLM queries using one test-case class."""

    def __init__(
        self,
        test_case_cls: type[TTestCase],
        verified_test_cases: list[TestCase] | None = None,
        *,
        provider: LLMProvider,
        cache_root_path: Path | None = None,
        additional_context: str | None = None,
        max_attempts: int = 5,
        auto_verify: bool = False,
        no_op: bool = False,
        overwrite_cache: bool = False,
        tool_box: ToolBox | None = None,
    ):
        """Initialize.

        Arguments:
            test_case_cls: class defining queries, verified answers, and prompt text
            verified_test_cases: test cases whose answers are verified and for which
              LLM need not be queried
            provider: provider to use for queries
            cache_root_path: root directory beneath which to cache
            additional_context: additional context to include in the system prompt
            max_attempts: maximum number of attempts
            auto_verify: automatically mark test cases as verified if no changes
            no_op: use neutral answers without reading or writing response caches
            overwrite_cache: whether to replace matching cache files
            tool_box: available tools and handlers
        """
        self.test_case_cls = test_case_cls
        """Class defining queries, answers, and prompt text."""
        self.prompt = test_case_cls.prompt
        """Text for LLM correspondence."""
        self.provider = provider

        self.verified_test_cases = self._get_verified_test_cases(
            verified_test_cases or []
        )
        """Test cases whose answers are verified for which LLM will not be queried."""
        self.few_shot_test_cases = {
            key: test_case
            for key, test_case in self.verified_test_cases.items()
            if test_case.few_shot
        }
        """Test cases included as few-shot examples."""
        self.encountered_test_cases: dict[tuple, TTestCase] = {}
        """Test cases actually encountered."""
        self.completion_metrics: list[ChatCompletionMetrics] = []
        """Provider completions made for test cases encountered by this queryer."""

        self.no_op = no_op
        """Whether neutral answers replace cache access and LLM queries."""
        self._cache: LlmCache | None = None
        if not self.no_op:
            self._cache = LlmCache(
                cache_root_path, self.test_case_cls.operation, overwrite_cache
            )
        """LLM response cache, disabled in no-op mode."""

        self.additional_context = additional_context
        """Additional context to include in the system prompt."""
        self.max_attempts = max_attempts
        """Maximum number of query attempts."""
        self.auto_verify = auto_verify
        """Automatically verify test cases if they meet selected criteria."""
        self.tool_box = tool_box or ToolBox()
        """Available tools and handlers."""
        self.system_prompt = self.prompt.base_system_prompt
        """System prompt shared by all queries executed by this instance."""
        if self.additional_context:
            self.system_prompt += f"\n\n{self.additional_context}"
        self.system_prompt += self.get_few_shot_test_cases_str()

    def __call__(  # noqa: PLR0912, PLR0915
        self, test_case: TestCase
    ) -> TTestCase:
        """Query LLM.

        Arguments:
            test_case: test case containing query for LLM
        Returns:
            test case including LLM's answer
        """
        test_case = self.test_case_cls.model_validate(test_case.model_dump(mode="json"))

        # Load a previously answered test case if available
        if known_test_case := self.get_known_test_case(test_case):
            return known_test_case

        # Produce and log a neutral answer without accessing the response cache
        if self.no_op:
            answer = test_case.get_no_op_answer()
            test_case = self.test_case_cls.model_validate(
                {
                    **test_case.model_dump(mode="json"),
                    "answer": answer.model_dump(mode="json"),
                    "few_shot": False,
                    "verified": False,
                }
            )
            test_case = self.log_encountered_test_case(test_case)
            logger.info(f"Used no-op answer: {test_case.query.key_str}")
            return test_case

        query_json = test_case.query.model_dump_json(by_alias=True, indent=4)
        query_key_sha256 = test_case.query.key_sha256

        # Query provider
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": query_json},
        ]
        for attempt in range(1, self.max_attempts + 1):
            # Get answer from provider
            initial_completion_count = len(self.provider.completion_metrics)
            try:
                content = self.provider.chat_completion(
                    messages,
                    self.test_case_cls.answer_cls,
                    self.tool_box,
                    operation=self.test_case_cls.operation,
                    query_key_sha256=query_key_sha256,
                    query_attempt=attempt,
                )
            except ScinoephileError as exc:
                logger.error(f"Attempt {attempt} failed: {type(exc).__name__}: {exc}")
                if attempt == self.max_attempts:
                    raise
                continue
            finally:
                self.completion_metrics.extend(
                    self.provider.completion_metrics[initial_completion_count:]
                )

            # Validate answer
            try:
                answer = self.test_case_cls.answer_cls.model_validate_json(
                    content,
                    by_alias=True,
                    by_name=False,
                    strict=True,
                    extra="forbid",
                    context={"alias_only": True},
                )
            except ValidationError as exc:
                logger.error(
                    f"Query:\n{test_case.query}\n"
                    f"Yielded invalid content (attempt {attempt}):\n{content}\n"
                    f"Validation errors:\n{self._format_validation_errors(exc)}"
                )
                if attempt == self.max_attempts:
                    raise
                validation_errors = self._get_prompt_validation_errors(exc)
                messages.append({"role": "assistant", "content": content})
                messages.append(
                    {
                        "role": "user",
                        "content": "\n".join(
                            (
                                self.prompt.answer_invalid_pre,
                                *validation_errors,
                                self.prompt.answer_invalid_post,
                            )
                        ),
                    }
                )
                continue

            # Validate test case
            try:
                test_case = self.test_case_cls.model_validate(
                    {
                        **test_case.model_dump(),
                        "answer": answer,
                        "few_shot": False,
                        "verified": False,
                    }
                )
                if self.auto_verify and test_case.get_auto_verified():
                    test_case.verified = True
            except ValidationError as exc:
                logger.error(
                    f"Query:\n{test_case.query}\n"
                    f"Yielded invalid answer (attempt {attempt}):\n{answer}\n"
                    f"Validation errors:\n{self._format_validation_errors(exc)}"
                )
                if attempt == self.max_attempts:
                    raise
                validation_errors = self._get_prompt_validation_errors(exc)
                messages.append({"role": "assistant", "content": content})
                messages.append(
                    {
                        "role": "user",
                        "content": "\n".join(
                            (
                                self.prompt.test_case_invalid_pre,
                                *validation_errors,
                                self.prompt.test_case_invalid_post,
                            )
                        ),
                    }
                )
                continue
            break
        if test_case.answer is None:
            raise ScinoephileError("Unable to obtain valid answer")

        return self.store_answered_test_case(test_case)

    def get_few_shot_test_cases_str(self) -> str:
        """String representation of all test cases in the log."""
        if not self.few_shot_test_cases:
            return ""
        few_shot = f"\n\n{self.prompt.few_shot_intro}"
        for test_case in self.few_shot_test_cases.values():
            assert test_case.answer is not None
            few_shot += f"\n\n{self.prompt.few_shot_query_intro}\n"
            few_shot += test_case.query.model_dump_json(by_alias=True, indent=4)
            few_shot += f"\n{self.prompt.few_shot_answer_intro}\n"
            few_shot += test_case.answer.model_dump_json(by_alias=True, indent=4)
        return few_shot

    def get_known_test_case(self, test_case: TestCase) -> TTestCase | None:
        """Get a verified or response-cached test case without querying the LLM.

        Arguments:
            test_case: test case containing the query to look up
        Returns:
            previously answered test case if available, else None
        """
        normalized = self.test_case_cls.model_validate(
            test_case.model_dump(mode="json")
        )
        if verified_test_case := self._get_verified_test_case(normalized.query):
            return verified_test_case
        if self._cache is None:
            return None

        query_json = normalized.query.model_dump_json(by_alias=True, indent=4)
        tools_json = self.tool_box.to_json()
        return self._get_cached_test_case(
            normalized, self.system_prompt, tools_json, query_json
        )

    def log_encountered_test_case(self, test_case: TestCase) -> TTestCase:
        """Log a test case as having been encountered.

        Arguments:
            test_case: test case to log
        Returns:
            normalized logged test case
        """
        normalized = self.test_case_cls.model_validate(
            test_case.model_dump(mode="json")
        )
        key = normalized.query.key
        normalized.few_shot |= key in self.few_shot_test_cases
        normalized.verified |= key in self.verified_test_cases
        self.encountered_test_cases[key] = normalized
        logger.debug(f"Logged test case: {normalized.query.key_str}")
        return normalized

    def store_answered_test_case(self, test_case: TestCase) -> TTestCase:
        """Log an answered test case and store its response under this queryer.

        Arguments:
            test_case: answered test case to normalize and store
        Returns:
            normalized answered test case
        Raises:
            ValueError: if the test case has no answer
        """
        if test_case.answer is None:
            raise ValueError("Cannot store a test case without an answer.")
        normalized = self.log_encountered_test_case(test_case)
        assert normalized.answer is not None
        if self._cache is None:
            return normalized

        query_json = normalized.query.model_dump_json(by_alias=True, indent=4)
        tools_json = self.tool_box.to_json()
        contents = normalized.answer.model_dump_json(exclude_defaults=True, indent=2)
        self._cache.save(
            self._get_cache_identity(),
            self.system_prompt,
            tools_json,
            query_json,
            contents,
        )
        return normalized

    def _get_cache_identity(self) -> dict[str, object]:
        """Get the provider and test-case cache identity."""
        return {
            "provider": self.provider.cache_identity,
            "test_case": {
                "module": self.test_case_cls.__module__,
                "qualname": self.test_case_cls.__qualname__,
            },
        }

    def _get_cached_test_case(
        self, test_case: TTestCase, system_prompt: str, tools_json: str, query_json: str
    ) -> TTestCase | None:
        """Get cached test case for the given query if available.

        Arguments:
            test_case: test case containing query for which to get cached version
            system_prompt: system prompt used for the query
            tools_json: JSON representation of configured tools
            query_json: JSON representation of the query
        Returns:
            cached test case if available, else None
        """
        assert self._cache is not None
        cache_identity = self._get_cache_identity()
        cache_path = self._cache.get_path(
            cache_identity, system_prompt, tools_json, query_json
        )
        contents = self._cache.load(
            cache_identity, system_prompt, tools_json, query_json
        )
        if contents is None:
            return None
        try:
            answer = self.test_case_cls.answer_cls.model_validate_json(contents)
            test_case = self.test_case_cls.model_validate(
                {
                    **test_case.model_dump(mode="json"),
                    "answer": answer,
                    "few_shot": False,
                    "verified": False,
                }
            )
            if self.auto_verify and test_case.get_auto_verified():
                test_case.verified = True
            test_case = self.log_encountered_test_case(test_case)
            return test_case
        except ValidationError as exc:
            logger.error(
                f"Cache content for query {test_case.query.key_str} at "
                f"{cache_path} is invalid: {exc}"
            )
            self._cache.remove(cache_identity, system_prompt, tools_json, query_json)
        return None

    def _get_verified_test_case(self, query: Query) -> TTestCase | None:
        """Get verified test case for the given query if available.

        Arguments:
            query: query for which to get verified test case
        Returns:
            verified test case if available, else None
        """
        if test_case := self.verified_test_cases.get(query.key):
            test_case = self.log_encountered_test_case(test_case)
            logger.info(f"Loaded from verified log: {query.key_str}")
            return test_case
        return None

    def _get_verified_test_cases(
        self, verified_test_cases: list[TestCase]
    ) -> dict[tuple, TTestCase]:
        """Snapshot, validate, and merge verified test cases.

        Arguments:
            verified_test_cases: verified test cases to prepare
        Returns:
            verified test cases keyed by query
        """
        verified_test_cases_by_query: dict[tuple, TTestCase] = {}
        for test_case in verified_test_cases:
            normalized = self.test_case_cls.model_validate(
                test_case.model_dump(mode="json")
            )
            if not normalized.verified:
                raise ValueError("Queryer test cases must be verified.")
            if normalized.answer is None:
                raise ValueError("Verified test cases must include an answer.")
            key = normalized.query.key
            existing = verified_test_cases_by_query.get(key)
            if existing is None:
                verified_test_cases_by_query[key] = normalized
                continue
            assert existing.answer is not None
            if existing.answer != normalized.answer:
                raise ValueError(
                    "Conflicting verified answers for query "
                    f"{normalized.query.key_str}.\n"
                    f"Existing answer:\n{existing.answer}\n"
                    f"Conflicting answer:\n{normalized.answer}"
                )
            existing.difficulty = max(existing.difficulty, normalized.difficulty)
            existing.few_shot |= normalized.few_shot
            existing.verified |= normalized.verified
        return verified_test_cases_by_query

    @staticmethod
    def _format_validation_errors(exc: ValidationError) -> str:
        """Format validation errors for logging.

        Arguments:
            exc: validation error
        Returns:
            formatted validation errors
        """
        lines: list[str] = []
        for error in exc.errors():
            location = ".".join(map(str, error.get("loc", ())))
            message = str(error.get("msg"))
            lines.append(f"{location}: {message}" if location else message)
        return "\n".join(lines)

    @staticmethod
    def _get_prompt_validation_errors(exc: ValidationError) -> list[str]:
        """Get prompt-authored validation errors suitable for LLM correspondence.

        Arguments:
            exc: validation error
        Returns:
            prompt-authored validation error messages
        """
        validation_errors: list[str] = []
        for error in exc.errors():
            context = error.get("ctx")
            if context is None:
                continue
            cause = context.get("error")
            if isinstance(cause, ValueError):
                validation_errors.append(str(cause))
        return validation_errors
