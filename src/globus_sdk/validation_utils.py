from __future__ import annotations

import re
from typing import Any, Pattern

UUID_REGEX = "([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})"  # noqa E501
AUTH_URN_REGEX = f"(urn:globus:(auth:identity|groups:id):{UUID_REGEX})"


class Validator:
    """
    Validation Interface
    """

    def validate(self, value: Any, key: str | None = None) -> Any:
        """
        To be implemented by subclasses

        :param value: Value to be validated
        :param key: Optional identifying key
            (used to more intelligently decorate error strings)
        :raises ValueError: on validation failure
        :returns: value on validation success
        """
        raise NotImplementedError()


class LenValidator(Validator):
    """
    Validates an iterable value falls between length constraints
    """

    def __init__(
        self,
        min_len: int = 0,
        max_len: int | float = float("inf"),
    ):
        self._min_len = min_len
        self._max_len = max_len

    def validate(self, value: Any, key: str | None = None) -> Any:
        if not (self._min_len <= len(value) <= self._max_len):
            identifier = f"Value '{value}'" if key is None else f"Key '{key}'"

            raise ValueError(
                f"{identifier} failed length constraint. "
                f"Length must be >= {self._min_len} and <= {self._max_len}. "
                f"Was {len(value)}"
            )
        return value


class RegexValidator(Validator):
    """
    Validates a string value matches a specified pattern
    """

    def __init__(self, pattern: str | Pattern[str]):
        self._pattern = re.compile(pattern) if isinstance(pattern, str) else pattern

    def validate(self, value: str, key: str | None = None) -> str:
        if self._pattern.fullmatch(value) is None:
            identifier = f"Value '{value}'" if key is None else f"Key '{key}'"

            raise ValueError(
                f"{identifier} failed regex validation. "
                f"Did not match pattern '{self._pattern.pattern}'"
            )
        return value


class ListValidator(Validator):
    """
    Validates all elements of a list value are valid based on a provided sub validator

    This validator in tandem with LenValidator for example could validate that
        no string in a list of strings is > 128 chars
    """

    def __init__(
        self,
        validator: Validator,
    ):
        self._validator = validator

    def validate(self, value: list[Any], key: str | None = None) -> Any:
        for elem in value:
            try:
                self._validator.validate(elem)
            except ValueError as e:
                identifier = f"Value '{value}'" if key is None else f"Key '{key}'"
                raise ValueError(f"{identifier} failed validation. {str(e)}") from e
        return value
