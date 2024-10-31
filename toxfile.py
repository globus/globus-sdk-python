"""
This is a very small 'tox' plugin.
'toxfile.py' is a special name for auto-loading a plugin without defining package
metadata.

For full doc, see: https://tox.wiki/en/latest/plugins.html

Methods decorated below with `tox.plugin.impl` are hook implementations.
We only implement hooks which we need.
"""

from __future__ import annotations

import pathlib
import shutil
import typing as t

from tox.plugin import impl

if t.TYPE_CHECKING:
    from tox.tox_env.api import ToxEnv

REPO_ROOT = pathlib.Path(__file__).parent
BUILD_DIR = REPO_ROOT / "build"


@impl
def tox_on_install(
    tox_env: ToxEnv, arguments: t.Any, section: str, of_type: str
) -> None:
    # when setting up the wheel build, clear the 'build/' directory if present
    if tox_env.name != "build_wheel":
        return
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
