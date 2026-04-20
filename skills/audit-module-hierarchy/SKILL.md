---
name: audit-module-hierarchy
description: Audit and correct module hierarchy comments and exported symbol ordering in scinoephile __init__.py files using dependency-aware "bubble up" ordering, including cycle detection (for example core/open_ai). Use when package structure changes or when hierarchy comments may be stale.
---

# Audit `__init__.py` Hierarchy and Exports

Use this workflow to keep `__init__.py` files consistent with actual imports.

## When to use

- A module was moved or renamed.
- A package hierarchy comment looks stale.
- `__all__` ordering is inconsistent with current structure.
- You suspect dependency cycles between sibling modules/packages.

## Goals

- Keep hierarchy comments truthful: "modules may import from any above."
- Bubble each module to the highest valid level.
- Group peers on the same line with ` / `.
- Report sibling cycles explicitly.
- Keep `__all__` aligned with imported/exported symbols and existing style.

## Quick workflow

1. Identify `__init__.py` files:
   - `scinoephile/__init__.py` (top-level package hierarchy)
   - nested package `__init__.py` files (for example `scinoephile/lang/*/__init__.py`)
2. Run the helper script:
   - `python skills/audit-module-hierarchy/scripts/audit_module_hierarchy.py --target scinoephile`
3. Review output:
   - proposed levels per package
   - detected cycles
4. Update hierarchy comment blocks in affected `__init__.py` files.
5. Check each edited package still matches import reality.
6. Run validation on changed Python files:
   - `uv run ruff format <changed_files>`
   - `uv run ruff check --fix <changed_files>`
   - `uv run ty check <changed_files>`

## Ordering rules

- Build edges as `importer -> importee`.
- Collapse strongly connected components (SCCs); each SCC is a same-level group.
- Assign each SCC level as:
  - `1` if it imports no sibling/module in scope
  - otherwise `1 + max(level(imported_scc))`
- Render levels ascending (dependencies first).
- For display, join same-level SCC members using ` / `.
- If a cycle exists, keep that cycle grouped on one line (for example `core / open_ai`).

## Scope guidance

- For repository-wide architecture, analyze top-level packages under `scinoephile/`.
- For local package docs (for example `scinoephile/lang/zho/__init__.py`), analyze direct children of that package only.
- Do not infer ordering from filenames; only from imports.

## Reporting guidance

When done, report:

- which `__init__.py` files were updated
- the new hierarchy levels
- any detected cycles
- whether validation checks passed

