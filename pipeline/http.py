"""HTTP GET with bounded retries and useful diagnostics for upstream failures."""
from __future__ import annotations

import random
import time

import requests

# Do not retry 403: ERDDAP uses it for access denials and IP blacklisting.
# Retrying a forbidden request can make an upstream block worse.
RETRY_STATUS = {408, 425, 429, 500, 502, 503, 504}
USER_AGENT = "fish-habitat-map/0.2 (+https://github.com/markeetox/lupita)"
DIAGNOSTIC_HEADERS = ("date", "server", "content-type", "retry-after", "x-ratelimit-remaining")


def _response_error(response, url: str, attempt: int, attempts: int) -> requests.HTTPError:
    """Build a bounded, actionable HTTP error without dumping an entire response."""
    status = response.status_code
    details = [f"HTTP {status} for {url} (attempt {attempt}/{attempts})"]
    response_headers = getattr(response, "headers", {}) or {}
    # requests uses a case-insensitive mapping, but normalize explicitly so
    # diagnostics also behave consistently with test doubles and other adapters.
    normalized_headers = {str(name).lower(): value for name, value in response_headers.items()}
    selected = {
        name: normalized_headers[name]
        for name in DIAGNOSTIC_HEADERS
        if name in normalized_headers
    }
    if selected:
        details.append(f"headers={selected!r}")
    body = " ".join(str(getattr(response, "text", "")).split())
    if body:
        details.append(f"body={body[:600]!r}")
    return requests.HTTPError("; ".join(details), response=response)


def get(url, params=None, headers=None, timeout=120, attempts=4, base_delay=20.0, sleep=time.sleep, getter=requests.get):
    """GET with exponential backoff for transient failures, never retrying HTTP 403.

    Retry delays grow as base_delay, 2*base_delay, 4*base_delay, etc.
    Permanent HTTP errors include the attempt number and bounded response diagnostics.
    """
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    request_headers = {"User-Agent": USER_AGENT, **(headers or {})}
    last_exc = None

    for index in range(attempts):
        attempt = index + 1
        try:
            response = getter(url, params=params, headers=request_headers, timeout=timeout)
        except (requests.ConnectionError, requests.Timeout) as exc:
            last_exc = exc
            if attempt == attempts:
                exc.args = (f"Request to {url} failed after {attempt}/{attempts} attempts: {exc}",)
                raise
        else:
            status = response.status_code
            if status == 403:
                raise _response_error(response, url, attempt, attempts)
            if status not in RETRY_STATUS:
                if status >= 400:
                    raise _response_error(response, url, attempt, attempts)
                return response
            if attempt == attempts:
                raise _response_error(response, url, attempt, attempts)

        if attempt < attempts:
            sleep(base_delay * 2 ** index + random.uniform(0, 5))

    # The loop either returns or raises; this is a defensive guard.
    raise last_exc
