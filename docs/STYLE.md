# Style Guide

Review this document before planning or coding, and check changed files for compliance before running `ruff` or `ty`.

## Code Style

* Include the standard copyright header at the top of the file.
* Include a module docstring at the top of each file.
* Include `from __future__ import annotations`, unless the file is empty.
* Prefer f-strings for string interpolation.
* Include type annotations for all function and method signatures, with the following exception:
  * If a function always returns `None`, omit the return type annotation.
* In `__init__.py` files, only import classes from the module, not functions or variables.
* Use the `logging` module rather than `print` for any user-facing output in scripts or libraries.
* Test modules do **not** need `__init__.py` files. Pytest can discover tests without them.
* Use explicit path nomenclature:
  * variables or parameters holding `Path` objects should end in `_path` (for example, `file_path`, `dir_path`, `cache_dir_path`)
  * use `*_name` for bare names and `*_stem` for stems, not for full paths
  * prefer `*_dir_path` over `*_directory` when the value is a path
* Within classes, sort methods in the following hierarchy:
  1. Level 1: `__init__`, other builtins, public methods, private methods
  2. Level 2: standard methods, class methods, static methods
  3. Level 3: alphabetical order

## Documentation

* Use Markdown for formatting.
* Do **not** include any reStructuredText markup such as double backticks.
* Provide docstrings for all classes and functions, including internal helpers prefixed with an underscore.
* Document class attributes using triple-quoted strings immediately below each instead of relying only on an `Attributes` section in the class docstring.
* Format docstrings using Google style, with the following tweaks:
  * Use `Arguments:` instead of `Args:`.
  * Do not include a blank line between the `Arguments:` and `Returns:` sections.
  * In argument descriptions, the first word after the colon should be lowercase unless it is a type name.
  * In the `Returns` section, the first word should be lowercase unless it is a type name.
