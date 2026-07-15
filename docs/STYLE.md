# Style Guide

## Python Version
* Target **Python 3.13** features where applicable; do not worry about
  compatibility with earlier versions.

## Copyright
* Include the standard two-line copyright header at the top of the file.

## Formatting
* Allow `ruff format` to manage code formatting details.

## Imports
* Include `from __future__ import annotations` in Python modules that contain
  imports, exports, type annotations, functions, or classes. Pure package marker
  files that contain only a module docstring do not need it.
* Use single-dot relative imports for imports rooted in the module's containing
  package, including its modules and child packages (for example,
  `from .foo import bar` or `from .child.foo import bar`).
* Use the absolute path to the concrete module or package for imports that must
  climb to a parent package or reach one of its other children. Do not use
  multi-dot relative imports (for example, `from ..foo import bar`).
* Public names may be imported from another package's `__init__.py` facade when
  they are listed in that package's `__all__`.
* Within a package subtree, do not import a name re-exported by one of the
  module's own ancestor package facades. Import from the concrete module that
  owns the name so internal dependencies remain visible (for example, use
  `from scinoephile.core.exceptions import ScinoephileError` within
  `scinoephile.core.llms`, not `from scinoephile.core import ScinoephileError`).
* Use `if TYPE_CHECKING:` blocks only when necessary to avoid circular imports.
* Allow `ruff` to manage import sorting.

## Exports
* Include `__all__` in Python modules that export public names.
* Do not include empty `__all__` assignments.
* If `__all__` contains one entry, keep it on one line, such as
  `__all__ = ["foo"]`.
* If `__all__` contains multiple entries, include a trailing comma after the
  last entry so `ruff` formats it as one item per line.
* `__all__` should list the intended public API for the module.
* Do not include internal helpers, which are names prefixed with an underscore.
* In `__init__.py` files, only import classes from the module, not functions or
  variables.

## Organization
* Within classes, sort methods in the following hierarchy:
  1. Level 1: `__init__`, other builtins, public properties, public methods,
     private properties, private methods
  2. Level 2: standard methods, class methods, static methods
  3. Level 3: alphabetical order
* Within modules, sort functions using the same hierarchy described for class
  methods:
  1. Level 1: public functions, private functions prefixed with an underscore
  2. Level 2: standard functions, then decorator-based variants where
     applicable, such as `@overload`
  3. Level 3: alphabetical order

## Nomenclature
* Use explicit path nomenclature:
  * variables or parameters holding `Path` objects should end in `_path`, such
    as `file_path`, `dir_path`, or `cache_dir_path`
  * bare `path` or `paths` parameters are acceptable for small path-focused
    helpers where no more specific role name applies
  * CLI-facing argument names may use conventional command-line terms such as
    `infile` and `outfile` without a `_path` suffix
  * generic validator inputs may use `value` or `value_to_validate`, even when
    the accepted type includes paths
  * use `*_name` for bare names and `*_stem` for stems, not for full paths
  * prefer `*_dir_path` over `*_directory` when the value is a path

## Style
* Exclusively use f-strings for string interpolation.
* Where possible, classes should implement `__repr__` methods such that they may
  be reconstructed from its `repr` output.
* Avoid ternary expressions; prefer explicit `if`/`else` statements for
  readability.
* Do not create public methods that only delegate to private methods with the
  same behavior. If the behavior belongs in the public API, put the
  implementation in the public method directly.
* Keep straightforward, single-use logic inline. Do not split logic into a
  helper solely to name a short expression, hide a few lines, or make a
  function look more organized.
  * Before a function is roughly 50 lines, extract a helper only when it is
    reused, isolates a genuinely separate operation, or materially improves
    testability.
  * Do not add one-line wrappers or predicates for logic that is clearer at the
    call site.
  * Prefer local variables and direct conditionals over private helpers for
    simple type narrowing, option selection, and guard checks.
* Use one-line block comments above continuous blocks of code when they help
  separate the steps of nontrivial logic; do not end these comments with
  periods.

## Type Annotations
* Include type annotations for all function and method signatures, with the
  following exception:
  * If a function always returns `None`, omit the return type annotation.
* Use `object` when a value may be any type but must be inspected or narrowed
  before type-specific use; use `Any` only for intentionally unchecked
  passthrough values, and use a narrower type, protocol, `TypedDict`, or alias
  when the shape is known.

## Exceptions
* Raise `ScinoephileError` for Scinoephile domain failures that should be shown
  directly to CLI users.
* Raise built-in exceptions such as `ValueError`, `TypeError`, `IndexError`,
  and `OSError` subclasses for programming errors, generic validation failures,
  and low-level helper or parser failures.
* Public Scinoephile operations should wrap lower-level exceptions in
  `ScinoephileError` when callers should not need to know
  implementation-specific failure types.
* CLI implementations should generally catch `ScinoephileError` and convert it
  to `parser.error(...)`.
* When wrapping a caught exception, use exception chaining with
  `raise ... from exc` to preserve context.

## Logging
* Use the `logging` module rather than `print` for any user-facing output in
  scripts or libraries.
* CLI tools may use `print` for intentional command output written to stdout.
  * Follow the repository pattern of defining a module-level
    `logger = getLogger(__name__)`.

## Command Line Interface
* In CLI modules, group arguments using the repository's standard
  `get_arg_groups_by_name(...)` helper when one is available.
  * Populated groups appear in this order:
    1. `positional arguments`
    2. `input arguments`
    3. `operation arguments`
    4. `llm arguments`
    5. `web arguments`
    6. `output arguments`
    7. `additional arguments`
    8. `additional help`
  * Omit groups that do not apply without changing the relative order of the
    remaining groups.
  * Rename the default optional group to `additional arguments` via
    `optional_arguments_name="additional arguments"`.
* Define CLI implementation methods with explicit keyword-only `_main`
  signatures whose parameters match the names produced by `argparse`; do not
  add per-CLI `TypedDict` classes just to type parsed kwargs.
* Use `dest=...` when command-line names should parse to Python-facing names
  such as `infile_path`, `outfile_path`, or `cache_dir_path`.
* Use argument `type=` validators, including `enum_arg(...)`, so `_main`
  receives the type it expects instead of reparsing strings.
  * Cache directory arguments should parse to `cache_dir_path` and include
    `(default: %(default)s)` in the help text.
* Base command CLIs that dispatch to subcommands should call the selected
  subcommand directly, such as
  `cls.subcommands()[subcommand_name]._main(**kwargs)`.
* CLI modules should support localization by defining a `localizations` mapping
  when the repository's CLI base supports it, and writing `help`,
  `description`, and argument-group titles using stable English strings that
  can be translated.
  * User-facing CLI help for the full command tree must have both `zh-hans`
    (`zho-Hans`) and `zh-hant` (`zho-Hant`) translations; do not leave new
    descriptions, argument help, or group titles to fall back to English.

## Testing
* Test modules do **not** need `__init__.py` files. Pytest can discover tests
  without them.

## Documentation
* Include a module docstring at the top of each file.
* Use Markdown for formatting.
* Do **not** include any reStructuredText markup such as double backticks.
* Provide docstrings for all modules, classes, properties, and functions,
  including internal helpers prefixed with an underscore.
* Provide docstrings for all modules, classes, properties, and functions,
  including internal helpers prefixed with an underscore.
  * Provide docstrings for property setters as well as getters when they are
    defined.
  * Provide docstrings for `TypedDict` classes, enums, and other public type
    definitions.
  * `@overload` stubs do not need docstrings when the concrete implementation
    is documented.
* Document class attributes using triple-quoted strings immediately below each
  instead of relying only on an `Attributes` section in the class docstring.
* Format docstrings using Google style, with the following tweaks:
  * Use `Arguments:` instead of `Args:`.
  * Do not include an `Arguments:` section for functions or methods that take no
    arguments.
  * In argument descriptions, the first word after the colon should be
    lowercase unless it is a type name.
  * Do not include a blank line between the `Arguments:` and `Returns:`
    sections.
  * Do not include a `Returns:` section for functions or methods that return
    None.
  * In the `Returns:` section, the first word should be lowercase unless it is a
    type name.
