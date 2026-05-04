---
name: audit-style
description: Audit Python files in a repository for compliance with docs/STYLE.md and write conservative markdown notes, typically to local/style_notes.md. Use when asked to review repository style compliance without automatically modifying source files.
---

# Audit `docs/STYLE.md` Compliance

Use this workflow to review Python source files against `docs/STYLE.md` and write notes without changing source code.

## Quick workflow

1. Read `docs/STYLE.md`.
2. Run the helper script:
   - `UV_CACHE_DIR=/tmp/uv-cache uv run python skills/audit-style/scripts/audit_style.py --target . --output local/style_notes.md`
3. Review the generated markdown report.
4. If asked to fix issues, edit source files separately and validate only changed Python files:
   - `UV_CACHE_DIR=/tmp/uv-cache uv run ruff format <changed_files>`
   - `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check --fix <changed_files>`
   - `UV_CACHE_DIR=/tmp/uv-cache uv run ty check <changed_files>`

## Notes

- The script is intentionally conservative and flags items that may require maintainer judgment.
- It does not run `ruff`, `ty`, or tests.
- It does not exhaustively prove public API intent, method ordering, or whether `print` output is user-facing.
- Keep generated audit notes under `local/` unless the user asks for a different path.
