# Instructions

## Tools

* This repository uses `uv`. Use `uv run` when executing tools.
* To activate the venv in your shell: `source .venv/bin/activate` (deactivate with `deactivate`).
* When running Python scripts that import from the `test/` package (e.g. `test/data/**`),
  set `PYTHONPATH` to the repo root, e.g. `PYTHONPATH=$PWD uv run python test/data/mlamd/create_output.py`.
* Run the following checks on **only the Python files you have changed or been asked 
  to**:
  1. `uv run ruff format`
  2. `uv run ruff check --fix`
* Run `ruff format` only on Python files (do not run it on JSON or other data files).
* Testing: run pytest from `test` directory, e.g. `cd test && uv run pytest`
* Pytest timeout: you may run pytest for up to 10 minutes without asking.
* Test files do **not** need `__init__.py` files. Pytest can discover tests without them.

## Code Style

* Include the standard copyright header at the top of the file.
* Include a module docstring at the top of each file.
* Include `from __future__ import annotations`, unless the file is empty (i.e., contains
  only copyright headers and module docstrings such as otherwise empty
  `__init__.py` files).
* Include type annotations for all function and method signatures, with the following
  exceptions:
    * If a function always returns `None`, omit the return type annotation.
* In `__init__.py` files, only import classes from the module, not functions or
  variables.
* Do **not** commit binary files.
    * If binary assets are required for tests, provide a script under test/scripts to
      generate them.
* Use the `logging` module rather than `print` for any user-facing output in scripts or
  libraries.

## Documentation

* Use Markdown for formatting.
* Do **not** include any reStructuredText markup such as double backticks.
* Provide docstrings for all classes and functions, including internal helpers prefixed
  with an underscore.
* Format docstrings using Google style, with the following tweaks:
    * Use "Arguments:" instead of "Args:".
    * Do not include a blank line between the "Arguments:" and "Returns:" sections.
    * In argument descriptions, the first word after the colon should be lowercase
      unless it is a type name.
    * In the Returns section, the first word should be lowercase unless it is a type 
      name.
