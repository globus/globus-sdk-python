import os.path

from setuptools import find_packages, setup

# single source of truth for package version
version_ns = {}  # type: ignore
with open(os.path.join("globus_sdk", "version.py")) as f:
    exec(f.read(), version_ns)

setup(
    name="globus-sdk",
    version=version_ns["__version__"],
    description="Globus SDK for Python",
    long_description=open("README.rst").read(),
    author="Globus Team",
    author_email="support@globus.org",
    url="https://github.com/globus/globus-sdk-python",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.6",
    install_requires=["requests>=2.9.2,<3.0.0", "pyjwt[crypto]>=1.5.3,<2.0.0"],
    extras_require={
        # the dev extra is for SDK developers only
        "dev": [
            # drive testing with tox
            "tox>=3.5.3,<4.0",
            # linting
            "flake8>=3.0,<4.0",
            "isort>=5.6.4,<6.0",
            "black==20.8b1",
            "flake8-bugbear==20.11.1",
            "mypy==0.800",
            # testing
            "pytest<7.0",
            "pytest-cov<3.0",
            "pytest-xdist<2.0",
            # mocking HTTP responses
            "responses==0.12.1",
            # pyinstaller is needed in order to test the pyinstaller hook
            "pyinstaller",
            # builds + uploads to pypi
            "twine>=3,<4",
            "wheel==0.36.2",
            # docs
            "sphinx==3.4.3",
            "sphinx-material==0.0.32",
        ]
    },
    entry_points={
        "pyinstaller40": ["hook-dirs = globus_sdk._pyinstaller:get_hook_dirs"]
    },
    include_package_data=True,
    keywords=["globus", "file transfer"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
