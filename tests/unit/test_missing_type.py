import copy
import pickle

import pytest

from globus_sdk._missing import MISSING, MissingType


def test_missing_type_cannot_be_instantiated():
    with pytest.raises(TypeError, match="MissingType should not be instantiated"):
        MissingType()


def test_missing_sentinel_bools_as_false():
    assert bool(MISSING) is False


def test_str_of_missing():
    assert str(MISSING) == "<globus_sdk.MISSING>"


def test_copy_of_missing_is_self():
    assert copy.copy(MISSING) is MISSING
    assert copy.deepcopy(MISSING) is MISSING


def test_pickle_of_missing_is_self():
    assert pickle.loads(pickle.dumps(MISSING)) is MISSING
