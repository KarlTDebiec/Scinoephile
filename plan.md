# Plan

Wrap up this PR by removing network/ML side effects from the default Chinese OCR validation path, fixing `ImageSubtitle` bbox state handling, making `CharValidator` robust to missing bboxes, and reducing import-time ML dependency loading. Keep tests fast and offline-friendly.

## Scope
- In: make `validate_zho_ocr()` default behavior not load/download ML models; fix `ImageSubtitle.img` bbox clearing; handle `bboxes=None` in `CharValidator`; avoid eager ML imports from `scinoephile.image.ocr`; update/add tests; run ruff + pytest.
- Out: changing OCR algorithms/accuracy, training new models, or adding new runtime dependencies.

## Action items
[ ] Keep `validate_zho_ocr()` defaulting `validate_chars=True`, and ensure the default path is stable/reproducible (pin model artifacts, deterministic init, clear failures) while still remaining reasonably fast.
[ ] Make `CharValidator` model loading/download explicitly opt-in (e.g., lazy init or a clear flag) so that even accidental construction cannot hang offline runs.
[ ] Fix `ImageSubtitle.img` setter to clear bbox state consistently (reset `self.bboxes` rather than an unused `_bboxes`) and add a regression test for reassigning `img`.
[ ] Update `CharValidator` to handle `sub.bboxes is None` deterministically (skip with a warning or raise a clear exception instructing callers to run `BboxValidator` first).
[ ] Adjust `scinoephile/image/ocr/__init__.py` to avoid importing heavy ML dependencies at import time (use lazy import/`__getattr__`, or stop re-exporting `CharValidator` from the package root).
[ ] Update/add tests to ensure `validate_zho_ocr()` runs offline by default (e.g., monkeypatch `snapshot_download` / assert `CharValidator` is not constructed) and that bbox state/None-bbox behavior is covered.
[ ] Run `uv run ruff format` and `uv run ruff check --fix` on the modified Python files only.
[ ] Run targeted pytest for the affected areas (e.g., `cd test && uv run pytest test/lang/zho/test_validate_zho_ocr.py` plus any new tests), then the full test suite if time permits.
[ ] Consider CI changes needed for the new default to pass (e.g., cache/prefetch the model, point to a vendored/local model directory, or selectively skip ML validation tests in CI/offline environments).

## Open questions
- Should `CharValidator` on `bboxes=None` raise (strict) or warn-and-skip (lenient)?
- Do we want a separate “ML validation” helper entrypoint to make the opt-in path obvious (vs. a boolean flag)?
- Should `scinoephile.image.ocr` still re-export `CharValidator`, or require `from scinoephile.image.ocr.char_validator import CharValidator` to avoid accidental heavy imports?
