"""HTTP GET with retries, for servers that sometimes refuse or time out (NOAA ERDDAP, ArcGIS, CO-OPS)."""
from __future__ import annotations

import random
import time

import requests

# 403 is included: ERDDAP servers answer 403 when they rate-limit or briefly block a busy address.
RETRY_STATUS = {403, 408, 425, 429, 500, 502, 503, 504}
USER_AGENT = "fish-habitat-map/0.2 (+https://github.com/markeetox/here-fishy-fishy)"


def get(url, params=None, headers=None, timeout=120, attempts=4, base_delay=20.0, sleep=time.sleep, getter=requests.get):
    """GET url, retrying refusals and network errors with growing waits (base_delay, then x2, x4, ...).
    Returns the response, or raises the last error once the attempts run out."""
    headers = {"User-Agent": USER_AGENT, **(headers or {})}
    last_exc = None
    for k in range(attempts):
        try:
            r = getter(url, params=params, headers=headers, timeout=timeout)
        except (requests.ConnectionError, requests.Timeout) as exc:
            last_exc = exc
        else:
            if r.status_code not in RETRY_STATUS or k == attempts - 1:
                r.raise_for_status()
                return r
        if k < attempts - 1:
            sleep(base_delay * 2 ** k + random.uniform(0, 5))
    raise last_exc
