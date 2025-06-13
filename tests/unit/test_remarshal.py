import collections.abc
import uuid

import pytest

from globus_sdk import MISSING
from globus_sdk._remarshal import commajoin, safe_strseq_iter, safe_strseq_listify


@pytest.mark.parametrize(
    "value, expected_result",
    (
        ("foo", ["foo"]),
        ((1, 2, 3), ["1", "2", "3"]),
        (uuid.UUID(int=10), [f"{uuid.UUID(int=10)}"]),
        (["foo", uuid.UUID(int=5)], ["foo", f"{uuid.UUID(int=5)}"]),
    ),
)
def test_safe_strseq_iter(value, expected_result):
    iter_ = safe_strseq_iter(value)
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
def test_safe_strseq_listify(value, expected_result):
    list_ = safe_strseq_listify(value)
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
    ),
)
def test_commajoin(value, expected_result):
    joined = commajoin(value)
    assert joined == expected_result
