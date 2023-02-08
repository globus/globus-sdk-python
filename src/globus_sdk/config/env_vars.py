"""
Definition and loading of standard environment variables, plus a wrappers for loading
and parsing values.

This does not include service URL env vars (see environments.py for loading of those)
"""
from __future__ import annotations

import logging
import os
import typing as t

log = logging.getLogger(__name__)
T = t.TypeVar("T")


ENVNAME_VAR = "GLOBUS_SDK_ENVIRONMENT"
HTTP_TIMEOUT_VAR = "GLOBUS_SDK_HTTP_TIMEOUT"
SSL_VERIFY_VAR = "GLOBUS_SDK_VERIFY_SSL"


def _str2bool(val: str) -> bool:
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError(f"invalid truth value: {val}")


@t.overload
def _load_var(
    varname: str,
    default: t.Any,
    explicit_value: t.Any | None,
    convert: t.Callable[[t.Any, t.Any], T],
) -> T:
    ...


@t.overload
def _load_var(
    varname: str,
    default: str,
    explicit_value: str | None,
) -> str:
    ...


def _load_var(
    varname: str,
    default: t.Any,
    explicit_value: t.Any | None = None,
    convert: t.Callable[[t.Any, t.Any], T] | None = None,
) -> t.Any:
    # use the explicit value if given and non-None, otherwise, do an env lookup
    value = (
        explicit_value if explicit_value is not None else os.getenv(varname, default)
    )
    if convert:
        value = convert(value, default)
    # only info log on non-default *values*
    # meaning that if we define the default as 'foo' and someone explicitly sets 'foo',
    # no info log gets emitted
    if value != default:
        log.info(f"on lookup, non-default setting: {varname}={value}")
    else:
        log.debug(f"on lookup, default setting: {varname}={value}")
    return value


def _bool_cast(value: t.Any, default: t.Any) -> bool:  # pylint: disable=unused-argument
    if isinstance(value, bool):
        return value
    elif not isinstance(value, str):
        raise ValueError(f"cannot cast value {value} of type {type(value)} to bool")
    return _str2bool(value)


def _optfloat_cast(value: t.Any, default: t.Any) -> float | None:
    try:
        return float(value)
    except ValueError:
        pass
    if value == "":
        return t.cast(float, default)
    log.error(f'Value "{value}" can\'t cast to optfloat')
    raise ValueError(f"Invalid config float: {value}")


def get_environment_name(inputenv: str | None = None) -> str:
    return _load_var(ENVNAME_VAR, "production", explicit_value=inputenv)


def get_ssl_verify(value: bool | None = None) -> bool:
    return _load_var(SSL_VERIFY_VAR, True, explicit_value=value, convert=_bool_cast)


def get_http_timeout(value: float | None = None) -> float | None:
    ret = _load_var(
        HTTP_TIMEOUT_VAR, 60.0, explicit_value=value, convert=_optfloat_cast
    )
    if ret == -1.0:
        return None
    return ret
