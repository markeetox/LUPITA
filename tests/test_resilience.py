import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest
import requests

from pipeline import http, layers as L, run

ROOT = Path(__file__).resolve().parent.parent


class Resp:
    def __init__(self, status, text="ok"):
        self.status_code, self.text = status, text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Client Error")


def scripted(*outcomes):
    """A fake requests.get that plays back responses or exceptions in order."""
    calls = []

    def getter(url, params=None, headers=None, timeout=None):
        calls.append(headers)
        o = outcomes[min(len(calls) - 1, len(outcomes) - 1)]
        if isinstance(o, Exception):
            raise o
        return Resp(o)
    getter.calls = calls
    return getter


def test_a_refused_request_is_retried_with_growing_waits_and_then_succeeds():
    waits, g = [], scripted(403, 403, 200)
    r = http.get("https://x", sleep=waits.append, getter=g)
    assert r.status_code == 200 and len(g.calls) == 3
    assert 20 <= waits[0] <= 25 and 40 <= waits[1] <= 45                       # 20 s then 40 s, plus a little jitter
    assert "fish-habitat-map" in g.calls[0]["User-Agent"]                      # identifies itself to the server


def test_network_errors_are_retried_and_missing_pages_are_not():
    waits = []
    assert http.get("https://x", sleep=waits.append, getter=scripted(requests.ConnectionError("boom"), 200)).status_code == 200
    g = scripted(404, 200)
    with pytest.raises(requests.HTTPError):
        http.get("https://x", sleep=waits.append, getter=g)
    assert len(g.calls) == 1                                                    # a 404 will not get better by asking again


def test_it_gives_up_after_the_last_attempt_with_the_real_error():
    g = scripted(403)
    with pytest.raises(requests.HTTPError, match="403"):
        http.get("https://x", attempts=3, sleep=lambda s: None, getter=g)
    assert len(g.calls) == 3


def test_second_noaa_server_is_tried_when_the_first_refuses():
    cfg = {"base": "https://main.example/erddap", "fallback_bases": ["https://backup.example/erddap"], "dataset": "d",
           "variable": "analysed_sst", "dims": ["time", "latitude", "longitude"]}
    seen = []

    def fetch(url):
        seen.append(url)
        if "main.example" in url:
            raise requests.HTTPError("403 Client Error")
        return "time,latitude,longitude,analysed_sst\nUTC,degrees_north,degrees_east,degree_C\n2026-10-12T09:00:00Z,25.0,-80.0,28.5\n"
    lats, lons, grid, when, unit = L._fetch_grid(cfg, {"lat": [24.5, 27.0], "lon": [-81.0, -78.5]}, fetch)
    assert grid[0, 0] == 28.5 and "main.example" in seen[0] and "backup.example" in seen[1]
    with pytest.raises(requests.HTTPError):                                    # both refuse: the last error comes through
        L._fetch_grid(cfg, {"lat": [24.5, 27.0], "lon": [-81.0, -78.5]}, lambda u: (_ for _ in ()).throw(requests.HTTPError("403")))


def test_a_failed_run_leaves_the_last_good_predictions_alone(tmp_path, monkeypatch):
    for d in ("config", "data"):
        shutil.copytree(ROOT / d, tmp_path / d, ignore=shutil.ignore_patterns("live"))
    (tmp_path / "data/live").mkdir(parents=True, exist_ok=True)
    good = {"sentinel": "last good fish.json"}
    (tmp_path / "data/live/fish.json").write_text(json.dumps(good))
    (tmp_path / "data/live/closures.json").write_text(json.dumps({"sentinel": "closures"}))
    monkeypatch.setattr(run, "ROOT", tmp_path)
    monkeypatch.setattr(run, "pull_buoys", lambda *a, **k: [])
    monkeypatch.setattr(run, "load_layers", lambda *a, **k: None)             # NOAA refused everything
    monkeypatch.setattr(run, "load_conditions", lambda *a, **k: {"now": datetime.now(timezone.utc), "tides": []})
    run.main()
    assert json.loads((tmp_path / "data/live/fish.json").read_text()) == good           # untouched
    assert json.loads((tmp_path / "data/live/closures.json").read_text()) == {"sentinel": "closures"}
    latest = json.loads((tmp_path / "data/live/latest.json").read_text())
    assert latest["fish_updated"] is False and any("kept the last published predictions" in e for e in latest["errors"])
