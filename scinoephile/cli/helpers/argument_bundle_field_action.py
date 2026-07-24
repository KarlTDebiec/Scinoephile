#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Argument actions for bundled CLI option groups."""

from __future__ import annotations

from argparse import Action, ArgumentParser, Namespace
from dataclasses import replace
from typing import Any

__all__ = ["ArgumentBundleFieldAction"]


class ArgumentBundleFieldAction(Action):
    """Update one field on a dataclass-backed argument bundle."""

    def __init__(
        self,
        option_strings: list[str],
        dest: str,
        *,
        bundle_type: type[Any],
        field_name: str,
        **kwargs: Any,
    ):
        """Initialize.

        Arguments:
            option_strings: option strings
            dest: namespace destination for the bundled dataclass
            bundle_type: dataclass type stored at dest
            field_name: dataclass field to update when this argument is used
            **kwargs: additional argparse action keyword arguments
        """
        self.bundle_type = bundle_type
        self.field_name = field_name
        kwargs.setdefault("default", bundle_type())
        super().__init__(option_strings=option_strings, dest=dest, **kwargs)

    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: Any,
        option_string: str | None = None,
    ):
        """Apply an argument value to the bundle field.

        Arguments:
            parser: active argument parser
            namespace: argparse namespace
            values: parsed argument value
            option_string: option string used
        """
        if self.nargs == 0:
            values = self.const
        bundle = getattr(namespace, self.dest, None)
        if not isinstance(bundle, self.bundle_type):
            bundle = self.bundle_type()
        try:
            updated_bundle = replace(bundle, **{self.field_name: values})
        except TypeError as err:
            argument_name = option_string or self.dest
            parser.error(
                f"{argument_name} cannot update argument bundle field "
                f"{self.field_name!r}: {err}"
            )
        setattr(namespace, self.dest, updated_bundle)
