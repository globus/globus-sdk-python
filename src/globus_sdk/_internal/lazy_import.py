"""
Tooling for an extremely simple lazy-import system, based on inspection of
pyi files.

Given a base module name (used for lookup and error messages) and the name
of a pyi file, we can use the pyi file to lookup import locations.

i.e. Given

  foo.py
  foo.pyi
  bar.py

then if `foo.pyi` has an import `from .bar import BarType`, it is possible to
*read* `foo.pyi` at runtime and use that information to load
`BarType` from `bar`.


Rationale
---------

Why use this type of lazy importer?

The major goals are:
- type information is still available to type checkers (and other tools like IDEs)
- we minimize manual duplication of names
- we minimize specialized knowledge needed to update our package exports
- the lazy importer itself is easy to maintain and update

``.pyi`` type stubs are designed for use with type checkers. The data format choice here
is "regular type stubs". We treat it as runtime data, which is a bit unusual, but we
are guaranteed that `mypy` and other tools can understand it without issue.

We reduce duplication with this technique, and the content in the ``.pyi`` file should
be easy for most developers to read and modify.
"""

from __future__ import annotations

import ast
import sys
import typing as t


def load_all_tuple(modname: str, pyi_filename: str) -> tuple[str, ...]:
    """
    Load the __all__ tuple from a ``.pyi`` file.

    This should run before the getattr and dir implementations are defined, as those use
    the runtime ``__all__`` tuple.

    :param modname: The name of the module doing the load. Usually ``__name__``.
    :param pyi_filename: The name of the ``pyi`` file relative to ``modname``.
        ``importlib.resources`` will use both of these fields to load the ``pyi``
        data, so the file must be in package metadata.
    """
    return _ParsedPYIData.load(modname, pyi_filename).all_names


def default_getattr_implementation(
    modname: str, pyi_filename: str
) -> t.Callable[[str], t.Any]:
    """
    Build an implementation of module ``__getattr__`` given the module name and
    the pyi file which will drive lazy imports.

    :param modname: The name of the module where ``__getattr__`` is being added.
        Usually ``__name__``.
    :param pyi_filename: The name of the ``pyi`` file relative to ``modname``.
        ``importlib.resources`` will use both of these fields to load the ``pyi``
        data, so the file must be in package metadata.
    """
    module_object = sys.modules[modname]
    all_tuple = module_object.__all__

    def getattr_implementation(name: str) -> t.Any:
        if name in all_tuple:
            value = load_attr(modname, pyi_filename, name)
            setattr(module_object, name, value)
            return value

        raise AttributeError(f"module {modname} has no attribute {name}")

    return getattr_implementation


def default_dir_implementation(modname: str) -> t.Callable[[], list[str]]:
    """
    Build an implementation of module ``__dir__`` given the module name.

    :param modname: The name of the module where ``__dir__`` is being added.
        Usually ``__name__``.
    """
    # dir(globus_sdk) should include everything exported in __all__
    # as well as some explicitly selected attributes from the default dir() output
    # on a module
    #
    # see also:
    # https://discuss.python.org/t/how-to-properly-extend-standard-dir-search-with-module-level-dir/4202
    module_object = sys.modules[modname]
    all_tuple = module_object.__all__

    def dir_implementation() -> list[str]:
        return list(all_tuple) + [
            # __all__ itself can be inspected
            "__all__",
            # useful to figure out where a package is installed
            "__file__",
            "__path__",
        ]

    return dir_implementation


def load_attr(modname: str, pyi_filename: str, attrname: str) -> t.Any:
    """
    Execute an import of a single attribute in the manner that it was declared in a
    ``.pyi`` file.

    The import in the pyi data is expected to be a `from x import y` statement.
    Only the specific attribute will be imported, even if the pyi declares multiple
    imports from the same module.

    :param modname: The name of the module importing the attribute.
        Usually ``__name__``.
    :param pyi_filename: The name of the ``pyi`` file relative to ``modname``.
        ``importlib.resources`` will use both of these fields to load the ``pyi``
        data, so the file must be in package metadata.
    :param attrname: The name of the attribute to load.
    """
    import importlib

    attr_source = find_source_module(modname, pyi_filename, attrname)
    attr_source_mod = importlib.import_module(attr_source, modname)
    return getattr(attr_source_mod, attrname)


def find_source_module(modname: str, pyi_filename: str, attrname: str) -> str:
    """
    Find the source module which provides an attribute, based on a declared import in a
    ``.pyi`` file.

    The ``.pyi`` data will be parsed as AST and scanned for an appropriate import.

    :param modname: The name of the module importing the attribute.
        Usually ``__name__``.
    :param pyi_filename: The name of the ``pyi`` file relative to ``modname``.
        ``importlib.resources`` will use both of these fields to load the ``pyi``
        data, so the file must be in package metadata.
    :param attrname: The name of the attribute to load.
    """
    parsed = _ParsedPYIData.load(modname, pyi_filename)
    return parsed.module_for_attr(attrname)


class _ParsedPYIData:
    _CACHE: dict[tuple[str, str], _ParsedPYIData] = {}

    @classmethod
    def load(cls, module_name: str, pyi_filename: str) -> _ParsedPYIData:
        if (module_name, pyi_filename) not in cls._CACHE:
            cls._CACHE[(module_name, pyi_filename)] = cls(module_name, pyi_filename)
        return cls._CACHE[(module_name, pyi_filename)]

    def __init__(self, module_name: str, pyi_filename: str) -> None:
        self.module_name = module_name
        self.pyi_filename = pyi_filename
        self._ast = _parse_pyi_ast(module_name, pyi_filename)

        self._import_attr_map: dict[str, str] = {}
        self._all_names: list[str] = []

        self._load()

    @property
    def all_names(self) -> tuple[str, ...]:
        return tuple(self._all_names)

    def module_for_attr(self, attrname: str) -> str:
        if attrname not in self._import_attr_map:
            raise LookupError(
                f"Could not find import of '{attrname}' in '{self.module_name}'."
            )
        return self._import_attr_map[attrname]

    def _load(self) -> None:
        for statement in self._ast.body:
            self._load_statement(statement)

    def _load_statement(self, statement: ast.AST) -> None:
        if isinstance(statement, ast.ImportFrom):
            # type ignore the possibility of 'import_from.module == None'
            # as it's not possible from parsed code
            module_name = (  # type: ignore[operator]
                "." * statement.level
            ) + statement.module

            for alias in statement.names:
                attr_name = alias.name if alias.asname is None else alias.asname
                self._import_attr_map[attr_name] = module_name
        elif isinstance(statement, ast.Assign):
            if len(statement.targets) != 1:
                return
            target = statement.targets[0]
            if not isinstance(target, ast.Name):
                return
            if target.id != "__all__":
                return
            if not isinstance(statement.value, ast.Tuple):
                raise ValueError(
                    f"While reading '__all__' for '{self.module_name}' from "
                    f"'{self.pyi_filename}', '__all__' was not a tuple "
                )
            for element in statement.value.elts:
                if not isinstance(element, ast.Constant):
                    continue
                self._all_names.append(element.value)


def _parse_pyi_ast(anchor_module_name: str, pyi_filename: str) -> ast.Module:
    import importlib.resources

    if sys.version_info >= (3, 9):
        source = (
            importlib.resources.files(anchor_module_name)  # pylint: disable=no-member
            .joinpath(pyi_filename)
            .read_bytes()
        )
    else:
        source = importlib.resources.read_binary(  # pylint: disable=deprecated-method
            anchor_module_name, pyi_filename
        )
    return ast.parse(source)
