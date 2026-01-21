---
name: scinoephile-test-authoring
description: Add or update pytest tests in Scinoephile's test/ suite, including new test modules, fixtures under test/data, or expected-output generation scripts for subtitle/LLM/CLI workflows.
---

# Add a Test in Scinoephile

## Quick steps
- Identify the closest existing test module under `test/` and mirror its structure.
- Reuse fixtures from `test/data/<title>/__init__.py`; add new fixtures there if needed.
- If new expected outputs are required, update the matching `test/data/<title>/create_output.py` or helper functions in `test/data/ocr.py` or `test/data/synchronization.py`.
- Add or update test data files under `test/data/<title>/input` and `test/data/<title>/output`.
- Run `uv run ruff format <changed.py>` and `uv run ruff check --fix <changed.py>` on changed Python files.
- Run tests from `test/` with `cd test && uv run pytest <optional-path>`.

## Test module pattern
- Include the standard copyright header, module docstring, and `from __future__ import annotations`.
- Use pytest fixtures from `test.data.*` (imported into `test/conftest.py`).
- Add type annotations to all function signatures; omit return type when the function returns `None`.
- Prefer helper functions for repeated assertions; include Google-style docstrings using `Arguments:` and `Returns:`.
- Use `pytest.mark.parametrize` for multiple inputs; use `Series` equality or per-event comparisons.
- For temporary output files, use `get_temp_file_path` and compare against expected files via `Series.load`.

## Fixtures and test data
- Test data is grouped by title (examples: `kob`, `mlamd`, `mnt`, `t`).
- Fixtures live in `test/data/<title>/__init__.py` and are exported via `__all__`.
- Each title module defines:
  - `title_root`, `input_dir`, and `output_dir` based on `test_data_root`.
  - `pytest.fixture` loaders for subtitle `Series`, `ImageSeries`, or `AudioSeries`.
  - Cached helpers like `get_<title>_*_test_cases()` for LLM prompt JSON test cases.
- If you introduce a new title namespace, add a `test/data/<title>/__init__.py` and update `test/conftest.py` to import it.

## Generating expected outputs
- Use the existing helpers in `test/data/ocr.py` and `test/data/synchronization.py` to build consistent output artifacts.
- Each title has a `test/data/<title>/create_output.py` script; extend it to generate any new outputs.
- Keep expected outputs in `test/data/<title>/output` and inputs in `test/data/<title>/input`.

## Data constraints
- Do not add new binary files; if binary assets are required, provide a generator script under `test/scripts` and store only sources needed for generation.

## Example skeleton
```python
#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.<area>.<function>."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series
from scinoephile.<area> import <function>


def _test_<function>(series: Series, expected: Series):
    """Test <function>.

    Arguments:
        series: input series fixture
        expected: expected output series fixture
    """
    output = <function>(series)
    assert output == expected


@pytest.mark.parametrize(
    ("series", "expected"),
    [
        ("kob_eng_fuse", "kob_eng_fuse_clean"),
        ("mnt_eng_fuse", "mnt_eng_fuse_clean"),
    ],
)
def test_<function>_titles(request: pytest.FixtureRequest, series: str, expected: str):
    """Test <function> across titles.

    Arguments:
        request: pytest request for fixture lookup
        series: fixture name for input
        expected: fixture name for expected output
    """
    _test_<function>(
        request.getfixturevalue(series),
        request.getfixturevalue(expected),
    )
```
