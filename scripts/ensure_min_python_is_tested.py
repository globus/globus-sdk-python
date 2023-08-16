#!/usr/bin/env python
# requires that a YAML implementation is available in order to extract github
# workflows data
import pathlib
import subprocess
import sys

try:
    import ruamel.yaml
except ImportError:
    raise ImportError(
        "ruamel.yaml is required to run this script. "
        "Please ensure that you are invoking it with "
        "'tox r -e check-min-python-is-tested'."
    )

YAML = ruamel.yaml.YAML(typ="safe")
REPO_ROOT = pathlib.Path(__file__).parent.parent

proc = subprocess.run(
    ["python", "scripts/get_python_requires.py"],
    check=True,
    capture_output=True,
    cwd=REPO_ROOT,
)
requires_python_version = proc.stdout.decode().strip()

with open(REPO_ROOT / ".github" / "workflows" / "build.yaml") as f:
    workflow = YAML.load(f)
    try:
        test_mindeps_job = workflow["jobs"]["test-mindeps"]
    except KeyError:
        raise ValueError("Could not find the test-mindeps job. Perhaps it has moved?")

    job_steps = test_mindeps_job["steps"]
    for step in job_steps:
        if "uses" in step and "actions/setup-python" in step["uses"]:
            setup_python_step = step
            break
    else:
        raise ValueError("Could not find the setup-python step.")

    python_version = setup_python_step["with"]["python-version"]
    if python_version != requires_python_version:
        print("ERROR: ensure_min_python_is_tested.py failed!")
        print(
            f"\nPackage data sets 'Requires-Python: >={requires_python_version}', "
            f"but the test-mindeps job is configured to test '{python_version}'.\n",
            file=sys.stderr,
        )
        sys.exit(1)