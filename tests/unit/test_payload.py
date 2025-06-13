import abc

import pytest

from globus_sdk._payload import AbstractPayload, Payload


def test_payload_methods():
    # just make sure that PayloadWrapper acts like a dict...
    data = Payload()
    assert "foo" not in data
    with pytest.raises(KeyError):
        data["foo"]
    data["foo"] = 1
    assert "foo" in data
    assert data["foo"] == 1
    del data["foo"]
    assert "foo" not in data
    assert len(data) == 0
    assert list(data) == []
    data["foo"] = 1
    data["bar"] = 2
    assert len(data) == 2
    assert data == {"foo": 1, "bar": 2}
    data.update({"x": "hello", "y": "world"})
    assert data == {"foo": 1, "bar": 2, "x": "hello", "y": "world"}


def test_abstract_payload_detects_abstract_methods():
    # A has no abstract methods so it will instantiate
    class A(AbstractPayload):
        pass

    A()

    # B has an abstract method and inherits from AbstractPayload so it should
    # fail to instantiate
    class B(A):
        @abc.abstractmethod
        def f(self): ...

    with pytest.raises(
        TypeError,
        match=(
            "Can't instantiate abstract class B without an "
            "implementation for abstract method 'f'"
        ),
    ):
        B()

    # C has two abstract methods, so these should be listed comma separated
    class C(B):
        @abc.abstractmethod
        def g(self): ...

    with pytest.raises(
        TypeError,
        match=(
            "Can't instantiate abstract class C without an "
            "implementation for abstract methods ('f', 'g'|'g', 'f')"
        ),
    ):
        C()

    # D should be instantiable because it defines the abstract methods
    class D(C):
        def f(self):
            return 1

        def g(self):
            return 2

    D()
