# Instructions

## Tools

* This repository uses a virtual environment. To activate the venv in your shell: `source .venv/bin/activate`.
* This repository uses `uv`. Use `uv run` when executing tools.

### Linting

* Run the following checks on **only the Python files you have changed or been asked to**:
  1. `uv run ruff format`
  2. `uv run ruff check --fix`
  3. `uv run ty`
* If `ruff` or `ty` suggest changes that would require major refactoring, confirm with the user before proceeding.

### Testing

* Run the tests as follows:
  * `cd test && uv run pytest`
* You may run pytest with a timeout of up to 10 minutes without asking the user.

## Code Style

* Include the standard copyright header at the top of the file.
* Include a module docstring at the top of each file.
* Include `from __future__ import annotations`, unless the file is empty.
* Include type annotations for all function and method signatures, with the following exception:
    * If a function always returns `None`, omit the return type annotation.
* In `__init__.py` files, only import classes from the module, not functions or variables.
* Use the `logging` module rather than `print` for any user-facing output in scripts or
  libraries.
* Test modules do **not** need `__init__.py` files. Pytest can discover tests without them.

## Documentation

* Use Markdown for formatting.
* Do **not** include any reStructuredText markup such as double backticks.
* Provide docstrings for all classes and functions, including internal helpers prefixed with an underscore.
* Format docstrings using Google style, with the following tweaks:
    * Use "Arguments:" instead of "Args:".
    * Do not include a blank line between the "Arguments:" and "Returns:" sections.
    * In argument descriptions, the first word after the colon should be lowercase unless it is a type name.
    * In the Returns section, the first word should be lowercase unless it is a type name.
