"""Time-varying conditions that are not grids: tide predictions at reference stations."""
from __future__ import annotations

from pipeline import tides


def load_conditions(stations: list[dict], now, errors: list[str], fetch=tides.fetch_hilo) -> dict:
    out = []
    for st in stations:
        try:
            events = tides.parse_hilo(fetch(st["id"], now))
            if not events:
                raise RuntimeError("no predictions returned")
            out.append({"station": st, "events": events})
        except Exception as exc:        # one station down must not stop the run
            errors.append(f"tides {st['id']}: {exc}")
    return {"now": now, "tides": out}
