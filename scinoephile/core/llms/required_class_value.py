#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Typing contract for class values supplied by concrete LLM classes."""

from __future__ import annotations

__all__ = ["RequiredClassValue"]


class RequiredClassValue[T]:
    """Represent a class value expected from a concrete subclass.

    Subclasses shadow this descriptor with a normal class attribute. It does not
    prevent reassignment at runtime.
    """

    def __get__(self, instance: object | None, owner: type[object]) -> T:
        """Raise when a subclass has not supplied the class value.

        Arguments:
            instance: accessed instance, or None for class access
            owner: class through which the value was accessed
        Raises:
            AttributeError: if the concrete subclass has not supplied a value
        """
        raise AttributeError("Concrete subclass must provide this class value")
