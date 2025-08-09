"""
This is a very small 'tox' plugin.
'toxfile.py' is a special name for auto-loading a plugin without defining package
metadata.

For full doc, see: https://tox.wiki/en/latest/plugins.html

Methods decorated below with `tox.plugin.impl` are hook implementations.
We only implement hooks which we need.
"""

from __future__ import annotations

import logging
import pathlib
import shutil
import typing as t

from tox.plugin import impl

if t.TYPE_CHECKING:
    from tox.config.sets import EnvConfigSet
    from tox.session.state import State
    from tox.tox_env.api import ToxEnv

log = logging.getLogger(__name__)

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


@impl
def tox_add_env_config(env_conf: EnvConfigSet, state: State) -> None:
    env_conf.add_config(
        keys=["globus_sdk_rmtree"],
        of_type=list[str],
        default=[],
        desc="A dir tree to remove before running the environment commands",
    )


@impl
def tox_before_run_commands(tox_env: ToxEnv) -> None:
    # determine if it was a parallel invocation by examining the CLI command
    parallel_detected = tox_env.options.command in ("p", "run-parallel")
    if parallel_detected:
        # tox is running parallel, set an indicator env var
        # and effectively disable pytest-xdist by setting xdist-workers to 0
        # -- 0 means tests will run in the main process, not even in a worker
        setenv = tox_env.conf.load("set_env")
        setenv.update({"TOX_PARALLEL": "1", "PYTEST_XDIST_AUTO_NUM_WORKERS": "0"})

    sdk_rmtree = tox_env.conf.load("globus_sdk_rmtree")
    for name in sdk_rmtree:
        path = pathlib.Path(name)
        if path.exists():
            log.warning(f"globus_sdk_rmtree: {path}")
            shutil.rmtree(path)
