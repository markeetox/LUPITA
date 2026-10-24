# Fish forecast API for Seabound

A small, read-only set of static files. No server, no key, no account. Files are plain JSON and PNG.
Paths below are relative to the base URL.

**Base URL (testing):** `https://raw.githubusercontent.com/markeetox/lupita/data/api/v1/`
**Base URL (recommended for the app):** turn on GitHub Pages for the `data` branch (repo Settings -> Pages -> Branch: `data`, folder `/ (root)`),
then use `https://markeetox.github.io/lupita/api/v1/`. Pages is a proper CDN with CORS enabled; `raw.githubusercontent.com` is
fine while you build but is not meant for production traffic. Later you can copy the same files to Firebase Hosting or Cloud Storage: only
the base URL changes, because every link inside the files is relative.

Updated every hour. Each file has `generated_utc`; cache by that, show "updated 40 min ago", and keep the last copy for offline use.

## Files

| Path | What | Size |
|---|---|---|
| `index.json` | Start here: species list, status, image and heat links, moon / cold front / sea state, attribution | about 4 KB |
| `species/<id>.json` | One fish: description, today's areas with reasons and timing, heat info | a few KB |
| `heat/<id>.png` | Transparent heat overlay, ready to drop on a map (see `bounds`) | tens to a few hundred KB |
| `heat/<id>.json` | The raw score grid, if you would rather draw the heat yourself | about 21 KB |
| `img/<id>.png` | The fish picture (transparent PNG, 1260 x 600) | about 60 KB |
| `closures.json` | No-fishing areas (GeoJSON) | small |
| `stream.json` | Gulf Stream inshore edge line (GeoJSON, approximate) | tiny |

Fish ids: `mahi-mahi`, `sailfish`, `wahoo`, `yellowtail-snapper`, `mutton-snapper`, `cobia`, `snook`, `tarpon`.

## index.json

```json
{ "api_version": 1, "generated_utc": "2026-10-12T14:10:05+00:00", "experimental": true, "disclaimer": "...",
  "region": {"name": "south_florida", "bounds": [west, south, east, north]},
  "conditions": {"moon": {...}, "front": {...}, "sea": {"now": {"level": "fair", "text": "..."}, "outlook": {...}}},
  "species": [ {"id": "mahi-mahi", "name": "Mahi-mahi", "scientific_name": "...", "color": "#34d399",
                "image": {"url": "img/mahi-mahi.png", "kind": "illustration", "credit": "", "license": ""},
                "status": "ok", "message": "", "area_count": 5, "has_timing": false,
                "heat": {"png": "heat/mahi-mahi.png", "bounds": [west, south, east, north]},
                "details": "species/mahi-mahi.json"} ],
  "layers": {"closures": "closures.json", "gulf_stream_edge": "stream.json"},
  "attribution": ["NOAA ...", "..."] }
```

`status` is `ok` (areas to show), `no_favorable_areas` (conditions poor right now: show `message`) or `unavailable` (not enough data: show
`message`). `heat` is `null` for fish scored at named inlets (snook, tarpon): show their areas, not a heat layer.

## species/<id>.json

`about` holds `size`, `diet`, `behavior`, `depth`, `swimming_depth`, `spawning`, `lifespan`, `regulations_note`, `regulations_link`, `sources`
(only the ones that exist for that fish). `today.areas[]` each have `id`, `title`, `score` (0 to 1), `confidence` (`Low` or `Medium`),
`coords` ([lon, lat]), `zone` (GeoJSON Polygon or MultiPolygon), `reasons[]` (`{tag, text}`), `details[]` (`{label, value}`: depth, temperature,
tide, moon, current, no-fishing check and so on), `timing` and `sea`.

`timing` is `null` when we have no reliable time-of-day information for that fish. Otherwise: `start` (the first bar's time), `step_min` (60),
`scores` (24 values, 0 to 100, one per hour from `start`), `window` (`{start, end, score}` of the best stretch, or `null`), `why[]` and
`evidence` (always `angler_lore` for now: patterns from local captains, not studies). Times are UTC ISO strings; convert with `toLocal()`.

`sea` is `{level, text}` for the water near that area, or `null`. `level` is `good`, `fair`, `rough` or `dangerous`.

## Showing the heat layer

`heat/<id>.png` is already coloured and transparent. Put it on the map at `bounds` = `[west, south, east, north]`:
- `flutter_map`: `OverlayImageLayer` with an `OverlayImage` (see `seabound_client.dart`).
- `google_maps_flutter`: a `GroundOverlay` with the same bounds (load the PNG bytes first).
- Mapbox: an image source with the four corners.

## What is not in here, on purpose

- **Legal size, bag limits and seasons.** Florida's rules vary by species, area and season and change during the year, and I have not
  verified them, so the API does not state any. Each fish has a `regulations_link` to FWC and sometimes a `regulations_note`. Showing a
  wrong legal size is worse than showing none. If you want them in the app, the safe way is to pull them from FWC's official pages with an
  "as of" date and always keep the link to FWC.
- **Anything about users.** The files are the same for everyone and contain no personal data.

## Rules for a stable app

- The path contains the version (`/v1/`). Inside v1 fields are only ever added, so ignore fields you do not know. Anything that removes or
  changes a field would go to `/v2/`, and v1 would stay for a while.
- Show `disclaimer` and `attribution` somewhere reachable (an info screen is fine). Fish pictures are original illustrations today. If you
  replace them with photos, keep each photo's `credit` visible.
- Do not poll more often than every 15 to 30 minutes; the data changes hourly.
