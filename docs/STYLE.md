# Style Guide

## Python Version
* Target **Python 3.13** features where applicable; do not worry about compatibility with earlier versions.

## Copyright
* Include the standard copyright header at the top of the file.

## Formatting
* Allow `ruff format` to manage code formatting details.

## Imports
* Include `from __future__ import annotations` in Python modules that contain
  imports, exports, type annotations, functions, or classes. Pure package
  marker files that contain only a module docstring do not need it.
* For imports within the same directory, use relative imports (for example, `from .foo import bar`).
* Do not use relative imports for imports from parent or sibling directories (for example, `from ..foo import bar` or `from .. import foo`).
* Allow `ruff` to manage import sorting.

## Exports
* Include `__all__` in Python modules that export public names. Pure package
  marker files that intentionally export nothing do not need it.
* If `__all__` contains multiple entries, include a trailing comma after the last entry so `ruff` formats it as one item per line.
* `__all__` should list the **intended public API** for the module.
  * Do not include internal helpers (names prefixed with an underscore).
  * Keep `__all__` stable where practical; renames/removals are user-facing changes.
* In `__init__.py` files, only import classes from the module, not functions or variables.

## Organization
* Within classes, sort methods in the following hierarchy:
  1. Level 1: `__init__`, other builtins, public properties, public methods, private properties, private methods
  2. Level 2: standard methods, class methods, static methods
  3. Level 3: alphabetical order
* Within modules, sort functions using the same hierarchy described for class methods:
  1. Level 1: public functions, private functions (prefixed with an underscore)
  2. Level 2: standard functions, then decorator-based variants where applicable (for example, `@overload`)
  3. Level 3: alphabetical order

## Nomenclature
* Use explicit path nomenclature:
  * variables or parameters holding `Path` objects should end in `_path` (for example, `file_path`, `dir_path`, `cache_dir_path`)
  * use `*_name` for bare names and `*_stem` for stems, not for full paths
  * prefer `*_dir_path` over `*_directory` when the value is a path

## Style
* Exclusively use f-strings for string interpolation.
* Where possible, classes should implement `__repr__` methods such that they may be reconstructed from its `repr` output.
* Avoid ternary expressions; prefer explicit `if`/`else` statements for readability.

## Type Annotations
* Include type annotations for all function and method signatures, with the following exception:
  * If a function always returns `None`, omit the return type annotation.

## Exceptions
* Prefer raising `ScinoephileError` (or a relevant subclass) for domain-specific errors that should be user-facing.
* Prefer built-in exceptions (`ValueError`, `TypeError`, etc.) for programming errors or invalid internal state.
* When wrapping a caught exception, use exception chaining (`raise ... from err`) to preserve context.

## Logging
* Use the `logging` module rather than `print` for any user-facing output in scripts or libraries.
  * Follow the repository pattern of defining a module-level `logger = getLogger(__name__)`.

## Testing
* Test modules do **not** need `__init__.py` files. Pytest can discover tests without them.

## Documentation
* Include a module docstring at the top of each file.
* Use Markdown for formatting.
* Do **not** include any reStructuredText markup such as double backticks.
* Provide docstrings for all modules, classes, properties, and functions, including internal helpers prefixed with an underscore.
  * Provide docstrings for property setters as well as getters when they are defined.
  * Provide docstrings for `TypedDict` classes, enums, and other public type definitions.
* Document class attributes using triple-quoted strings immediately below each instead of relying only on an `Attributes` section in the class docstring.
* Format docstrings using Google style, with the following tweaks:
  * Use `Arguments:` instead of `Args:`.
  * Do not include an `Arguments:` section for functions or methods that take no arguments.
  * In argument descriptions, the first word after the colon should be lowercase unless it is a type name.
  * Do not include a blank line between the `Arguments:` and `Returns:` sections.
  * Do not include an `Returns:` section for functions or methods that return None.
  * In the `Returns:` section, the first word should be lowercase unless it is a type name.
