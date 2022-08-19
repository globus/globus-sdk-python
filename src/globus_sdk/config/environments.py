import logging
import os
from typing import Any, Dict, List, Optional, Type, cast

from .env_vars import get_environment_name

log = logging.getLogger(__name__)
# the format string for a service URL pulled out of the environment
# these are handled with uppercased service names, e.g.
#   `GLOBUS_SDK_SERVICE_URL_SEARCH=...`
_SERVICE_URL_VAR_FORMAT = "GLOBUS_SDK_SERVICE_URL_{}"


class EnvConfig:
    envname: str
    domain: str
    no_dotapi: List[str] = ["app", "auth"]
    automate_services: List[str] = ["actions", "flows", "timer"]

    # this same dict is inherited (and therefore shared!) by all subclasses
    _registry: Dict[str, Type["EnvConfig"]] = {}

    # this is an easier hook to use than metaclass definition -- register every subclass
    # in this dict automatically
    #
    # as a result, anyone can define
    #
    #       class BetaEnv(EnvConfig):
    #           domain = "beta.foo.bar.example.com"
    #           envname = "beta"
    #
    # and retrieve it with get_config_by_name("beta")
    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        cls._registry[cls.envname] = cls

    @classmethod
    def get_service_url(cls, service: str) -> str:
        # you can override any name with a config attribute
        service_url_attr = f"{service}_url"
        if hasattr(cls, service_url_attr):
            return cast(str, getattr(cls, service_url_attr))

        # the typical pattern for a service hostname is X.api.Y
        # X=transfer, Y=preview.globus.org => transfer.api.preview.globus.org
        # check `no_dotapi` for services which don't have `.api` in their names
        if service in cls.no_dotapi:
            return f"https://{service}.{cls.domain}/"
        if service in cls.automate_services:
            return f"https://{cls.envname}.{service}.automate.globus.org/"
        return f"https://{service}.api.{cls.domain}/"

    @classmethod
    def get_by_name(cls, env: str) -> Optional[Type["EnvConfig"]]:
        return cls._registry.get(env)


def get_service_url(service: str, environment: Optional[str] = None) -> str:
    """
    Return the base URL for the given service in this environment. For example:

    >>> from globus_sdk.config import get_service_url
    >>> get_service_url("auth", environment="preview")
    'https://auth.preview.globus.org/'
    >>> get_service_url("search", environment="production")
    'https://search.api.globus.org/'

    If no ``environment`` is specified, this will use the ``GLOBUS_SDK_ENVIRONMENT``
    environment variable.
    """
    log.debug(f'Service URL Lookup for "{service}" under env "{environment}"')
    environment = environment or get_environment_name()
    # check for an environment variable of the form
    #   GLOBUS_SDK_SERVICE_URL_*
    # and use it ahead of any env config if set
    varname = _SERVICE_URL_VAR_FORMAT.format(service.upper())
    from_env = os.getenv(varname)
    if from_env:
        log.debug(f"Got URL from env var, {varname}={from_env}")
        return from_env
    conf = EnvConfig.get_by_name(environment)
    if not conf:
        raise ValueError(f'Unrecognized environment "{environment}"')
    url = conf.get_service_url(service)
    log.debug(f'Service URL Lookup Result: "{service}" is at "{url}"')
    return url


def get_webapp_url(environment: Optional[str] = None) -> str:
    """
    Return the URL to access the Globus web app in the given environment. For example:

    >>> get_webapp_url("preview")
    'https://app.preview.globus.org/'
    """
    environment = environment or get_environment_name()
    return get_service_url("app", environment=environment)


#
# public environments
#


class ProductionEnvConfig(EnvConfig):
    envname = "production"
    domain = "globus.org"
    nexus_url = "https://nexus.api.globusonline.org/"
    timer_url = "https://timer.automate.globus.org/"
    flows_url = "https://flows.automate.globus.org/"
    actions_url = "https://actions.automate.globus.org/"


class PreviewEnvConfig(EnvConfig):
    envname = "preview"
    domain = "preview.globus.org"


#
# environments for internal use only
#
for envname in ["sandbox", "integration", "test", "staging"]:
    # use `type()` rather than the `class` syntax to control classnames
    type(
        f"{envname.title()}EnvConfig",
        (EnvConfig,),
        {
            "envname": envname,
            "domain": f"{envname}.globuscs.info",
        },
    )
