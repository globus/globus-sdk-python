"""
Definition and loading of standard environment variables, plus a wrappers for loading
and parsing values.

This does not include service URL env vars (see environments.py for loading of those)
"""

from __future__ import annotations

import logging
import os
import pathlib
import typing as t

log = logging.getLogger(__name__)

ENVNAME_VAR = "GLOBUS_SDK_ENVIRONMENT"
HTTP_TIMEOUT_VAR = "GLOBUS_SDK_HTTP_TIMEOUT"
SSL_VERIFY_VAR = "GLOBUS_SDK_VERIFY_SSL"


def get_environment_name(inputenv: str | None = None) -> str:
    if inputenv is None:
        value = os.getenv(ENVNAME_VAR, "production")
    else:
        value = inputenv
    log.debug(f"get_environment_name() got value: {value}")
    return value


def get_ssl_verify(value: bool | str | pathlib.Path | None = None) -> bool | str:
    if value is None:
        value = os.getenv(SSL_VERIFY_VAR, "1")
    value = _ssl_verify_cast(value)
    log.debug(f"get_ssl_verify() got value: {value}")
    return value


def get_http_timeout(value: float | None = None) -> float | None:
    if value is not None:
        result: float = value
    else:
        var = os.getenv(HTTP_TIMEOUT_VAR, "60")

        # TODO: re-evaluate converting `""` to a default timeout -- it seems like this
        # should error instead, but the behavior has been established for a long time,
        # so will need proper deprecation
        if var == "":
            result = 60.0
        else:
            result = _float_cast(var)

    log.debug(f"get_http_timeout() got value: {result}")
    if result == -1.0:
        return None
    return result


def _ssl_verify_cast(value: t.Any) -> bool | str:
    if isinstance(value, bool):
        return value
    if not isinstance(value, (str, pathlib.Path)):
        msg = f"Value {value} of type {type(value)} cannot be used for SSL verification"
        raise ValueError(msg)
    if isinstance(value, str):
        if value.lower() in {"y", "yes", "t", "true", "on", "1"}:
            return True
        if value.lower() in {"n", "no", "f", "false", "off", "0"}:
            return False
        if os.path.isfile(value):
            return value
    if isinstance(value, pathlib.Path) and value.is_file():
        return str(value.absolute())
    raise ValueError(
        "SSL verification value must be a valid boolean value "
        f"or a path to a file that exists (got {value})"
    )


def _float_cast(value: str) -> float:
    try:
        return float(value)
    except ValueError as e:
        log.error(f'Value "{value}" can\'t cast to float')
        raise ValueError(f"Invalid config float: {value}") from e
