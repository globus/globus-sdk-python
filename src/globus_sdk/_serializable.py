from __future__ import annotations

import inspect
import sys
import typing as t

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


class Serializable:
    """
    This is a base class for helpers which represent data which can be
    loaded to or from a dictionary.

    Serializable classes:
    - know what fields they have, based on their initializer signatures
    - support `to_dict()` and `from_dict()` conversions
    - typically use `globus_sdk._guards.validators` to check attribute types
    """

    _EXCLUDE_VARS: t.ClassVar[tuple[str, ...]] = ("self", "extra")
    extra: dict[str, t.Any]

    @classmethod
    def _supported_fields(cls) -> list[str]:
        signature = inspect.signature(cls.__init__)
        return [
            name
            for name in signature.parameters.keys()
            if name not in cls._EXCLUDE_VARS
        ]

    @classmethod
    def from_dict(cls, data: dict[str, t.Any]) -> Self:
        """
        Instantiate from a dictionary.

        :param data: The dictionary to create the error from.
        """

        # Extract any extra fields
        extras = {k: v for k, v in data.items() if k not in cls._supported_fields()}
        kwargs: dict[str, t.Any] = {"extra": extras}
        # Ensure required fields are supplied
        for field_name in cls._supported_fields():
            kwargs[field_name] = data.get(field_name)

        return cls(**kwargs)

    def to_dict(self, include_extra: bool = False) -> dict[str, t.Any]:
        """
        Render to a dictionary.

        :param include_extra: Whether to include stored extra (non-standard) fields in
            the returned dictionary.
        """
        result = {}

        # Set any authorization parameters
        for field in self._supported_fields():
            value = getattr(self, field)
            if value is not None:
                if isinstance(value, Serializable):
                    value = value.to_dict(include_extra=include_extra)
                result[field] = value

        # Set any extra fields
        if include_extra:
            result.update(self.extra)

        return result
