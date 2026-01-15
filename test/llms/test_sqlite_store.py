#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for SQLite persistence of LLM artifacts."""

from __future__ import annotations

from pathlib import Path

from scinoephile.lang.eng.ocr_fusion.prompts import EngOcrFusionPrompt
from scinoephile.llms.base.sqlite_store import SqliteStore
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionManager


def test_sqlite_store_round_trip():
    """Persist and reload prompts, test cases, and results."""
    db_path = Path.cwd() / "prompt_store.sqlite"
    if db_path.exists():
        db_path.unlink()
    try:
        with SqliteStore(db_path) as store:
            store.initialize_schema()

            prompt_version = store.get_or_create_prompt_version(
                EngOcrFusionPrompt, version_label="v1"
            )
            loaded_prompt_version = store.load_prompt_version(
                EngOcrFusionPrompt,
                prompt_version.prompt_version_id,
            )

            assert loaded_prompt_version.content["base_system_prompt"]
            assert loaded_prompt_version.content_hash == prompt_version.content_hash

            model_id = store.get_or_create_model("gpt-5.1", provider="openai")

            test_case_cls = OcrFusionManager.get_test_case_cls(
                prompt_cls=EngOcrFusionPrompt
            )
            query = test_case_cls.query_cls(lens="Hello", tesseract="Hello!")
            answer = test_case_cls.answer_cls(
                output="Hello!", note="Prefer Tesseract punctuation."
            )
            test_case = test_case_cls(query=query, answer=answer)
            test_case_id = store.upsert_test_case(test_case)

            loaded_test_cases = store.load_test_cases(EngOcrFusionPrompt)
            assert len(loaded_test_cases) == 1
            assert (
                loaded_test_cases[0].query.model_dump() == test_case.query.model_dump()
            )
            assert (
                loaded_test_cases[0].answer.model_dump()
                == test_case.answer.model_dump()
            )

            result_id = store.insert_test_result(
                prompt_cls=EngOcrFusionPrompt,
                test_case_id=test_case_id,
                prompt_version_id=prompt_version.prompt_version_id,
                model_id=model_id,
                status="success",
            )
            assert result_id > 0
    finally:
        if db_path.exists():
            db_path.unlink()
