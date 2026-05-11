# English From Chinese Translation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable unaligned dual-block LLM processor and use it to generate English subtitles from Chinese subtitles with original English guidance.

**Architecture:** Add `scinoephile.llms.dual_block_cardinality` for two input blocks where output count and timing follow source one. Add `scinoephile.multilang.eng_zho.translation` as a feature wrapper with an English-from-Chinese prompt and factory functions.

**Tech Stack:** Python 3.13, Pydantic dynamic models, existing `Processor` / `Manager` / `Prompt` LLM framework, `Series` / `Subtitle`, pytest, ruff, ty, uv.

---

## File Structure

- Create `scinoephile/llms/dual_block_cardinality/__init__.py`: public exports for the generic shape.
- Create `scinoephile/llms/dual_block_cardinality/prompt.py`: field naming helpers for source one, source two, and output.
- Create `scinoephile/llms/dual_block_cardinality/manager.py`: dynamic query, answer, and test-case model factories keyed by source-one and source-two sizes.
- Create `scinoephile/llms/dual_block_cardinality/processor.py`: block-pair processor whose output series follows source one timing.
- Modify `scinoephile/llms/__init__.py`: include the new package in the hierarchy docstring.
- Create `scinoephile/multilang/eng_zho/__init__.py`: package marker and hierarchy docstring.
- Create `scinoephile/multilang/eng_zho/translation/__init__.py`: operation spec, typed kwargs, public wrapper, and processor factory.
- Create `scinoephile/multilang/eng_zho/translation/prompts.py`: English prompt for Chinese-driven translation with original English guidance.
- Modify `scinoephile/multilang/__init__.py`: include `eng_zho` in the hierarchy docstring.
- Modify `scinoephile/llms/default_test_cases.py`: add an empty-path-capable constant for future English-from-Chinese default cases.
- Create `test/llms/dual_block_cardinality/test_manager.py`: generic dynamic model tests.
- Create `test/llms/dual_block_cardinality/test_processor.py`: generic processor behavior test.
- Create `test/multilang/eng_zho/test_translation.py`: feature wrapper and prompt tests.

### Task 1: Generic Prompt And Manager

**Files:**
- Create: `scinoephile/llms/dual_block_cardinality/__init__.py`
- Create: `scinoephile/llms/dual_block_cardinality/prompt.py`
- Create: `scinoephile/llms/dual_block_cardinality/manager.py`
- Test: `test/llms/dual_block_cardinality/test_manager.py`

- [ ] **Step 1: Write failing manager tests**

Create tests that import `DualBlockCardinalityManager` and `DualBlockCardinalityPrompt`, define a local `_Prompt`, and assert:

```python
query_cls = DualBlockCardinalityManager.get_query_cls(2, 3, _Prompt)
assert set(query_cls.model_fields) == {
    "source_one_1",
    "source_one_2",
    "source_two_1",
    "source_two_2",
    "source_two_3",
}
answer_cls = DualBlockCardinalityManager.get_answer_cls(2, 3, _Prompt)
assert set(answer_cls.model_fields) == {"output_1", "output_2"}
test_case_cls = DualBlockCardinalityManager.get_test_case_cls_from_data(
    {
        "query": {
            "source_one_1": "一",
            "source_one_2": "二",
            "source_two_1": "one",
            "source_two_2": "two",
            "source_two_3": "three",
        }
    },
    prompt_cls=_Prompt,
)
assert getattr(test_case_cls, "source_one_size") == 2
assert getattr(test_case_cls, "source_two_size") == 3
```

- [ ] **Step 2: Run manager tests to verify red**

Run: `UV_CACHE_DIR=/tmp/uv-cache uv run pytest test/llms/dual_block_cardinality/test_manager.py -q`

Expected: FAIL because `scinoephile.llms.dual_block_cardinality` does not exist.

- [ ] **Step 3: Implement prompt and manager**

Implement `DualBlockCardinalityPrompt` with class variables and methods analogous to `DualBlockPrompt`, but without notes:

```python
class DualBlockCardinalityPrompt(Prompt, ABC):
    src_1_pfx: ClassVar[str] = "source_one_"
    src_1_desc_tpl: ClassVar[str] = "Subtitle {idx} text from source one"
    src_2_pfx: ClassVar[str] = "source_two_"
    src_2_desc_tpl: ClassVar[str] = "Subtitle {idx} text from source two"
    output_pfx: ClassVar[str] = "output_"
    output_desc_tpl: ClassVar[str] = "English subtitle {idx} generated for source one subtitle {idx}"
```

Implement `DualBlockCardinalityManager` with `get_query_cls(source_one_size, source_two_size, prompt_cls)`, `get_answer_cls(...)`, `get_test_case_cls(...)`, and `get_test_case_cls_from_data(...)`. Use `get_model_name`, Pydantic `Field`, and `create_model` following `DualBlockManager`. Set `source_one_size` and `source_two_size` attributes on generated classes. Reject `source_one_size < 1` and `source_two_size < 0` with `ScinoephileError`.

- [ ] **Step 4: Run manager tests to verify green**

Run: `UV_CACHE_DIR=/tmp/uv-cache uv run pytest test/llms/dual_block_cardinality/test_manager.py -q`

Expected: PASS.

### Task 2: Generic Processor

**Files:**
- Create: `scinoephile/llms/dual_block_cardinality/processor.py`
- Modify: `scinoephile/llms/dual_block_cardinality/__init__.py`
- Test: `test/llms/dual_block_cardinality/test_processor.py`

- [ ] **Step 1: Write failing processor test**

Create a test using a local prompt and a processor instance with a mocked provider. Replace `processor.queryer` with a callable fake that fills answers from the dynamic answer class:

```python
def fake_queryer(test_case):
    answer = test_case.answer_cls(output_1="First translated", output_2="Second translated")
    return type(test_case)(query=test_case.query, answer=answer)
```

Build a Chinese/source-one series with two subtitles and an English/source-two series with three subtitles in the same pause block. Assert the output has two subtitles, source-one timings, and fake English text.

- [ ] **Step 2: Run processor test to verify red**

Run: `UV_CACHE_DIR=/tmp/uv-cache uv run pytest test/llms/dual_block_cardinality/test_processor.py -q`

Expected: FAIL because `DualBlockCardinalityProcessor` does not exist.

- [ ] **Step 3: Implement processor**

Implement `DualBlockCardinalityProcessor.process(source_one, source_two, stop_at_idx=None)`. Use `get_block_pairs_by_pause`, build query kwargs from every source-one and source-two subtitle in each paired block, query the LLM, and append one `Subtitle` per source-one subtitle with source-one start/end and the answer output text. Save encountered test cases when `test_case_path` is set, following existing processors.

- [ ] **Step 4: Run processor test to verify green**

Run: `UV_CACHE_DIR=/tmp/uv-cache uv run pytest test/llms/dual_block_cardinality/test_processor.py -q`

Expected: PASS.

### Task 3: English-Chinese Translation Feature

**Files:**
- Create: `scinoephile/multilang/eng_zho/__init__.py`
- Create: `scinoephile/multilang/eng_zho/translation/__init__.py`
- Create: `scinoephile/multilang/eng_zho/translation/prompts.py`
- Modify: `scinoephile/multilang/__init__.py`
- Modify: `scinoephile/llms/default_test_cases.py`
- Test: `test/multilang/eng_zho/test_translation.py`

- [ ] **Step 1: Write failing feature tests**

Create tests that assert:

```python
assert EngVsZhoTranslationPrompt.src_1(1) == "zho_1"
assert EngVsZhoTranslationPrompt.src_2(1) == "eng_reference_1"
assert EngVsZhoTranslationPrompt.output(1) == "eng_1"
processor = get_eng_vs_zho_translator(test_cases=[], provider=provider)
assert isinstance(processor, DualBlockCardinalityProcessor)
assert processor.prompt_cls is EngVsZhoTranslationPrompt
output = get_eng_translated_vs_zho(zho_series, eng_series, translator=fake_processor)
assert len(output) == len(zho_series)
```

- [ ] **Step 2: Run feature tests to verify red**

Run: `UV_CACHE_DIR=/tmp/uv-cache uv run pytest test/multilang/eng_zho/test_translation.py -q`

Expected: FAIL because `scinoephile.multilang.eng_zho` does not exist.

- [ ] **Step 3: Implement feature package**

Implement `EngVsZhoTranslationPrompt(DualBlockCardinalityPrompt, PromptEng)` with field prefixes `zho_`, `eng_reference_`, and `eng_`, plus a system prompt that prioritizes Chinese meaning and uses original English for names, terminology, register, and compatible wording.

Implement `get_eng_translated_vs_zho(...)` and `get_eng_vs_zho_translator(...)` following the existing `yue_zho.translation` factory pattern, using `DualBlockCardinalityProcessor`, `DualBlockCardinalityManager`, `get_default_provider`, and a new `ENG_FROM_ZHO_TRANSLATION_JSON_PATHS` constant set to an empty tuple.

- [ ] **Step 4: Run feature tests to verify green**

Run: `UV_CACHE_DIR=/tmp/uv-cache uv run pytest test/multilang/eng_zho/test_translation.py -q`

Expected: PASS.

### Task 4: Style, Type, And Focused Verification

**Files:**
- Modify only files changed by Tasks 1-3 as formatting and lint require.

- [ ] **Step 1: Review changed Python files against style guide**

Run: `git diff --name-only -- '*.py'`

Check the listed files for copyright headers, module docstrings, `from __future__ import annotations`, `__all__`, relative-import rules, typed signatures, and docstrings.

- [ ] **Step 2: Format changed Python files**

Run: `UV_CACHE_DIR=/tmp/uv-cache uv run ruff format <changed-python-files>`

Expected: exit code 0.

- [ ] **Step 3: Lint changed Python files**

Run: `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check --fix <changed-python-files>`

Expected: exit code 0.

- [ ] **Step 4: Type-check changed Python files**

Run: `UV_CACHE_DIR=/tmp/uv-cache uv run ty check <changed-python-files>`

Expected: exit code 0, unless ty does not accept file arguments in this project. If that happens, report the command failure and use the smallest supported project-level ty command.

- [ ] **Step 5: Run focused tests**

Run:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest \
  test/llms/dual_block_cardinality \
  test/multilang/eng_zho \
  -q
```

Expected: PASS.

- [ ] **Step 6: Inspect final diff**

Run: `git diff --stat && git diff --check`

Expected: no whitespace errors and a diff limited to the planned files.
