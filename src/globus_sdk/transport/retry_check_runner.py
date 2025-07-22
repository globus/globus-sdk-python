from __future__ import annotations

import logging
import typing as t

from .retry import RetryCheck, RetryCheckFlags, RetryCheckResult, RetryContext

log = logging.getLogger(__name__)


class RetryCheckRunner:
    """
    A RetryCheckRunner is an object responsible for running retry checks over the
    lifetime of a request. Unlike the checks or the retry context, the runner persists
    between retries. It can therefore implement special logic for checks like "only try
    this check once".

    Its primary responsibility is to answer the question "should_retry(context)?" with a
    boolean.

    It takes as its input a list of checks. Checks may be paired with flags to indicate
    their configuration options. When not paired with flags, the flags are taken to be
    "NONE".

    Supported flags:

    ``RUN_ONCE``
      The check will run at most once for a given request. Once it has run, it is
      recorded as "has_run" and will not be run again on that request.
    """

    # check configs: a list of pairs, (check, flags)
    # a check without flags is assumed to have flags=NONE
    def __init__(self, checks: t.Iterable[RetryCheck]) -> None:
        self._checks: list[RetryCheck] = []
        self._check_data: dict[RetryCheck, dict[str, t.Any]] = {}
        for check in checks:
            self._checks.append(check)
            self._check_data[check] = {}

    def should_retry(self, context: RetryContext) -> bool:
        for check in self._checks:
            flags = getattr(check, "_retry_check_flags", RetryCheckFlags.NONE)

            if flags & RetryCheckFlags.RUN_ONCE:
                if self._check_data[check].get("has_run"):
                    continue
                else:
                    self._check_data[check]["has_run"] = True

            result = check(context)
            log.debug(  # try to get name but don't fail if it's not a function...
                "ran retry check (%s) => %s", getattr(check, "__name__", check), result
            )
            if result is RetryCheckResult.no_decision:
                continue
            elif result is RetryCheckResult.do_not_retry:
                return False
            else:
                return True

        # fallthrough: don't retry any request which isn't marked for retry
        return False
