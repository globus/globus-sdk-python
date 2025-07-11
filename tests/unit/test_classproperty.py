from globus_sdk._internal.classprop import classproperty


def test_classproperty_simple():
    class Foo:
        x = {"x": 1}

        @classproperty
        def y(self_or_cls):
            return self_or_cls.x["x"]

    assert Foo.y == 1


def test_classproperty_prefers_instance():
    class Foo:
        x = {"x": 1}

        def __init__(self) -> None:
            self.x = {"x": 2}

        @classproperty
        def y(self_or_cls):
            return self_or_cls.x["x"]

    assert Foo.y == 1
    assert Foo().y == 2
