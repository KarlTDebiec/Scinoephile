---
name: test-fixture-sync
description: Sync test fixtures in test/data/* by comparing the input and output files present with test fixtures in __init__.py and making appropriate updates, followed by updating the relevant tests to use the current fixtures/files. Use when test data file organization changes, output files are added/removed, or tests fail due to fixture mismatches.
---

# Sync Test Fixtures

Follow this workflow to keep test fixtures aligned with the files on disk.

## Scan files

- List each test dataset under `test/data` (e.g., `kob`, `mlamd`, `mnt`, `t`).
- For each dataset, list `test/data/<dataset>/input` contents
  - `.srt` and `.sup` files are of interest
- For each dataset, list `test/data/<dataset>/output` contents
  - `.srt` and `_image` directories are of interest
For each dataset, list the contents of other directories under `test/data/<dataset>` recursively
- `.json` directories are of interest
- Compare against fixtures and `__all__` in `test/data/<dataset>/__init__.py`.

Suggested commands:

```bash
Get-ChildItem -Path test/data/<dataset>/output | Sort-Object Name | Select-Object Name
rg -n "output_dir /" test/data/<dataset>/__init__.py
```

## Update fixtures

- Add/remove fixtures in `test/data/<dataset>/__init__.py` to match output files/dirs.
- Keep fixture names consistent with filenames (match the naming convention used in the repo).
- Within `test/data/<dataset>/__init__.py`, group fixtures into:
    - Input fixtures (pointing to files in `input/`)
    - Action fixtures (pointing to files in other directories such as `lang/`)
    - Output fixtures (pointing to files in `output/`)
- Within each group, sort fixtures alphabetically.
- Update `__all__` to match fixture names, maintaining the same grouping and order as above.

## Update tests

- Use `rg` to find fixture usages in `test/` and update to the new fixture names.
- Prefer replacing old fixture names with the most semantically equivalent new ones.

Suggested commands:

```bash
rg -n "<old_fixture_name>" test
rg -n "fuse_proofread|clean_validate|proofread_flatten" test
```

## Validate

- Format/check only the Python files you touched:

```bash
uv run ruff format <files>
uv run ruff check --fix <files>
```

- Run pytest:

```bash
cd test && uv run pytest
```

## Notes

- Keep changes minimal and consistent with existing naming patterns.
