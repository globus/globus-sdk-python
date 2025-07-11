import importlib.metadata
import logging
import sys

from ._internal.lazy_import import (
    default_dir_implementation,
    default_getattr_implementation,
    load_all_tuple,
)

__version__ = importlib.metadata.distribution("globus_sdk").version


def _force_eager_imports() -> None:
    current_module = sys.modules[__name__]

    for attr in __all__:
        getattr(current_module, attr)


#
# all lazy SDK attributes are defined in __init__.pyi
#
# to add an attribute, write the relevant import in `__init__.pyi` and update
# the `__all__` tuple there
#
__all__ = load_all_tuple(__name__, "__init__.pyi")
__getattr__ = default_getattr_implementation(__name__, "__init__.pyi")
__dir__ = default_dir_implementation(__name__)

del load_all_tuple
del default_getattr_implementation
del default_dir_implementation


# configure logging for a library, per python best practices:
# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
logging.getLogger("globus_sdk").addHandler(logging.NullHandler())
