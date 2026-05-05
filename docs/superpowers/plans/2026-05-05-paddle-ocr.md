# PaddleOCR Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `scinoephile ocr paddle --infile INFILE --outfile OUTFILE` to convert `.sup` files or image subtitle directories to SRT with native Python PaddleOCR.

**Architecture:** Add an `ocr` CLI dispatcher and a Paddle subcommand that loads existing `ImageSeries` inputs, calls a focused PaddleOCR library layer, and saves a text `Series`. Move the existing image OCR validation package under `scinoephile/image/ocr/validation` so `scinoephile/image/ocr/paddle` can own OCR recognition code. Keep Paddle imports lazy so tests can use fakes without requiring models.

**Tech Stack:** Python 3.13, argparse CLI classes, `pysubs2`, Pillow, NumPy, PaddleOCR/PaddlePaddle, pytest, ruff, ty.

---

## File Structure

- `pyproject.toml`: add PaddleOCR runtime dependencies if dependency resolution succeeds.
- `uv.lock`: update lock after dependency changes.
- `docs/THIRD_PARTY_NOTICES.md`: add SubtitleEdit MIT notice.
- `scinoephile/cli/scinoephile_cli.py`: register `OcrCli`.
- `scinoephile/cli/ocr/__init__.py`: export OCR CLI classes.
- `scinoephile/cli/ocr/ocr_cli.py`: nested `ocr` dispatcher.
- `scinoephile/cli/ocr/ocr_paddle_cli.py`: parse `--infile`, `--outfile`, `--language`, and `--overwrite`; run OCR.
- `scinoephile/image/ocr/validation/*`: moved existing validation modules.
- `scinoephile/image/ocr/paddle/result.py`: normalized OCR result dataclasses and line grouping.
- `scinoephile/image/ocr/paddle/preprocessing.py`: SubtitleEdit-inspired border preprocessing.
- `scinoephile/image/ocr/paddle/engine.py`: lazy PaddleOCR wrapper.
- `scinoephile/image/ocr/paddle/series.py`: convert `ImageSeries` to text `Series`.
- `test/cli/ocr/test_ocr_cli.py`: CLI help, usage, dispatch, fake-recognizer conversion.
- `test/image/ocr/paddle/test_preprocessing.py`: preprocessing dimensions and image mode.
- `test/image/ocr/paddle/test_result.py`: geometry-based line grouping.
- `test/image/ocr/paddle/test_series.py`: fake recognizer preserves timings and writes text.

## Task 1: Update Spec Detail

**Files:**
- Modify: `docs/superpowers/specs/2026-05-05-paddle-ocr-design.md`

- [x] **Step 1: Record CLI argument pattern**

Update the design command to:

```bash
scinoephile ocr paddle --infile INFILE --outfile OUTFILE --language en
```

- [x] **Step 2: Record language help requirement**

State that `--language` help must list `en` (English), `ch` (simplified Chinese and English), and `chinese_cht` (traditional Chinese).

- [x] **Step 3: Commit**

Run:

```bash
git add docs/superpowers/specs/2026-05-05-paddle-ocr-design.md
git commit --amend --no-edit
```

Expected: design commit amended.

## Task 2: Move Validation Package

**Files:**
- Move: `scinoephile/image/ocr/char_cursor.py` to `scinoephile/image/ocr/validation/char_cursor.py`
- Move: `scinoephile/image/ocr/char_dims.py` to `scinoephile/image/ocr/validation/char_dims.py`
- Move: `scinoephile/image/ocr/char_grp_dims.py` to `scinoephile/image/ocr/validation/char_grp_dims.py`
- Move: `scinoephile/image/ocr/char_pair_gaps.py` to `scinoephile/image/ocr/validation/char_pair_gaps.py`
- Move: `scinoephile/image/ocr/gap_cursor.py` to `scinoephile/image/ocr/validation/gap_cursor.py`
- Move: `scinoephile/image/ocr/validation_manager.py` to `scinoephile/image/ocr/validation/validation_manager.py`
- Modify: `scinoephile/image/ocr/__init__.py`
- Create: `scinoephile/image/ocr/validation/__init__.py`

- [ ] **Step 1: Move files with git**

Run `mkdir -p scinoephile/image/ocr/validation`, then `git mv` each validation file into that directory.

- [ ] **Step 2: Update imports and exports**

Make `scinoephile/image/ocr/validation/__init__.py` export `ValidationManager`, and keep `scinoephile/image/ocr/__init__.py` exporting `ValidationManager` for compatibility.

- [ ] **Step 3: Run import search**

Run:

```bash
rg -n "scinoephile\\.image\\.ocr|from \\.char|from \\.gap|from \\.validation_manager" scinoephile test -g '*.py'
```

Expected: no stale intra-package imports.

## Task 3: Add Paddle Result and Preprocessing Tests

**Files:**
- Create: `test/image/ocr/paddle/test_result.py`
- Create: `test/image/ocr/paddle/test_preprocessing.py`

- [ ] **Step 1: Write failing result grouping tests**

Create tests that construct four `PaddleOcrTextResult` values out of order and assert `format_paddle_ocr_text(...) == "Top left Top right\\NBottom left Bottom right"`.

- [ ] **Step 2: Write failing preprocessing test**

Create a small transparent `PIL.Image` and assert `preprocess_paddle_ocr_image(image, border=10)` returns an RGBA image with width and height increased by 20.

- [ ] **Step 3: Verify RED**

Run:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest test/image/ocr/paddle/test_result.py test/image/ocr/paddle/test_preprocessing.py -q
```

Expected: fail because modules do not exist.

## Task 4: Implement Paddle Result and Preprocessing

**Files:**
- Create: `scinoephile/image/ocr/paddle/__init__.py`
- Create: `scinoephile/image/ocr/paddle/result.py`
- Create: `scinoephile/image/ocr/paddle/preprocessing.py`

- [ ] **Step 1: Implement result dataclasses and grouping**

Define frozen dataclasses `PaddleOcrPoint`, `PaddleOcrBoundingBox`, and `PaddleOcrTextResult`. Implement `group_paddle_ocr_text_results(...)` by sorting detections by center Y, splitting when the next center exceeds the previous top plus average height, then sorting each line by left X. Implement `format_paddle_ocr_text(...)` with spaces within lines and `\\N` between lines.

- [ ] **Step 2: Implement preprocessing**

Add a transparent canvas around an RGBA-converted image and paste the original image at the requested border offset. Include a concise comment that this border behavior is adapted from SubtitleEdit's PaddleOCR preprocessing.

- [ ] **Step 3: Verify GREEN**

Run:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest test/image/ocr/paddle/test_result.py test/image/ocr/paddle/test_preprocessing.py -q
```

Expected: pass.

## Task 5: Add Fake-Recognizer Series Tests

**Files:**
- Create: `test/image/ocr/paddle/test_series.py`

- [ ] **Step 1: Write failing conversion test**

Create a two-event `ImageSeries` with blank RGBA images and a fake recognizer whose `recognize_image(...)` returns `"first"` then `"second"`. Assert `ocr_image_series_with_paddle(...)` returns a text `Series` with matching start/end times and text.

- [ ] **Step 2: Verify RED**

Run:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest test/image/ocr/paddle/test_series.py -q
```

Expected: fail because `ocr_image_series_with_paddle` does not exist.

## Task 6: Implement Paddle Engine and Series Conversion

**Files:**
- Create: `scinoephile/image/ocr/paddle/engine.py`
- Create: `scinoephile/image/ocr/paddle/series.py`
- Modify: `scinoephile/image/ocr/paddle/__init__.py`

- [ ] **Step 1: Implement recognizer protocol and series conversion**

Define a runtime protocol with `recognize_image(image: Image.Image) -> str`. Implement `ocr_image_series_with_paddle(image_series, recognizer=None, language="en") -> Series`, preserving timing and using the supplied recognizer or a new `PaddleOcrRecognizer`.

- [ ] **Step 2: Implement lazy PaddleOCR wrapper**

`PaddleOcrRecognizer.__init__` lazily imports `PaddleOCR`, creates the engine with conservative subtitle-oriented options, and converts Paddle structured results into `PaddleOcrTextResult` objects. If imports fail, raise `ScinoephileError` with a direct installation message.

- [ ] **Step 3: Verify GREEN**

Run:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest test/image/ocr/paddle/test_series.py -q
```

Expected: pass without importing PaddleOCR because the fake recognizer is used.

## Task 7: Add OCR CLI Tests

**Files:**
- Create: `test/cli/ocr/test_ocr_cli.py`

- [ ] **Step 1: Write failing help and usage tests**

Use existing `assert_cli_help` and `assert_cli_usage` for `(OcrCli,)`, `(OcrCli, OcrPaddleCli)`, `(ScinoephileCli, OcrCli, OcrPaddleCli)`. Assert Paddle help includes `en (English)`, `ch (simplified Chinese and English)`, and `chinese_cht (traditional Chinese)`.

- [ ] **Step 2: Write failing CLI conversion test**

Monkeypatch the CLI's OCR function to return a one-event text `Series`, run `OcrPaddleCli` with `--infile <fixture sup> --outfile <tmp.srt>`, and assert the output SRT loads with expected text.

- [ ] **Step 3: Verify RED**

Run:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest test/cli/ocr/test_ocr_cli.py -q
```

Expected: fail because CLI modules do not exist.

## Task 8: Implement OCR CLI

**Files:**
- Create: `scinoephile/cli/ocr/__init__.py`
- Create: `scinoephile/cli/ocr/ocr_cli.py`
- Create: `scinoephile/cli/ocr/ocr_paddle_cli.py`
- Modify: `scinoephile/cli/scinoephile_cli.py`

- [ ] **Step 1: Implement nested dispatcher**

Follow `CacheCli`: `OcrCli` adds subparsers with `dest="ocr_subcommand_name"` and dispatches to `OcrPaddleCli`.

- [ ] **Step 2: Implement Paddle command**

Use `--infile` with `dest="infile_path"`, `--outfile` with `dest="outfile_path"`, `--language` with default `en` and help listing `en`, `ch`, and `chinese_cht`, and `--overwrite`. Load with `ImageSeries.load`, call `ocr_image_series_with_paddle`, and save as SRT.

- [ ] **Step 3: Register top-level command**

Import and add `OcrCli.name(): OcrCli` in `ScinoephileCli.subcommands()`.

- [ ] **Step 4: Verify GREEN**

Run:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest test/cli/ocr/test_ocr_cli.py -q
```

Expected: pass.

## Task 9: Dependencies and Third-Party Notices

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Modify: `docs/THIRD_PARTY_NOTICES.md`

- [ ] **Step 1: Add Paddle dependency**

Run:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv add paddleocr
```

If PaddlePaddle is not resolved or import verification shows it is missing, run:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv add paddlepaddle
```

- [ ] **Step 2: Add SubtitleEdit notice**

Add a `SubtitleEdit (adapted OCR preprocessing and grouping logic)` section to `docs/THIRD_PARTY_NOTICES.md`, following the jyut-dict MIT notice pattern.

- [ ] **Step 3: Verify lock/import metadata**

Run:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -c "import importlib.util; print(importlib.util.find_spec('paddleocr') is not None)"
```

Expected: prints `True`.

## Task 10: Formatting, Type Checking, and Tests

**Files:**
- All changed Python files.

- [ ] **Step 1: Check changed Python files against style guide**

Run:

```bash
git diff --name-only -- '*.py'
```

Review changed files for `docs/STYLE.md` requirements before automated tools.

- [ ] **Step 2: Run changed-file formatting and linting**

Run `UV_CACHE_DIR=/tmp/uv-cache uv run ruff format` on changed Python files only, then `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check --fix` on changed Python files only.

- [ ] **Step 3: Run changed-file type checking**

Run `UV_CACHE_DIR=/tmp/uv-cache uv run ty check` on changed Python files only.

- [ ] **Step 4: Run targeted tests**

Run:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest test/image/ocr/paddle test/cli/ocr -q
```

- [ ] **Step 5: Run full suite if targeted checks pass**

Run:

```bash
cd test && UV_CACHE_DIR=/tmp/uv-cache uv run pytest -n auto
```
