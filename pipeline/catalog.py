"""Standalone species catalog generator.
Reads all profiles in data/species/*.json and produces a catalog dataset independent of ocean data ingestion."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path


SPEC_ROWS = [("size", "Typical size"), ("diet", "Diet"), ("swimming_depth", "Swimming depth"),
             ("depth", "Adult depth"), ("behavior", "Behavior"), ("spawning", "Spawning"),
             ("lifespan", "Lifespan")]


def _specs(profile: dict) -> list[list[str]]:
    p = profile.get("profile", {})
    return [[label, p[key]] for key, label in SPEC_ROWS if p.get(key)]


def species_image(profile: dict) -> dict:
    img = profile.get("image") or {}
    if img.get("url"):
        return {"url": img["url"], "kind": img.get("kind", "photo"), "credit": img.get("credit") or "", "license": img.get("license") or ""}
    return {"url": f"fish/{profile['id']}.png", "kind": "illustration", "credit": "Original illustration", "license": ""}


def build_catalog(species_dir: Path | str, generated_utc: str | None = None) -> dict:
    """Read all species JSON files from species_dir and return catalog dict."""
    species_path = Path(species_dir)
    if not species_path.exists():
        return {"version": 1, "generated_utc": generated_utc or datetime.now(timezone.utc).isoformat(), "total": 0, "species": []}

    profiles = []
    for p in sorted(species_path.glob("*.json")):
        try:
            profiles.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            continue

    catalog_species = []
    for profile in profiles:
        sid = profile.get("id")
        name = profile.get("common_name")
        if not sid or not name:
            continue
        entry = {
            "id": sid,
            "name": name,
            "sci": profile.get("scientific_name", ""),
            "color": profile.get("display", {}).get("color", "#ffffff"),
            "environment": profile.get("environment", "saltwater"),
            "model": profile.get("model", "grid"),
            "lat_range": profile.get("lat_range"),
            "lon_range": profile.get("lon_range"),
            "regulations": profile.get("regulations"),
            "specs": _specs(profile),
            "image": species_image(profile)
        }
        catalog_species.append(entry)

    catalog_species.sort(key=lambda s: s["name"].lower())

    now = generated_utc or datetime.now(timezone.utc).isoformat()
    return {
        "version": 1,
        "generated_utc": now,
        "total": len(catalog_species),
        "species": catalog_species
    }


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    live = root / "data/live"
    live.mkdir(parents=True, exist_ok=True)
    cat_data = build_catalog(root / "data/species")
    dest = live / "species_catalog.json"
    dest.write_text(json.dumps(cat_data, indent=2, allow_nan=False), encoding="utf-8")
    print(f"Wrote {dest} ({cat_data['total']} species)")


if __name__ == "__main__":
    main()
