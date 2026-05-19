# Frame-Grid Video Offset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build frame-grid fine visual offset search with multi-window sampling and aggregate reporting.

**Architecture:** Keep the implementation in `scinoephile/media/video_offset.py`, where sampling and scoring already live. Extend the existing result dataclasses rather than adding a new subsystem, and keep CLI formatting in `scinoephile/cli/media/media_offset_cli.py`.

**Tech Stack:** Python 3.13, ffmpeg-python/ffprobe, numpy, pytest, ruff, ty.

---

### Task 1: Frame Metadata and Frame-Grid Search

**Files:**
- Modify: `scinoephile/media/video_offset.py`
- Test: `test/media/test_video_offset.py`

- [x] Write failing tests for parsing reference FPS and rejecting missing FPS.
- [x] Write a failing test showing fine search returns `-20` frames for `24000/1001` fps rather than a seconds-grid value.
- [x] Implement concise ffprobe helpers and frame-grid fine candidate generation.
- [x] Run the focused video offset tests.

### Task 2: Multi-Window Results and Aggregation

**Files:**
- Modify: `scinoephile/media/video_offset.py`
- Test: `test/media/test_video_offset.py`

- [x] Write failing tests for automatic window starts across shared runtime.
- [x] Write failing tests for frame-unit aggregate mean, median, stdev, min, max, and agreement.
- [x] Add window result and aggregate dataclasses, then run each window independently.
- [x] Run the focused video offset tests.

### Task 3: CLI Arguments and Reporting

**Files:**
- Modify: `scinoephile/cli/media/media_offset_cli.py`
- Test: `test/cli/media/test_media_offset_cli.py`

- [x] Write failing tests for `--sample-windows`, automatic multi-window calls, and frame-aware output.
- [x] Update CLI arguments, localized help text, call wiring, and output formatting.
- [x] Run focused CLI tests and localized help tests.

### Task 4: Verification and Publishing

**Files:**
- Check changed Python files with `docs/STYLE.md`
- Run formatting, linting, type checking, tests, and manual Toy Story commands

- [x] Run `UV_CACHE_DIR=/tmp/uv-cache uv run ruff format` on changed Python files.
- [x] Run `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check --fix` on changed Python files.
- [x] Run `UV_CACHE_DIR=/tmp/uv-cache uv run ty check` on changed Python files.
- [x] Run focused tests and the repository test command.
- [x] Run `scinoephile media offset` against the requested Toy Story reference and target files.
- [ ] Commit, push `feature/frame-grid-video-offset`, and open a draft PR through GitHub MCP.
