# Instructions

## Tools

* This repository uses `uv`. Use `uv run` when executing tools.
* Formatting: `uv run ruff format`
* Linting: `uv run ruff check`
* Type checking: `uv run pyright`
* Testing: `uv run pytest`

## Code Style

* Include the standard copyright header at the top of the file.
* Include a module docstring at the top of each file.
* Include `from __future__ import annotations`, unless the file is empty.
* All imports within the `scinoephile` package should use absolute paths starting with
  `scinoephile` rather than relative imports.
* In `__init__.py` files, only import classes from the module, not functions or
  variables.
* Do **not** commit binary files.
    * If binary assets are required for tests, provide a script under test/scripts to
      generate them.
* Use the `logging` module rather than `print` for any user-facing output in scripts or
  libraries.

## Documentation

* Use Markdown for formatting.
* Do **not** include any reStructuredText markup.
* Provide docstrings for all classes and functions, including internal helpers prefixed
  with an underscore.
* Format docstrings using Google style, with the following tweaks.
    * Use "Arguments:" instead of "Args:".
    * Do not include a blank link between the "Arguments:" and "Returns:" sections.

## Dependencies

* When adding a new dependency:
    * Update `pyproject.toml`
    * Update `scripts/conda_scinoephile.sh` and `scripts/conda_scinoephile.ps1`
    * Keep dependencies in both places alphabetized
