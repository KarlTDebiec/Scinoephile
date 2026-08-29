# Docstring Guide

## Coverage

* Include a module docstring at the top of each file.
* Provide docstrings for all modules, classes, properties, and functions,
  including internal helpers prefixed with an underscore.
  * Provide docstrings for property setters as well as getters when they are
    defined.
  * Provide docstrings for `TypedDict` classes, enums, and other public type
    definitions.
  * `@overload` stubs do not need docstrings when the concrete implementation is
    documented.
* Document class attributes using triple-quoted strings immediately below each
  attribute instead of relying only on an `Attributes` section in the class
  docstring.

## Formatting

* Use Markdown and do not include reStructuredText markup such as double
  backticks.
* Use Google-style docstrings with `Arguments:` instead of `Args:`.
* Begin descriptions in `Arguments:`, `Returns:`, and `Yields:` with a lowercase
  word unless the first word is a type name.
* Do not include a blank line between adjacent `Arguments:`, `Raises:`,
  `Returns:`, or `Yields:` sections.

## Sections

| Section | Requirement |
| --- | --- |
| `Arguments:` | Include when the callable has parameters that require documentation; omit when it does not. |
| `Returns:` | Include when the callable returns a value, including typed abstract methods and interface stubs. Omit when it returns `None`. A property or cached-property getter, pytest fixture, or `@model_validator(mode="after")` method may instead describe its value in the summary. |
| `Yields:` | Include for generators and context managers that contain `yield` or `yield from`; omit when the callable does not yield. |
| `Raises:` | Include when the callable contains an explicit `raise`. It may also document exceptions propagated from callees. A sole `raise NotImplementedError` in an abstract method is a contract placeholder and does not require this section. |
