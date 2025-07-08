from __future__ import annotations

import ast
import typing as t

CODEMAP: dict[str, str] = {
    # SDK001 is necessary for SDK002 enforcement to be easy
    # otherwise, we would have to have a more sophisticated linter which knows about
    # lexical scopes!
    "SDK001": "SDK001 loggers should be named 'log'",
    "SDK002": "SDK002 never use 'log.info'",
    # don't do `isinstance(x, MissingType)` -- use `x is MISSING` instead
    "SDK003": "SDK003 use `is MISSING`, not `isinstance(..., MissingType)`",
}


class Plugin:
    name = "globus-sdk-flake8"
    version = "1.0.0"

    # args to init determine plugin behavior. see:
    # https://flake8.pycqa.org/en/latest/plugin-development/plugin-parameters.html#indicating-desired-data
    #
    # by having "tree" as an init arg, we tell flake8 that we are an AST-handling
    # plugin, run once per file
    def __init__(self, tree: ast.AST) -> None:
        self.tree = tree

    # Plugin.run() is how checks will run. For detail, see implementation of:
    # https://flake8.pycqa.org/en/latest/internal/checker.html#flake8.checker.FileChecker.run_ast_checks
    def run(self) -> t.Iterator[tuple[int, int, str, type]]:
        visitor = SDKVisitor()
        visitor.visit(self.tree)
        for lineno, col, code in visitor.collect:
            yield lineno, col, CODEMAP[code], type(self)


class SDKVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.collect: list[tuple[int, int, str]] = []

    def _record(self, node: ast.expr | ast.stmt, code: str) -> None:
        self.collect.append((node.lineno, node.col_offset, code))

    def visit_Assign(self, node: ast.Assign) -> None:
        if matches_sdk001(node):
            self._record(node, "SDK001")

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if matches_sdk003(node):
            self._record(node, "SDK003")
        elif matches_sdk002(node):
            self._record(node, "SDK002")

        self.generic_visit(node)


def matches_sdk001(node: ast.Assign) -> bool:
    """
    A matcher for the SDK001 lint rule.

    Checks for `x = logging.getLogger(__name__)` where `x` is not `log`.

    :param node: the assignment statement AST node to check
    """
    # the value must be a call and must be using attr access in the function call
    # this eliminates bare funcs like `x = foo()` but allows `x = foo.bar()`
    if not (
        isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute)
    ):
        return False

    call_node: ast.Call = node.value
    func_node: ast.Attribute = node.value.func

    # make sure it's 'logging.getLogger' and no other function
    if not (
        func_node.attr == "getLogger"
        and isinstance(func_node.value, ast.Name)
        and func_node.value.id == "logging"
    ):
        return False

    # the assignee must be a single variable and it must be a name node
    if not (len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)):
        return False

    # if the assigned name is `log`, then it cannot be a match
    name_node: ast.Name = node.targets[0]
    if name_node.id == "log":
        return False

    # confirm that the `logging.getLogger` args are a single name -- that's the
    # form it will be when `__name__` is passed
    if len(call_node.args) != 1 or not isinstance(call_node.args[0], ast.Name):
        return False

    # if the argument is some other name, e.g. `logging.getLogger(my_variable)`,
    # then that cannot be a match
    logger_arg: ast.Name = call_node.args[0]
    if logger_arg.id != "__name__":
        return False

    return True  # all conditions met!


def matches_sdk002(node: ast.Call) -> bool:
    """
    A matcher for the SDK002 lint rule.

    Checks for `log.info(...)`

    :param node: the function call AST node to check
    """
    func_node = node.func
    # the function call must be of the form 'OBJ.info(...)'
    if not (isinstance(func_node, ast.Attribute) and func_node.attr == "info"):
        return False

    # and, more specifically, the object must be named 'log', so
    # it's `log.info(...)
    if not (isinstance(func_node.value, ast.Name) and func_node.value.id == "log"):
        return False

    return True  # all conditions met!


def matches_sdk003(node: ast.Call) -> bool:
    """
    A matcher for the SDK003 lint rule.

    Checks for `isinstance(x, MissingType)`

    :param node: the function call AST node to check
    """
    # it must be a call to a function named "isinstance"
    if not (isinstance(node.func, ast.Name) and node.func.id == "isinstance"):
        return False
    # if the number of arguments is improper, it can't be a violation (not a
    # valid 'isinstance' call)
    if len(node.args) != 2:
        return False
    right_hand_side = node.args[1]
    # the second argument must be the name 'MissingType'
    if not (
        isinstance(right_hand_side, ast.Name) and right_hand_side.id == "MissingType"
    ):
        return False

    return True  # all conditions met!
