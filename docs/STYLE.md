# Style Guide

## Python Version
* Target **Python 3.13** features where applicable; do not worry about compatibility with earlier versions.

## Copyright
* Include the standard two-line copyright header at the top of the file.

## Formatting
* Allow `ruff format` to manage code formatting details.

## Imports
* Include `from __future__ import annotations` in Python modules that contain imports, exports, type annotations, functions, or classes. Pure package marker files that contain only a module docstring do not need it.
* For imports within the same directory, use relative imports (for example, `from .foo import bar`).
* Do not use relative imports for imports from parent or sibling directories (for example, `from ..foo import bar` or `from .. import foo`).
* Use `if TYPE_CHECKING:` blocks only when necessary to avoid circular imports.
* Allow `ruff` to manage import sorting.

## Exports
* Include `__all__` in Python modules that export public names.
* Do not include empty `__all__` assignments.
* If `__all__` contains one entry, keep it on one line, such as `__all__ = ["foo"]`.
* If `__all__` contains multiple entries, include a trailing comma after the last entry so `ruff` formats it as one item per line.
* `__all__` should list the intended public API for the module.
* Do not include internal helpers, which are names prefixed with an underscore.
* In `__init__.py` files, only import classes from the module, not functions or variables.

## Organization
* Within classes, sort methods in the following hierarchy:
  1. Level 1: `__init__`, other builtins, public properties, public methods, private properties, private methods
  2. Level 2: standard methods, class methods, static methods
  3. Level 3: alphabetical order
* Within modules, sort functions using the same hierarchy described for class methods:
  1. Level 1: public functions, private functions prefixed with an underscore
  2. Level 2: standard functions, then decorator-based variants where applicable, such as `@overload`
  3. Level 3: alphabetical order

## Nomenclature
* Use explicit path nomenclature:
  * variables or parameters holding `Path` objects should end in `_path`, such as `file_path`, `dir_path`, or `cache_dir_path`
  * bare `path` or `paths` parameters are acceptable for small path-focused helpers where no more specific role name applies
  * CLI-facing argument names may use conventional command-line terms such as `infile` and `outfile` without a `_path` suffix
  * generic validator inputs may use `value` or `value_to_validate`, even when the accepted type includes paths
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
* Prefer repository-specific exceptions from for domain-specific errors that should be user-facing.
* Prefer built-in exceptions such as `ValueError` and `TypeError` for programming errors or invalid internal state.
* When wrapping a caught exception, use exception chaining with `raise ... from err` to preserve context.

## Logging
* Use the `logging` module rather than `print` for any user-facing output in scripts or libraries.
* CLI tools may use `print` for intentional command output written to stdout.
  * Follow the repository pattern of defining a module-level `logger = getLogger(__name__)`.

## Command Line Interface
* In CLI modules under `scinoephile/cli/`, group arguments using
  `scinoephile.common.argument_parsing.get_arg_groups_by_name(...)`.
  * Standard group names are:
    * `input arguments`
    * `operation arguments`
    * `output arguments`
  * Rename the default optional group to `additional arguments` via
    `optional_arguments_name="additional arguments"`.
* CLI modules should support localization by defining a `localizations` mapping (as used by
  `ScinoephileCliBase.translate_text`), and writing `help`, `description`, and argument-group
  titles using stable English strings that can be translated.

## Testing
* Test modules do **not** need `__init__.py` files. Pytest can discover tests without them.

## Documentation
* Include a module docstring at the top of each file.
* Use Markdown for formatting.
* Do **not** include any reStructuredText markup such as double backticks.
* Provide docstrings for all modules, classes, properties, and functions, including internal helpers prefixed with an underscore.
* Provide docstrings for all modules, classes, properties, and functions, including internal helpers prefixed with an underscore.
  * Provide docstrings for property setters as well as getters when they are defined.
  * Provide docstrings for `TypedDict` classes, enums, and other public type definitions.
  * `@overload` stubs do not need docstrings when the concrete implementation is documented.
* Document class attributes using triple-quoted strings immediately below each instead of relying only on an `Attributes` section in the class docstring.
* Format docstrings using Google style, with the following tweaks:
  * Use `Arguments:` instead of `Args:`.
  * Do not include an `Arguments:` section for functions or methods that take no arguments.
  * In argument descriptions, the first word after the colon should be lowercase unless it is a type name.
  * Do not include a blank line between the `Arguments:` and `Returns:` sections.
  * Do not include a `Returns:` section for functions or methods that return None.
  * In the `Returns:` section, the first word should be lowercase unless it is a type name.
