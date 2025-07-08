import collections.abc
import uuid

import pytest

from globus_sdk import MISSING
from globus_sdk._internal.remarshal import (
    commajoin,
    list_map,
    listify,
    strseq_iter,
    strseq_listify,
)


@pytest.mark.parametrize(
    "value, expected_result",
    (
        ("foo", ["foo"]),
        ((1, 2, 3), ["1", "2", "3"]),
        (uuid.UUID(int=10), [f"{uuid.UUID(int=10)}"]),
        (["foo", uuid.UUID(int=5)], ["foo", f"{uuid.UUID(int=5)}"]),
    ),
)
def test_strseq_iter(value, expected_result):
    iter_ = strseq_iter(value)
    assert not isinstance(iter_, list)
    assert isinstance(iter_, collections.abc.Iterator)
    assert list(iter_) == expected_result
    assert list(iter_) == []


@pytest.mark.parametrize(
    "value, expected_result",
    (
        ("foo", ["foo"]),
        ((1, 2, 3), ["1", "2", "3"]),
        (uuid.UUID(int=10), [f"{uuid.UUID(int=10)}"]),
        (["foo", uuid.UUID(int=5)], ["foo", f"{uuid.UUID(int=5)}"]),
        (MISSING, MISSING),
        (None, None),
    ),
)
def test_strseq_listify(value, expected_result):
    list_ = strseq_listify(value)
    assert isinstance(list_, list) or list_ in (MISSING, None)
    assert list_ == expected_result


@pytest.mark.parametrize(
    "value, expected_result",
    (
        ("foo", "foo"),
        (uuid.UUID(int=10), f"{uuid.UUID(int=10)}"),
        ((1, 2, 3), "1,2,3"),
        (range(5), "0,1,2,3,4"),
        (["foo", uuid.UUID(int=5)], f"foo,{uuid.UUID(int=5)}"),
        (MISSING, MISSING),
        (None, None),
    ),
)
def test_commajoin(value, expected_result):
    joined = commajoin(value)
    assert joined == expected_result


@pytest.mark.parametrize(
    "value, expected_result",
    (
        ("foo", ["f", "o", "o"]),
        ((1, 2, 3), [1, 2, 3]),
        (range(5), [0, 1, 2, 3, 4]),
        (["foo", uuid.UUID(int=5)], ["foo", uuid.UUID(int=5)]),
        (MISSING, MISSING),
        (None, None),
    ),
)
def test_listify(value, expected_result):
    converted = listify(value)
    assert converted == expected_result


@pytest.mark.parametrize(
    "value, expected_result",
    (
        ("foo", ["ff", "oo", "oo"]),
        ((1, 2, 3), [2, 4, 6]),
        (range(5), [0, 2, 4, 6, 8]),
        (MISSING, MISSING),
        (None, None),
    ),
)
def test_list_map(value, expected_result):
    converted = list_map(value, lambda x: x * 2)
    assert converted == expected_result
