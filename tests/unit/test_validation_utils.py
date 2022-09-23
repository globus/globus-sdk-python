import uuid

import pytest

from globus_sdk.validation_utils import (
    UUID_REGEX,
    LenValidator,
    ListValidator,
    RegexValidator,
)


def test_len_validator():
    validator = LenValidator(10, 100)

    assert validator.validate("a" * 80) == "a" * 80
    with pytest.raises(ValueError):
        validator.validate("a")
    with pytest.raises(ValueError):
        validator.validate("a" * 101)


def test_regex_validator():
    uuid_validator = RegexValidator(UUID_REGEX)

    test_uuid = str(uuid.uuid4())
    assert uuid_validator.validate(test_uuid) == test_uuid
    with pytest.raises(ValueError):
        uuid_validator.validate("a")


def test_list_validator():
    len_validator = LenValidator(10, 100)
    validator = ListValidator(len_validator)

    valid_list = ["a" * 20, "a" * 70, "a" * 30]
    invalid_list = ["a" * 10, "a" * 300, "a" * 34]
    assert validator.validate(valid_list) == valid_list
    with pytest.raises(ValueError):
        validator.validate(invalid_list)
