import pytest

from globus_sdk.scopes import ScopeParser, TransferScopes


def _make_deep_scope(depth):
    big_scope = ""
    for i in range(depth):
        big_scope += f"foo{i}["
    big_scope += "bar"
    for _ in range(depth):
        big_scope += "]"
    return big_scope


def _make_wide_scope(width):
    big_scope = ""
    for i in range(width):
        big_scope += f"foo{i} "
    return big_scope


def test_ordinary_scope_parsing(benchmark):
    scope_string = f"openid profile {TransferScopes.all}"
    benchmark(ScopeParser.parse, scope_string)


@pytest.mark.parametrize("depth", (10, 100, 1000, 2000, 3000, 4000, 5000))
def test_deep_scope_parsing(benchmark, depth):
    scope_string = _make_deep_scope(depth)
    benchmark(ScopeParser.parse, scope_string)


@pytest.mark.parametrize("width", (5000, 10000))
def test_wide_scope_parsing(benchmark, width):
    scope_string = _make_wide_scope(width)
    benchmark(ScopeParser.parse, scope_string)
